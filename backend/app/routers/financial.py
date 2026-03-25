from fastapi import APIRouter, HTTPException
from app.services.decision_engine import run_engine, simulate_cash_flow, calculate_runway
from app.services.email_generator import generate_all_emails
from app.services.data_ingestion import load_normalized_state, enrich_from_ledger
from app.services.predictive_engine import forecast_revenue, compute_seasonal_insights, generate_demand_forecast
<<<<<<< HEAD
from app.services.context_agents import WebCrawlingAgent, ContextAnalysisAgent
=======
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
import os
import json

router = APIRouter(prefix="/api", tags=["financials"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "mock_data")


def _load_state():
    state = load_normalized_state(os.path.join(MOCK_DATA_DIR, "normalized_financial_state.json"))
    state = enrich_from_ledger(state, os.path.join(MOCK_DATA_DIR, "ledger_data.json"))
    return state


def _load_ledger():
    with open(os.path.join(MOCK_DATA_DIR, "ledger_data.json")) as f:
        return json.load(f)


@router.get("/financial-state")
def get_financial_state():
    """Return the normalized financial state."""
    state = _load_state()
    return state.dict()


@router.get("/dashboard")
def get_dashboard():
    """Return dashboard summary KPIs."""
    state = _load_state()
    result = run_engine(state)
    ledger = _load_ledger()

    return {
        "business_name": state.business_name,
        "cash_balance": state.cash_balance,
        "risk_level": result["risk_level"],
        "days_to_zero": result["runway"]["days_to_zero"],
        "is_safe": result["runway"]["is_safe"],
        "first_negative_date": result["runway"]["first_negative_date"],
        "total_payables": result["summary"]["total_payables"],
        "total_receivables_expected": result["summary"]["total_receivables_expected"],
        "total_overheads": result["summary"]["total_overheads"],
        "net_position": result["summary"]["net_position"],
        "monthly_income": state.ledger_summary.monthly_income if state.ledger_summary else 0,
        "monthly_expense": state.ledger_summary.monthly_expense if state.ledger_summary else 0,
        "avg_payment_cycle": state.ledger_summary.avg_payment_cycle_days if state.ledger_summary else 7,
        "payables_count": len(state.payables),
        "receivables_count": len(state.receivables),
        "overdue_receivables": len([r for r in state.receivables if r.days_overdue > 0]),
        "critical_payables": len([p for p in state.payables if p.type == "critical"]),
        "shortfall_detected": result["shortfall"]["shortfall_detected"],
        "production_units_month": state.production.units_this_month if state.production else 0,
        "production_target": state.production.monthly_target if state.production else 0,
    }


@router.get("/cash-flow")
def get_cash_flow(days: int = 30):
    """Return 30-day cash flow projection."""
    state = _load_state()
    projection = simulate_cash_flow(state, days=min(days, 60))
    runway = calculate_runway(projection)
    return {
        "projection": projection,
        "runway": runway,
        "cash_balance": state.cash_balance
    }


@router.get("/analyze")
def analyze():
    """Run the full decision engine and return all results."""
    state = _load_state()
    return run_engine(state)


@router.get("/recommendations")
def get_recommendations():
    """Return prioritized action list from the decision engine."""
    state = _load_state()
    result = run_engine(state)
    return {
        "actions": result["actions"]["actions"],
        "shortfall": result["shortfall"],
        "overhead_optimization": result["overhead_optimization"],
        "inventory_optimization": result["inventory_optimization"],
        "explanation": result["explanation"]
    }


@router.get("/email-drafts")
def get_email_drafts():
    """Return AI-drafted emails for clients and vendors."""
    state = _load_state()
    result = run_engine(state)
    ledger = _load_ledger()

    delayed_payables = result["allocation"]["delayed"]
    emails = generate_all_emails(
        receivables=state.receivables,
        delayed_payables=delayed_payables,
        payables=state.payables,
        vendor_insights=state.vendor_insights,
        client_ledger=ledger.get("client_ledger", [])
    )

    return {
        "emails": emails,
        "total": len(emails),
        "ar_emails": len([e for e in emails if e["type"] == "receivable_collection"]),
        "ap_emails": len([e for e in emails if e["type"] == "payment_delay_request"])
    }


@router.get("/vendors")
def get_vendors():
    """Return vendor insights and procurement orders."""
    state = _load_state()
    with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
        inv_data = json.load(f)

    return {
        "vendor_insights": [v.dict() for v in state.vendor_insights],
        "procurement_orders": inv_data.get("procurement_orders", []),
        "all_vendor_insights": inv_data.get("vendor_insights", [])
    }


@router.get("/inventory")
def get_inventory():
    """Return inventory status and optimization suggestions."""
    state = _load_state()
    with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
        inv_data = json.load(f)

    from app.services.decision_engine import optimize_inventory
    opt = optimize_inventory(state.inventory_status)

    return {
        "inventory_status": inv_data.get("inventory_status", []),
        "procurement_orders": inv_data.get("procurement_orders", []),
        "optimization": opt,
        "total_inventory_value": sum(
            i.get("total_value", 0) for i in inv_data.get("inventory_status", [])
        )
    }


@router.get("/payables")
def get_payables():
    """Return scored and sorted payables."""
    from app.services.decision_engine import score_payables
    state = _load_state()
    scored = score_payables(state.payables)
    return {
        "payables": [p.dict() for p in scored],
        "total_amount": sum(p.amount for p in scored),
        "critical_count": len([p for p in scored if p.type == "critical"]),
        "flexible_count": len([p for p in scored if p.type == "flexible"])
    }


@router.get("/receivables")
def get_receivables():
    """Return receivables with collection insights."""
    state = _load_state()
    ledger = _load_ledger()
    client_map = {c["client"]: c for c in ledger.get("client_ledger", [])}

    enriched = []
    for r in state.receivables:
        client_info = client_map.get(r.client, {})
        enriched.append({
            **r.dict(),
            "contact": client_info.get("contact", ""),
            "phone": client_info.get("phone", ""),
            "email": client_info.get("email", ""),
            "risk_level": client_info.get("risk_level", "medium"),
            "relationship_months": client_info.get("relationship_months", 0),
            "avg_payment_days": client_info.get("avg_payment_days", 14),
            "on_time_rate": client_info.get("on_time_payment_rate", 0.7)
        })

    return {
        "receivables": enriched,
        "total_expected": round(sum(r.amount * r.collection_probability for r in state.receivables), 2),
        "total_outstanding": sum(r.amount for r in state.receivables),
        "overdue_count": len([r for r in state.receivables if r.days_overdue > 0])
    }


@router.get("/forecast")
def get_forecast():
    """Return predictive analytics and forecasts."""
    state = _load_state()
    ledger = _load_ledger()

    monthly_data = ledger.get("monthly_summary", [])
    monthly_incomes = [m["income"] for m in monthly_data]
    monthly_expenses = [m["expense"] for m in monthly_data]

<<<<<<< HEAD
    # Agent Layer: Extract context multiplier
    try:
        crawler = WebCrawlingAgent()
        signals = crawler.gather_signals()
        analyzer = ContextAnalysisAgent()
        context = analyzer.analyze_context(signals)
        multiplier = context.get("demand_multiplier", 1.0)
        agent_reasoning = context.get("reasoning", "")
    except Exception as e:
        multiplier = 1.0
        agent_reasoning = "Agents unavailable."

    revenue_forecast = forecast_revenue(monthly_incomes, periods=3, context_multiplier=multiplier)
=======
    revenue_forecast = forecast_revenue(monthly_incomes, periods=3)
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
    seasonal = compute_seasonal_insights(monthly_data)

    # Production trend from daily data
    prod_data = ledger.get("production_data", {}).get("daily_production", {})
    prod_units = list(prod_data.values()) if prod_data else []
<<<<<<< HEAD
    demand_forecast = generate_demand_forecast(prod_units, days=30, demand_multiplier=multiplier)
=======
    demand_forecast = generate_demand_forecast(prod_units, days=30)
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948

    return {
        "revenue_forecast": revenue_forecast,
        "seasonal_insights": seasonal,
        "demand_forecast": demand_forecast,
        "monthly_summary": monthly_data,
<<<<<<< HEAD
        "key_insights": seasonal.get("insights", []) + [agent_reasoning]
=======
        "key_insights": seasonal.get("insights", [])
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
    }


@router.get("/ledger")
def get_ledger():
    """Return full ledger summary and client ledger."""
    ledger = _load_ledger()
    return ledger


@router.get("/transactions")
def get_transactions():
    """Return recent transaction history."""
    state = _load_state()
    with open(os.path.join(MOCK_DATA_DIR, "bank_statement.csv")) as f:
        content = f.read()
    from app.services.data_ingestion import parse_bank_statement_csv
    transactions = parse_bank_statement_csv(content)
    return {
        "transactions": [t.dict() for t in transactions],
        "total": len(transactions)
    }
