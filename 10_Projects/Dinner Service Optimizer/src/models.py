"""
Data contracts and schemas for the Dinner Service Optimizer.
Defines models for tables, parties, orders, kitchen stations, and simulation telemetry.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class TableStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    DIRTY = "DIRTY"
    HELD = "HELD"


class CourseType(str, Enum):
    BEVERAGE = "BEVERAGE"
    APPETIZER = "APPETIZER"
    ENTREE = "ENTREE"
    DESSERT = "DESSERT"


class ItemStatus(str, Enum):
    QUEUED = "QUEUED"
    COOKING = "COOKING"
    READY = "READY"
    SERVED = "SERVED"


class StationType(str, Enum):
    GRILL = "GRILL"
    SAUTE = "SAUTE"
    COLD_LARDER = "COLD_LARDER"
    PASTRY = "PASTRY"
    BAR = "BAR"


class Table(BaseModel):
    id: str
    table_number: int
    capacity: int
    min_capacity: int = 1
    status: TableStatus = TableStatus.AVAILABLE
    section: str = "Main Dining"
    current_party_id: Optional[str] = None
    current_party_size: Optional[int] = None
    seated_at_minute: Optional[int] = None
    estimated_vacate_minute: Optional[int] = None


class Party(BaseModel):
    id: str
    name: str
    size: int
    is_reservation: bool = False
    reservation_minute: Optional[int] = None
    arrived_at_minute: int = 0
    max_wait_minutes: int = 45
    vip: bool = False
    special_requests: List[str] = Field(default_factory=list)


class OrderItem(BaseModel):
    id: str
    name: str
    course: CourseType
    station: StationType
    prep_time_minutes: int
    status: ItemStatus = ItemStatus.QUEUED
    fired_at_minute: Optional[int] = None
    completed_at_minute: Optional[int] = None


class Order(BaseModel):
    id: str
    table_id: str
    party_id: str
    items: List[OrderItem] = Field(default_factory=list)
    created_at_minute: int = 0
    current_course: CourseType = CourseType.APPETIZER
    is_completed: bool = False


class KitchenStation(BaseModel):
    id: str
    name: str
    station_type: StationType
    capacity: int = 4  # Maximum concurrent dishes
    active_item_ids: List[str] = Field(default_factory=list)
    queued_item_ids: List[str] = Field(default_factory=list)


class WaitTimeEstimate(BaseModel):
    party_id: str
    party_name: str
    party_size: int
    estimated_wait_minutes: int
    confidence_score: float
    recommended_table_id: Optional[str] = None
    reasoning: str


class TableAssignmentRequest(BaseModel):
    party_id: str


class TableAssignmentResult(BaseModel):
    success: bool
    table_id: Optional[str] = None
    table_number: Optional[int] = None
    party_id: str
    score: float = 0.0
    message: str


class DispatchDecision(BaseModel):
    minute: int
    fired_item_ids: List[str] = Field(default_factory=list)
    station_utilization: Dict[str, float] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


class SimulationStepRequest(BaseModel):
    step_minutes: int = 1


class SimulationStepResult(BaseModel):
    current_minute: int
    tables_occupied: int
    tables_available: int
    waiting_parties_count: int
    active_orders_count: int
    dishes_fired: List[str]
    dishes_completed: List[str]
    tables_vacated: List[int]


class ServiceState(BaseModel):
    current_minute: int = 0
    tables: List[Table] = Field(default_factory=list)
    parties_waiting: List[Party] = Field(default_factory=list)
    active_orders: List[Order] = Field(default_factory=list)
    stations: Dict[str, KitchenStation] = Field(default_factory=dict)
    total_covers_served: int = 0
    completed_orders_count: int = 0
