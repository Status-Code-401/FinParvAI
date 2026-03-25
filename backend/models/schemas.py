from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date


# ─── Ingest Models ────────────────────────────────────────────────────────────

class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    type: str  # credit / debit
    balance: Optional[float] = None

class Payable(BaseModel):
    vendor: str
    amount: float
    due_date: str
    penalty: str = "medium"  # low / medium / high
    type: str = "flexible"   # critical / flexible
    linked_orders: Optional[List[str]] = []
    priority_score: Optional[float] = 0.5

class Receivable(BaseModel):
    client: str
    amount: float
    expected_date: str
    collection_probability: float = 0.8

class Overhead(BaseModel):
    type: str
    amount: float
    essential: bool

class VendorInsight(BaseModel):
    vendor: str
    total_orders: int
    avg_lead_time: float
    payment_delay_avg: float
    reliability_score: float
    cost_efficiency_score: float

class InventoryItem(BaseModel):
    item: str
    available_quantity: float
    required_quantity: float
    shortage: float
    excess: float

class ProcurementOrder(BaseModel):
    order_id: str
    vendor: str
    material: str
    quantity: float
    unit_cost: float
    total_cost: float
    order_date: str
    delivery_date: str
    lead_time: int
    status: str

class ProductionData(BaseModel):
    daily_output: Dict[str, float]
    cost_per_unit: float

class LedgerSummary(BaseModel):
    monthly_income: float
    monthly_expense: float
    avg_payment_cycle_days: float

class FinancialState(BaseModel):
    cash_balance: float
    transactions: Optional[List[Transaction]] = []
    payables: Optional[List[Payable]] = []
    receivables: Optional[List[Receivable]] = []
    overheads: Optional[List[Overhead]] = []
    ledger_summary: Optional[LedgerSummary] = None
    inventory_procurement: Optional[List[ProcurementOrder]] = []
    inventory_status: Optional[List[InventoryItem]] = []
    vendor_insights: Optional[List[VendorInsight]] = []
    production: Optional[ProductionData] = None
    cost_breakdown: Optional[Dict[str, float]] = {}


# ─── Decision Engine Models ───────────────────────────────────────────────────

class DailyCashFlow(BaseModel):
    day: int
    date: str
    opening_cash: float
    inflows: float
    outflows: float
    closing_cash: float
    events: List[str]

class ScoredPayable(BaseModel):
    vendor: str
    amount: float
    due_date: str
    score: float
    action: str  # pay_now / partial / delay
    reason: str
    partial_amount: Optional[float] = None

class RecoveryStrategy(BaseModel):
    type: str
    description: str
    estimated_impact: float

class DecisionOutput(BaseModel):
    runway_days: Optional[int]
    is_safe: bool
    risk_level: str  # low / medium / high / critical
    cash_flow_projection: List[DailyCashFlow]
    scored_payables: List[ScoredPayable]
    pay_now: List[str]
    delay: List[str]
    partial: List[str]
    recovery_strategies: List[RecoveryStrategy]
    overhead_actions: List[str]
    inventory_actions: List[str]
    explanation: str
    confidence_score: float


# ─── Predictive Engine Models ─────────────────────────────────────────────────

class ForecastPoint(BaseModel):
    date: str
    value: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class Prediction(BaseModel):
    revenue_forecast: List[ForecastPoint]
    cash_flow_forecast: List[ForecastPoint]
    demand_multiplier: float
    festival_impact: Optional[str] = None
    recommendations: List[str]
    shap_explanations: Dict[str, float]


# ─── Action Models ────────────────────────────────────────────────────────────

class EmailDraft(BaseModel):
    recipient_type: str  # client / vendor
    recipient_name: str
    subject: str
    body: str
    tone: str  # formal / semi-formal / urgent

class PaymentSchedule(BaseModel):
    date: str
    vendor: str
    amount: float
    priority: str
    notes: str

class ActionPlan(BaseModel):
    payment_schedule: List[PaymentSchedule]
    email_drafts: List[EmailDraft]
    summary: str
