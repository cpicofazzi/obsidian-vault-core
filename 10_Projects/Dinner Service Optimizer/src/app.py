"""
FastAPI application for the Dinner Service Optimizer.
Provides RESTful endpoints for real-time table allocation, queue management,
synchronized kitchen dispatch, and service simulation.
"""

from __future__ import annotations
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    Table, Party, Order, OrderItem, KitchenStation, TableStatus,
    CourseType, ItemStatus, StationType, WaitTimeEstimate,
    TableAssignmentRequest, TableAssignmentResult, DispatchDecision,
    SimulationStepRequest, SimulationStepResult, ServiceState
)
from .optimizer import TableOptimizer, WaitTimePredictor, KitchenDispatchScheduler

app = FastAPI(
    title="Dinner Service Optimizer API",
    description="Intelligent Table Seating, Wait-Time Forecasting, and Synchronized Kitchen Dispatch Engine",
    version="1.0.0"
)

# Enable CORS for frontend clients (Next.js / React / Streamlit)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# In-Memory State & Default Seed Data
# -----------------------------------------------------------------------------

def create_default_state() -> ServiceState:
    """Initializes a standard 10-table restaurant with 4 kitchen stations."""
    tables = [
        Table(id="t1", table_number=1, capacity=2, min_capacity=1, section="Bar", status=TableStatus.AVAILABLE),
        Table(id="t2", table_number=2, capacity=2, min_capacity=1, section="Bar", status=TableStatus.AVAILABLE),
        Table(id="t3", table_number=3, capacity=4, min_capacity=2, section="Main Dining", status=TableStatus.AVAILABLE),
        Table(id="t4", table_number=4, capacity=4, min_capacity=2, section="Main Dining", status=TableStatus.AVAILABLE),
        Table(id="t5", table_number=5, capacity=4, min_capacity=3, section="Main Dining", status=TableStatus.AVAILABLE),
        Table(id="t6", table_number=6, capacity=6, min_capacity=4, section="Main Dining", status=TableStatus.AVAILABLE),
        Table(id="t7", table_number=7, capacity=2, min_capacity=1, section="Patio", status=TableStatus.AVAILABLE),
        Table(id="t8", table_number=8, capacity=4, min_capacity=2, section="Patio", status=TableStatus.AVAILABLE),
        Table(id="t9", table_number=9, capacity=6, min_capacity=4, section="Patio", status=TableStatus.AVAILABLE),
        Table(id="t10", table_number=10, capacity=8, min_capacity=5, section="Main Dining", status=TableStatus.AVAILABLE),
    ]

    stations = {
        StationType.GRILL.value: KitchenStation(id="s_grill", name="Grill Station", station_type=StationType.GRILL, capacity=4),
        StationType.SAUTE.value: KitchenStation(id="s_saute", name="Saute Station", station_type=StationType.SAUTE, capacity=5),
        StationType.COLD_LARDER.value: KitchenStation(id="s_cold", name="Cold Larder / Salad", station_type=StationType.COLD_LARDER, capacity=6),
        StationType.PASTRY.value: KitchenStation(id="s_pastry", name="Pastry & Dessert", station_type=StationType.PASTRY, capacity=4),
        StationType.BAR.value: KitchenStation(id="s_bar", name="Service Bar", station_type=StationType.BAR, capacity=8),
    }

    return ServiceState(
        current_minute=0,
        tables=tables,
        parties_waiting=[],
        active_orders=[],
        stations=stations,
        total_covers_served=0,
        completed_orders_count=0
    )


# Persistent live runtime state
STATE = create_default_state()


# -----------------------------------------------------------------------------
# Endpoints: System Health & State Management
# -----------------------------------------------------------------------------

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "Dinner Service Optimizer", "minute": STATE.current_minute}


@app.get("/state", response_model=ServiceState, tags=["System"])
def get_service_state():
    """Returns the full runtime snapshot of tables, queues, stations, and telemetry."""
    return STATE


@app.post("/reset", tags=["System"])
def reset_service():
    """Resets restaurant floor and kitchen to initial clean state."""
    global STATE
    STATE = create_default_state()
    return {"message": "Service state reset successfully.", "minute": STATE.current_minute}


# -----------------------------------------------------------------------------
# Endpoints: Table Management & Seating Optimization
# -----------------------------------------------------------------------------

@app.get("/tables", response_model=List[Table], tags=["Tables"])
def list_tables():
    """List all dining tables with current occupancy and remaining dining times."""
    return STATE.tables


@app.post("/tables/assign", response_model=TableAssignmentResult, tags=["Tables"])
def assign_table(req: TableAssignmentRequest):
    """
    Optimally allocates the best available table for a waiting party,
    minimizing seat wastage and balancing server workload.
    """
    party = next((p for p in STATE.parties_waiting if p.id == req.party_id), None)
    if not party:
        raise HTTPException(status_code=404, detail=f"Party '{req.party_id}' not found in waitlist.")

    result = TableOptimizer.assign_table_for_party(party, STATE.tables, STATE.current_minute)

    if result.success and result.table_id:
        # Commit seating update to table
        table = next(t for t in STATE.tables if t.id == result.table_id)
        table.status = TableStatus.OCCUPIED
        table.current_party_id = party.id
        table.current_party_size = party.size
        table.seated_at_minute = STATE.current_minute
        table.estimated_vacate_minute = STATE.current_minute + TableOptimizer.DEFAULT_DINING_DURATION

        # Remove from waitlist
        STATE.parties_waiting = [p for p in STATE.parties_waiting if p.id != party.id]

    return result


# -----------------------------------------------------------------------------
# Endpoints: Parties & Wait-Time Forecasting
# -----------------------------------------------------------------------------

@app.get("/waitlist", response_model=List[Party], tags=["Parties"])
def list_waitlist():
    """Returns all parties currently waiting for table seating."""
    return STATE.parties_waiting


@app.post("/waitlist/add", response_model=WaitTimeEstimate, tags=["Parties"])
def add_party_to_waitlist(party: Party):
    """
    Registers a new walk-in or arrival and calculates an instant,
    data-driven wait time estimate.
    """
    party.arrived_at_minute = STATE.current_minute
    STATE.parties_waiting.append(party)

    estimate = WaitTimePredictor.predict_wait_time(
        party=party,
        tables=STATE.tables,
        waiting_queue=STATE.parties_waiting,
        current_minute=STATE.current_minute
    )
    return estimate


@app.post("/parties/estimate-wait", response_model=WaitTimeEstimate, tags=["Parties"])
def estimate_wait(party: Party):
    """Calculates wait time prediction for a prospective party without adding them to the queue."""
    return WaitTimePredictor.predict_wait_time(
        party=party,
        tables=STATE.tables,
        waiting_queue=STATE.parties_waiting,
        current_minute=STATE.current_minute
    )


# -----------------------------------------------------------------------------
# Endpoints: Orders & Kitchen Dispatch
# -----------------------------------------------------------------------------

@app.post("/orders", response_model=Order, tags=["Orders"])
def place_order(order: Order):
    """Creates a new multi-course ticket for an occupied table."""
    order.created_at_minute = STATE.current_minute
    STATE.active_orders.append(order)

    # Immediately evaluate dispatch for beverages/appetizers
    KitchenDispatchScheduler.schedule_table_order(order, STATE.stations, STATE.current_minute)
    return order


@app.get("/kitchen/stations", response_model=Dict[str, KitchenStation], tags=["Kitchen"])
def get_kitchen_stations():
    """Returns live cooking load and capacity across all kitchen stations."""
    return STATE.stations


@app.post("/kitchen/dispatch", response_model=List[DispatchDecision], tags=["Kitchen"])
def dispatch_kitchen():
    """Runs the synchronized dispatch optimizer across all active table orders."""
    decisions: List[DispatchDecision] = []
    for order in STATE.active_orders:
        decision = KitchenDispatchScheduler.schedule_table_order(
            order=order,
            stations=STATE.stations,
            current_minute=STATE.current_minute
        )
        decisions.append(decision)
    return decisions


# -----------------------------------------------------------------------------
# Endpoints: Simulation Engine
# -----------------------------------------------------------------------------

@app.post("/simulation/step", response_model=SimulationStepResult, tags=["Simulation"])
def step_simulation(req: SimulationStepRequest):
    """
    Advances the restaurant service clock by `step_minutes`.
    Updates dish cooking timers, completes courses, frees finished tables,
    and automatically seats eligible waitlisted guests.
    """
    step = max(1, req.step_minutes)
    STATE.current_minute += step

    dishes_fired: List[str] = []
    dishes_completed: List[str] = []
    tables_vacated: List[int] = []

    # 1. Update Cooking Dishes in Kitchen
    for order in STATE.active_orders:
        for item in order.items:
            if item.status == ItemStatus.COOKING and item.fired_at_minute is not None:
                elapsed = STATE.current_minute - item.fired_at_minute
                if elapsed >= item.prep_time_minutes:
                    item.status = ItemStatus.READY
                    item.completed_at_minute = STATE.current_minute
                    dishes_completed.append(f"{item.name} (Table {order.table_id})")

                    # Release station capacity
                    station = STATE.stations.get(item.station.value)
                    if station and item.id in station.active_item_ids:
                        station.active_item_ids.remove(item.id)

    # 2. Re-run dispatch scheduler for coursing transitions
    for order in STATE.active_orders:
        decision = KitchenDispatchScheduler.schedule_table_order(order, STATE.stations, STATE.current_minute)
        dishes_fired.extend(decision.fired_item_ids)

    # 3. Process Table Vacancies & Turnover
    for table in STATE.tables:
        if table.status == TableStatus.OCCUPIED and table.estimated_vacate_minute is not None:
            if STATE.current_minute >= table.estimated_vacate_minute:
                # Table finishes meal
                table.status = TableStatus.AVAILABLE
                table.current_party_id = None
                tables_vacated.append(table.table_number)
                if table.current_party_size:
                    STATE.total_covers_served += table.current_party_size
                table.current_party_size = None
                table.seated_at_minute = None
                table.estimated_vacate_minute = None

    # 4. Auto-seat waiting parties if tables opened up
    for party in list(STATE.parties_waiting):
        alloc = TableOptimizer.assign_table_for_party(party, STATE.tables, STATE.current_minute)
        if alloc.success and alloc.table_id:
            tbl = next(t for t in STATE.tables if t.id == alloc.table_id)
            tbl.status = TableStatus.OCCUPIED
            tbl.current_party_id = party.id
            tbl.current_party_size = party.size
            tbl.seated_at_minute = STATE.current_minute
            tbl.estimated_vacate_minute = STATE.current_minute + TableOptimizer.DEFAULT_DINING_DURATION
            STATE.parties_waiting.remove(party)

    # Calculate statistics
    tables_occupied = sum(1 for t in STATE.tables if t.status == TableStatus.OCCUPIED)
    tables_available = sum(1 for t in STATE.tables if t.status == TableStatus.AVAILABLE)

    return SimulationStepResult(
        current_minute=STATE.current_minute,
        tables_occupied=tables_occupied,
        tables_available=tables_available,
        waiting_parties_count=len(STATE.parties_waiting),
        active_orders_count=len(STATE.active_orders),
        dishes_fired=dishes_fired,
        dishes_completed=dishes_completed,
        tables_vacated=tables_vacated
    )


@app.post("/simulation/seed-rush", tags=["Simulation"])
def seed_dinner_rush():
    """Seeds a realistic Friday evening dinner rush with multiple parties and orders."""
    reset_service()

    # Pre-seat some tables
    table_assignments = [
        ("t1", "p_bar1", "Alice", 2, 15),
        ("t3", "p_main1", "Bob Smith", 4, 30),
        ("t7", "p_patio1", "Clara VIP", 2, 40),
    ]

    for t_id, p_id, name, size, elapsed in table_assignments:
        tbl = next(t for t in STATE.tables if t.id == t_id)
        tbl.status = TableStatus.OCCUPIED
        tbl.current_party_id = p_id
        tbl.current_party_size = size
        tbl.seated_at_minute = 0
        tbl.estimated_vacate_minute = TableOptimizer.DEFAULT_DINING_DURATION - elapsed

    # Add waiting walk-ins
    STATE.parties_waiting = [
        Party(id="w1", name="David Party", size=4, arrived_at_minute=0, vip=False),
        Party(id="w2", name="Elena Duo", size=2, arrived_at_minute=0, vip=True),
        Party(id="w3", name="Franklin Family", size=6, arrived_at_minute=0, vip=False),
    ]

    # Create active tickets
    order1 = Order(
        id="ord_t3",
        table_id="t3",
        party_id="p_main1",
        items=[
            OrderItem(id="i1", name="Calamari Fritti", course=CourseType.APPETIZER, station=StationType.COLD_LARDER, prep_time_minutes=8),
            OrderItem(id="i2", name="Ribeye Steak 12oz", course=CourseType.ENTREE, station=StationType.GRILL, prep_time_minutes=18),
            OrderItem(id="i3", name="Wild Mushroom Risotto", course=CourseType.ENTREE, station=StationType.SAUTE, prep_time_minutes=12),
        ]
    )
    place_order(order1)

    return {
        "message": "Dinner rush scenario loaded successfully.",
        "tables_occupied": sum(1 for t in STATE.tables if t.status == TableStatus.OCCUPIED),
        "parties_waiting": len(STATE.parties_waiting),
        "active_orders": len(STATE.active_orders)
    }
