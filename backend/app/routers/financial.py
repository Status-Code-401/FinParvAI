from fastapi import APIRouter, HTTPException
from app.services.decision_engine import run_engine, simulate_cash_flow, calculate_runway
from app.services.email_generator import generate_all_emails
from app.services.data_ingestion import (
    load_normalized_state, enrich_from_ledger, 
    _parse_normalized_state, enrich_from_ledger_dict
)
from app.services.predictive_engine import forecast_revenue, compute_seasonal_insights, generate_demand_forecast
from app.services.context_agents import WebCrawlingAgent, ContextAnalysisAgent
from app.services.database import db
import os
import json

router = APIRouter(prefix="/api", tags=["financials"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "mock_data")


BUSINESS_ID = 1

def _load_state():
    """Load financial state from DB (with transparent mock fallback)."""
    state_dict = db.get_financial_state(BUSINESS_ID)
    state = _parse_normalized_state(state_dict)
    
    # Enrich with ledger data (also from DB/mock)
    ledger_dict = db.get_ledger(BUSINESS_ID)
    state = enrich_from_ledger_dict(state, ledger_dict)
    
    return state


def _load_ledger():
    """Load ledger data from DB (with transparent mock fallback)."""
    return db.get_ledger(BUSINESS_ID)


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
        "actions": result["actions"]["actions"],
        "explanation": result["explanation"],
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

    # Agent Layer: Extract context multiplier
    signals = {}
    agent_reasoning = "Market signals stable."
    multiplier = 1.0

    try:
        crawler = WebCrawlingAgent()
        signals = crawler.gather_signals()
        analyzer = ContextAnalysisAgent()
        context = analyzer.analyze_context(signals)
        multiplier = context.get("demand_multiplier", 1.0)
        agent_reasoning = context.get("reasoning", "")
    except Exception as e:
        print(f"Agent analysis failed: {e}")
        agent_reasoning = "Live market context temporarily unavailable — using calendar baseline."

    revenue_forecast = forecast_revenue(monthly_incomes, periods=3, context_multiplier=multiplier)
    seasonal = compute_seasonal_insights(monthly_data)

    # Production trend from daily data
    prod_data = ledger.get("production_data", {}).get("daily_production", {})
    prod_units = list(prod_data.values()) if prod_data else []
    demand_forecast = generate_demand_forecast(prod_units, days=30, demand_multiplier=multiplier)

    # Merge agent signals into seasonal insights for the frontend to display
    seasonal.update({
        "market_sentiment": signals.get("market_sentiment", "neutral"),
        "sentiment_summary": signals.get("sentiment_summary", ""),
        "action_insight": signals.get("action_insight", ""),
        "source_links": signals.get("source_links", []),
        "news_source": signals.get("news_source", "fallback"),
        "upcoming_festivals": signals.get("upcoming_festivals", []),
    })

    return {
        "revenue_forecast": revenue_forecast,
        "seasonal_insights": seasonal,
        "demand_forecast": demand_forecast,
        "monthly_summary": monthly_data,
        "key_insights": seasonal.get("insights", []) + [agent_reasoning]
    }


@router.get("/ledger")
def get_ledger():
    """Return full ledger summary and client ledger."""
    ledger = _load_ledger()
    return ledger


@router.get("/transactions")
def get_transactions():
    """Return recent transaction history from DB."""
    state = _load_state()
    # Pull from the state object which already came from DB/Mock
    return {
        "transactions": [t.dict() for t in state.transactions],
        "total": len(state.transactions)
    }


@router.get("/calendar")
def get_calendar():
    """
    Return a day-keyed event map for the calendar dashboard.
    Each date key maps to a list of events: sales, payables, receivables,
    procurement deliveries, and historical bank transactions.
    Covers 60 days back and 45 days forward from today.
    """
    from datetime import date, timedelta

    state = _load_state()
    ledger = _load_ledger()

    today = date.today()
    start_date = today - timedelta(days=60)
    end_date = today + timedelta(days=45)

    # Build an empty day map
    day_map: dict = {}
    cursor = start_date
    while cursor <= end_date:
        day_map[str(cursor)] = {
            "date": str(cursor),
            "is_today": cursor == today,
            "is_past": cursor < today,
            "is_future": cursor > today,
            "events": [],
            "net_flow": 0.0,
            "total_inflow": 0.0,
            "total_outflow": 0.0,
        }
        cursor += timedelta(days=1)

    def add_event(date_str: str, event: dict):
        if date_str in day_map:
            flow = event.get("amount", 0)
            if event.get("flow") == "in":
                day_map[date_str]["total_inflow"] += flow
                day_map[date_str]["net_flow"] += flow
            elif event.get("flow") == "out":
                day_map[date_str]["total_outflow"] += flow
                day_map[date_str]["net_flow"] -= flow
            day_map[date_str]["events"].append(event)

    # ── 1. Historical bank transactions ─────────────────────────────────────
    for txn in state.transactions:
        if txn.date in day_map:
            if txn.credit and txn.credit > 0:
                add_event(txn.date, {
                    "type": "bank_credit",
                    "label": txn.description or "Payment received",
                    "amount": txn.credit,
                    "flow": "in",
                    "category": txn.category or "income",
                    "badge": "success",
                })
            if txn.debit and txn.debit > 0:
                add_event(txn.date, {
                    "type": "bank_debit",
                    "label": txn.description or "Payment made",
                    "amount": txn.debit,
                    "flow": "out",
                    "category": txn.category or "expense",
                    "badge": "danger",
                })

    # ── 2. Daily production (past + today) ───────────────────────────────────
    prod_data = ledger.get("production_data", {}).get("daily_production", {})
    cost_per_unit = ledger.get("production_data", {}).get("cost_per_unit", 95)
    sell_per_unit = ledger.get("production_data", {}).get("selling_price_per_unit", 185)

    for date_str, units in prod_data.items():
        if date_str in day_map and units > 0:
            add_event(date_str, {
                "type": "production",
                "label": f"Production: {units} units",
                "units": units,
                "amount": round(units * sell_per_unit, 2),
                "cost": round(units * cost_per_unit, 2),
                "flow": "in",
                "badge": "info",
            })

    # ── 3. Future expected production (simple avg projection) ────────────────
    if prod_data:
        avg_daily = round(sum(prod_data.values()) / len(prod_data))
        future = today + timedelta(days=1)
        while future <= end_date:
            fstr = str(future)
            if fstr in day_map and future.weekday() < 6:  # Mon-Sat
                add_event(fstr, {
                    "type": "production_forecast",
                    "label": f"Expected production: ~{avg_daily} units",
                    "units": avg_daily,
                    "amount": round(avg_daily * sell_per_unit, 2),
                    "flow": "in",
                    "badge": "info",
                    "forecast": True,
                })
            future += timedelta(days=1)

    # ── 4. Payables ─────────────────────────────────────────────────────────
    for p in ledger.get("active_payables", []):
        due = p.get("due_date", "")
        if due in day_map:
            add_event(due, {
                "type": "payable",
                "label": f"Pay {p['vendor']}: {p.get('description', '')}",
                "vendor": p["vendor"],
                "amount": p["amount"],
                "flow": "out",
                "priority": p.get("type", "flexible"),
                "badge": "danger" if p.get("type") == "critical" else "warning",
                "payable_id": p.get("payable_id"),
                "status": p.get("status", "unpaid"),
            })

    # ── 5. Receivables ───────────────────────────────────────────────────────
    for r in ledger.get("active_receivables", []):
        exp = r.get("expected_date", "")
        if exp in day_map:
            add_event(exp, {
                "type": "receivable",
                "label": f"Collect from {r['client']}",
                "client": r["client"],
                "amount": r["amount"],
                "flow": "in",
                "probability": r.get("collection_probability", 0.8),
                "badge": "success",
                "invoice_id": r.get("invoice_id"),
                "status": r.get("status", "upcoming"),
            })

    # ── 6. Procurement deliveries ─────────────────────────────────────────────
    with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
        inv_data = json.load(f)
    proc_orders = inv_data.get("procurement_orders", [])

    for po in proc_orders:
        delivery_date = po.get("expected_delivery") or po.get("actual_delivery")
        if delivery_date and delivery_date in day_map:
            add_event(delivery_date, {
                "type": "procurement",
                "label": f"Delivery: {po.get('material', '')} from {po.get('vendor', '')}",
                "vendor": po.get("vendor", ""),
                "material": po.get("material", ""),
                "quantity": po.get("quantity", 0),
                "amount": po.get("total_cost", 0),
                "flow": "neutral",
                "badge": "accent",
                "order_id": po.get("order_id", ""),
                "status": po.get("status", "pending"),
            })

    # Return as sorted list for easy frontend rendering
    return {
        "days": [day_map[k] for k in sorted(day_map.keys())],
        "today": str(today),
        "start": str(start_date),
        "end": str(end_date),
        "summary": {
            "total_payables_due": sum(p["amount"] for p in ledger.get("active_payables", [])),
            "total_receivables_expected": sum(r["amount"] for r in ledger.get("active_receivables", [])),
            "procurement_deliveries": len(proc_orders),
        }
    }


# ─── v2: COST INTELLIGENCE COMBINED ENDPOINT ──────────────────────────────────

@router.get("/cost-intelligence")
def get_cost_intelligence():
    """
    Combined endpoint that runs all 4 v2 modules:
    M1: Cost Impact Engine
    M2: Cost Leakage Detection Engine
    M3: Autonomous Execution Layer
    M4: Enterprise Signal Layer
    
    Returns a unified response for the frontend Cost Intelligence Dashboard.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    
    from services.impact_engine import run_impact_engine
    from services.leakage_engine import run_leakage_engine
    from services.execution_engine import run_execution_engine
    from services.signal_engine import run_signal_engine

    state = _load_state()
    ledger = _load_ledger()
    result = run_engine(state)

    # Load inventory/procurement data
    with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
        inv_data = json.load(f)

    # ── M1: Impact Engine ──
    actions = result.get("actions", {}).get("actions", [])
    state_context = {
        "cash_balance": state.cash_balance,
        "shortfall": result.get("shortfall", {}).get("gap", 0),
        "inventory_status": [i.dict() for i in state.inventory_status],
    }
    impact_result = run_impact_engine(state_context, actions)

    # ── M2: Leakage Detection ──
    leak_input = {
        "transactions": [t.dict() for t in state.transactions],
        "payables": [p.dict() for p in state.payables],
        "receivables": [r.dict() for r in state.receivables],
        "inventory_status": [i.dict() for i in state.inventory_status],
        "procurement_orders": inv_data.get("procurement_orders", []),
        "vendor_insights": [v.dict() for v in state.vendor_insights],
    }
    leakage_result = run_leakage_engine(leak_input)

    # ── M4: Enterprise Signals ──
    signal_input = {
        "payables": [p.dict() for p in state.payables],
        "receivables": [r.dict() for r in state.receivables],
        "inventory_status": [i.dict() for i in state.inventory_status],
        "procurement_orders": inv_data.get("procurement_orders", []),
        "vendor_insights": [v.dict() for v in state.vendor_insights],
        "production": state.production.dict() if state.production else {},
        "ledger_summary": state.ledger_summary.dict() if state.ledger_summary else {},
    }
    signal_result = run_signal_engine(signal_input)

    # ── M3: Execution Layer ──
    exec_result = run_execution_engine(impact_result.get("actions_with_impact", []))

    # ── Combined Summary ──
    total_savings = impact_result.get("total_potential_savings", 0)
    total_leakage = leakage_result.get("total_leakage_amount", 0)
    total_signal_impact = signal_result.get("total_impact", 0)

    return {
        "impact": impact_result,
        "leakage": leakage_result,
        "signals": signal_result,
        "execution": exec_result,
        "combined_summary": {
            "total_potential_savings": round(total_savings, 2),
            "total_leakage_detected": round(total_leakage, 2),
            "total_signal_impact": round(total_signal_impact, 2),
            "grand_total_financial_impact": round(total_savings + total_leakage + total_signal_impact, 2),
            "actions_count": len(actions),
            "leakages_count": leakage_result.get("leakage_count", 0),
            "signals_count": signal_result.get("total_signals", 0),
            "execution_ready_count": exec_result.get("auto_eligible_count", 0),
            "risk_level": result.get("risk_level", "unknown"),
            "cash_balance": state.cash_balance,
        }
    }