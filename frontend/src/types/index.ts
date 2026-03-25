export interface Transaction {
  date: string;
  description: string;
  amount: number;
  type: 'credit' | 'debit';
  balance?: number;
}

export interface Payable {
  vendor: string;
  amount: number;
  due_date: string;
  penalty: 'low' | 'medium' | 'high';
  type: 'critical' | 'flexible';
  linked_orders?: string[];
  priority_score?: number;
}

export interface Receivable {
  client: string;
  amount: number;
  expected_date: string;
  collection_probability: number;
}

export interface Overhead {
  type: string;
  amount: number;
  essential: boolean;
}

export interface InventoryItem {
  item: string;
  available_quantity: number;
  required_quantity: number;
  shortage: number;
  excess: number;
}

export interface VendorInsight {
  vendor: string;
  total_orders: number;
  avg_lead_time: number;
  payment_delay_avg: number;
  reliability_score: number;
  cost_efficiency_score: number;
}

export interface LedgerSummary {
  monthly_income: number;
  monthly_expense: number;
  avg_payment_cycle_days: number;
}

export interface ProcurementOrder {
  order_id: string;
  vendor: string;
  material: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  order_date: string;
  delivery_date: string;
  lead_time: number;
  status: string;
}

export interface FinancialState {
  cash_balance: number;
  transactions?: Transaction[];
  payables?: Payable[];
  receivables?: Receivable[];
  overheads?: Overhead[];
  ledger_summary?: LedgerSummary;
  inventory_procurement?: ProcurementOrder[];
  inventory_status?: InventoryItem[];
  vendor_insights?: VendorInsight[];
  production?: { daily_output: Record<string, number>; cost_per_unit: number };
  cost_breakdown?: Record<string, number>;
}

export interface DailyCashFlow {
  day: number;
  date: string;
  opening_cash: number;
  inflows: number;
  outflows: number;
  closing_cash: number;
  events: string[];
}

export interface ScoredPayable {
  vendor: string;
  amount: number;
  due_date: string;
  score: number;
  action: 'pay_now' | 'partial' | 'delay';
  reason: string;
  partial_amount?: number;
}

export interface RecoveryStrategy {
  type: string;
  description: string;
  estimated_impact: number;
}

export interface DecisionOutput {
  runway_days: number;
  is_safe: boolean;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  cash_flow_projection: DailyCashFlow[];
  scored_payables: ScoredPayable[];
  pay_now: string[];
  delay: string[];
  partial: string[];
  recovery_strategies: RecoveryStrategy[];
  overhead_actions: string[];
  inventory_actions: string[];
  explanation: string;
  confidence_score: number;
}

export interface ForecastPoint {
  date: string;
  value: number;
  lower_bound?: number;
  upper_bound?: number;
}

export interface Prediction {
  revenue_forecast: ForecastPoint[];
  cash_flow_forecast: ForecastPoint[];
  demand_multiplier: number;
  festival_impact?: string;
  recommendations: string[];
  shap_explanations: Record<string, number>;
}

export interface EmailDraft {
  recipient_type: string;
  recipient_name: string;
  subject: string;
  body: string;
  tone: string;
}

export interface PaymentSchedule {
  date: string;
  vendor: string;
  amount: number;
  priority: string;
  notes: string;
}

export interface ActionPlan {
  payment_schedule: PaymentSchedule[];
  email_drafts: EmailDraft[];
  summary: string;
}
