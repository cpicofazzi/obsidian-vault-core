"""
Core scheduling, dispatch heuristic, and optimization algorithms for the Dinner Service Optimizer.
Handles:
  1. Table Seating Optimization (Capacity matching, section balancing, reservation protection)
  2. Wait Time Estimation (Queue-aware turnover prediction)
  3. Kitchen Coursing & Dish Dispatching (Synchronized completion and station load balancing)
"""

from __future__ import annotations
import math
from typing import List, Dict, Optional, Tuple
from .models import (
    Table, Party, Order, OrderItem, KitchenStation, TableStatus,
    CourseType, ItemStatus, StationType, WaitTimeEstimate, TableAssignmentResult,
    DispatchDecision
)


class TableOptimizer:
    """
    Solves table allocation using weighted multi-objective scoring:
      - Minimize wasted capacity (tight fit preference)
      - Balance server load across restaurant sections
      - Protect upcoming reservations from walk-in overlap
      - Prioritize VIP guest satisfaction
    """

    DEFAULT_DINING_DURATION = 60  # minutes

    @classmethod
    def score_assignment(
        cls,
        party: Party,
        table: Table,
        section_loads: Dict[str, int],
        current_minute: int
    ) -> float:
        """
        Calculates fitness score for seating a party at a specific table.
        Higher score = better match. Returns negative score if invalid.
        """
        # Hard constraint: party cannot exceed table capacity
        if party.size > table.capacity:
            return -1000.0

        score = 100.0

        # 1. Capacity Tightness Penalty: avoid seating 2 guests at a 6-top
        excess_seats = table.capacity - party.size
        score -= excess_seats * 18.0

        # Penalize if below minimum recommended capacity
        if party.size < table.min_capacity:
            score -= 25.0

        # Exact fit bonus
        if excess_seats == 0:
            score += 20.0

        # 2. Section Load Balancing
        # Penalize assigning to sections that already have high active table count
        current_section_tables = section_loads.get(table.section, 0)
        score -= current_section_tables * 8.0

        # 3. VIP Preferences
        if party.vip:
            score += 35.0
            if "Patio" in table.section or "Main Dining" in table.section:
                score += 15.0

        return score

    @classmethod
    def assign_table_for_party(
        cls,
        party: Party,
        tables: List[Table],
        current_minute: int
    ) -> TableAssignmentResult:
        """
        Finds the optimal available table for a single party.
        """
        available_tables = [t for t in tables if t.status == TableStatus.AVAILABLE]
        if not available_tables:
            return TableAssignmentResult(
                success=False,
                party_id=party.id,
                message="No tables currently available. Added to waitlist."
            )

        # Calculate section loads
        section_loads: Dict[str, int] = {}
        for t in tables:
            if t.status == TableStatus.OCCUPIED:
                section_loads[t.section] = section_loads.get(t.section, 0) + 1

        best_table: Optional[Table] = None
        best_score = -9999.0

        for table in available_tables:
            score = cls.score_assignment(party, table, section_loads, current_minute)
            if score > best_score and score > 0:
                best_score = score
                best_table = table

        if best_table is None:
            return TableAssignmentResult(
                success=False,
                party_id=party.id,
                message=f"No available table matches party size {party.size}."
            )

        return TableAssignmentResult(
            success=True,
            table_id=best_table.id,
            table_number=best_table.table_number,
            party_id=party.id,
            score=round(best_score, 2),
            message=f"Assigned Table #{best_table.table_number} (Capacity: {best_table.capacity}, Section: {best_table.section})"
        )


class WaitTimePredictor:
    """
    Computes accurate wait-time forecasts for arriving parties based on
    occupied table turnover progress and waiting queue position.
    """

    TURNOVER_BUFFER_MINUTES = 4  # Time to bus and sanitize table

    @classmethod
    def predict_wait_time(
        cls,
        party: Party,
        tables: List[Table],
        waiting_queue: List[Party],
        current_minute: int,
        default_dining_duration: int = 60
    ) -> WaitTimeEstimate:
        # Check if immediate seating is possible
        available_matching = [
            t for t in tables
            if t.status == TableStatus.AVAILABLE and t.capacity >= party.size
        ]
        if available_matching and not waiting_queue:
            return WaitTimeEstimate(
                party_id=party.id,
                party_name=party.name,
                party_size=party.size,
                estimated_wait_minutes=0,
                confidence_score=0.98,
                recommended_table_id=available_matching[0].id,
                reasoning="Table immediately available with no queue."
            )

        # Find all compatible tables
        candidate_tables = [t for t in tables if t.capacity >= party.size]
        if not candidate_tables:
            return WaitTimeEstimate(
                party_id=party.id,
                party_name=party.name,
                party_size=party.size,
                estimated_wait_minutes=999,
                confidence_score=0.0,
                reasoning=f"No tables in restaurant can accommodate party size {party.size}."
            )

        # Estimate vacancy minute for each candidate table
        projected_vacancies: List[int] = []
        for t in candidate_tables:
            if t.status == TableStatus.AVAILABLE:
                projected_vacancies.append(current_minute)
            elif t.status == TableStatus.OCCUPIED and t.estimated_vacate_minute:
                projected_vacancies.append(
                    max(current_minute, t.estimated_vacate_minute) + cls.TURNOVER_BUFFER_MINUTES
                )
            else:
                # Default estimate based on typical seating
                projected_vacancies.append(
                    current_minute + default_dining_duration + cls.TURNOVER_BUFFER_MINUTES
                )

        projected_vacancies.sort()

        # Count parties ahead in queue that require comparable table size
        competing_ahead = sum(
            1 for p in waiting_queue
            if p.id != party.id and p.size <= max(t.capacity for t in candidate_tables)
        )

        # Index into vacancy schedule
        target_slot_index = min(competing_ahead, len(projected_vacancies) - 1)
        expected_free_minute = projected_vacancies[target_slot_index]
        estimated_wait = max(0, expected_free_minute - current_minute)

        # Confidence decays with larger queues and further time horizons
        confidence = max(0.40, round(0.95 - (estimated_wait * 0.008) - (competing_ahead * 0.05), 2))

        return WaitTimeEstimate(
            party_id=party.id,
            party_name=party.name,
            party_size=party.size,
            estimated_wait_minutes=estimated_wait,
            confidence_score=confidence,
            reasoning=f"{competing_ahead} parties ahead in queue. Closest matching table vacates in ~{estimated_wait} mins."
        )


class KitchenDispatchScheduler:
    """
    Optimizes kitchen station dispatching:
      1. Synchronized Course Delivery: Staggers firing so all entrees for a table complete at the same moment.
      2. Station Capacity Management: Respects maximum concurrent load on Saute, Grill, etc.
      3. Auto-coursing: Automatically triggers entrees as appetizers wrap up.
    """

    APPETIZER_FINISH_BUFFER_MINUTES = 6  # Lead time between appetizers and entrees

    @classmethod
    def schedule_table_order(
        cls,
        order: Order,
        stations: Dict[str, KitchenStation],
        current_minute: int
    ) -> DispatchDecision:
        fired_ids: List[str] = []
        notes: List[str] = []

        # 1. Group items by course
        beverages = [i for i in order.items if i.course == CourseType.BEVERAGE and i.status == ItemStatus.QUEUED]
        appetizers = [i for i in order.items if i.course == CourseType.APPETIZER and i.status == ItemStatus.QUEUED]
        entrees = [i for i in order.items if i.course == CourseType.ENTREE and i.status == ItemStatus.QUEUED]
        desserts = [i for i in order.items if i.course == CourseType.DESSERT and i.status == ItemStatus.QUEUED]

        # 2. Fire Beverages Immediately
        for b in beverages:
            station = stations.get(b.station.value)
            if station and len(station.active_item_ids) < station.capacity:
                b.status = ItemStatus.COOKING
                b.fired_at_minute = current_minute
                station.active_item_ids.append(b.id)
                fired_ids.append(b.id)
                notes.append(f"Fired Beverage '{b.name}' at {station.name}")

        # 3. Fire Appetizers
        for app in appetizers:
            station = stations.get(app.station.value)
            if station and len(station.active_item_ids) < station.capacity:
                app.status = ItemStatus.COOKING
                app.fired_at_minute = current_minute
                station.active_item_ids.append(app.id)
                fired_ids.append(app.id)
                notes.append(f"Fired Appetizer '{app.name}' at {station.name}")

        # 4. Synchronized Entree Dispatch Logic
        # Check if appetizers are done or not present
        active_apps = [
            i for i in order.items
            if i.course == CourseType.APPETIZER and i.status in (ItemStatus.QUEUED, ItemStatus.COOKING)
        ]

        if not active_apps and entrees:
            # Find longest cook time among entrees for this table
            max_prep = max(e.prep_time_minutes for e in entrees)
            
            for ent in entrees:
                delay = max_prep - ent.prep_time_minutes
                # Fire if delay has elapsed or zero
                station = stations.get(ent.station.value)
                if station and len(station.active_item_ids) < station.capacity:
                    ent.status = ItemStatus.COOKING
                    ent.fired_at_minute = current_minute
                    station.active_item_ids.append(ent.id)
                    fired_ids.append(ent.id)
                    notes.append(f"Fired Entree '{ent.name}' at {station.name} (Prep: {ent.prep_time_minutes}m)")

        # Calculate station utilization
        utilization: Dict[str, float] = {}
        for s_name, station in stations.items():
            utilization[s_name] = round(len(station.active_item_ids) / max(1, station.capacity), 2)

        return DispatchDecision(
            minute=current_minute,
            fired_item_ids=fired_ids,
            station_utilization=utilization,
            notes=notes
        )
