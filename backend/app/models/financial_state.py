from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date


class Transaction(BaseModel):
    date: str
    description: str
    debit: Optional[float] = 0
    credit: Optional[float] = 0
    balance: Optional[float] = None
    category: Optional[str] = None
    type: Optional[str] = None


class Payable(BaseModel):
    payable_id: str
    vendor: str
    amount: float
    due_date: str
    days_until_due: int = 0
    penalty: str = "none"  # none, low, medium, high, very_high
    type: str = "flexible"  # critical, flexible, non_essential
    flexibility: str = "medium"  # none, low, medium, high, very_high
    linked_orders: List[str] = []
    priority_score: float = 0.5
    status: Optional[str] = "unpaid"
    description: Optional[str] = None
    penalty_amount: Optional[float] = 0


class Receivable(BaseModel):
    invoice_id: str
    client: str
    amount: float
    expected_date: str
    collection_probability: float = 0.8
    status: str = "upcoming"  # upcoming, due_soon, overdue
    days_overdue: int = 0
    action_required: Optional[str] = None


class Overhead(BaseModel):
    type: str
    amount: float
    essential: bool = True
    can_reduce: bool = False
    reducible_by: Optional[float] = 0.0


class InventoryItem(BaseModel):
    item_id: Optional[str] = None
    item: str
    unit: Optional[str] = None
    available_quantity: float
    required_quantity: float
    shortage: float = 0
    excess: float = 0
    unit_cost: Optional[float] = None
    total_value: Optional[float] = None


class ProcurementOrder(BaseModel):
    order_id: str
    vendor: str
    material: str
    quantity: float
    unit_cost: float
    total_cost: float
    order_date: str
    delivery_date: Optional[str] = None
    lead_time: int = 3
    status: str = "pending"
    payment_status: Optional[str] = "unpaid"
    payment_due: Optional[str] = None


class VendorInsight(BaseModel):
    vendor: str
    vendor_id: Optional[str] = None
    total_orders: int = 0
    avg_lead_time: float = 3
    payment_delay_avg: float = 0
    reliability_score: float = 0.8
    cost_efficiency_score: float = 0.8
    negotiation_flexibility: str = "medium"
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    allows_credit: Optional[bool] = False
    credit_limit: Optional[float] = 0


class LedgerSummary(BaseModel):
    monthly_income: float
    monthly_expense: float
    avg_payment_cycle_days: float = 7
    avg_collection_days: Optional[float] = 9.8


class Production(BaseModel):
    daily_output: Dict[str, Any] = {}
    cost_per_unit: float = 95
    selling_price_per_unit: float = 185
    units_this_month: Optional[int] = 0
    monthly_target: Optional[int] = 2200


class FinancialState(BaseModel):
    business_name: Optional[str] = "Sri Lakshmi Garments"
    cash_balance: float
    transactions: List[Transaction] = []
    payables: List[Payable] = []
    receivables: List[Receivable] = []
    overheads: List[Overhead] = []
    ledger_summary: Optional[LedgerSummary] = None
    inventory_procurement: List[ProcurementOrder] = []
    inventory_status: List[InventoryItem] = []
    vendor_insights: List[VendorInsight] = []
    production: Optional[Production] = None
    cost_breakdown: Optional[Dict[str, float]] = None
