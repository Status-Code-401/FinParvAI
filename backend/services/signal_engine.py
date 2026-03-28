"""
Enterprise Signal Layer (Module 4)
Simulates enterprise-grade signals:
- SLA Risk Detection
- Vendor Benchmarking
- Inventory Turnover Analysis
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─── Default Market Benchmarks (simulated) ────────────────────────────────────
MARKET_BENCHMARKS = {
    "Cotton Fabric": {"market_avg_price": 90, "unit": "meter"},
    "Silk Thread": {"market_avg_price": 25, "unit": "spool"},
    "Polyester Blend": {"market_avg_price": 65, "unit": "meter"},
    "Buttons (plastic)": {"market_avg_price": 1.5, "unit": "piece"},
    "Buttons (metal)": {"market_avg_price": 3.0, "unit": "piece"},
    "Zippers": {"market_avg_price": 8, "unit": "piece"},
    "Dye (reactive)": {"market_avg_price": 350, "unit": "kg"},
    "Elastic Band": {"market_avg_price": 12, "unit": "meter"},
    "Packaging Material": {"market_avg_price": 5, "unit": "piece"},
    "Labels & Tags": {"market_avg_price": 2, "unit": "piece"},
}


# ─── SLA Risk Signal ─────────────────────────────────────────────────────────

def detect_sla_risks(payables: List[Dict], sla_terms: Dict = None) -> List[Dict]:
    """
    FR1: SLA Risk Signal
    if payment_delay > allowed_days: penalty_risk = penalty_rate * amount
    """
    if sla_terms is None:
        # Default SLA terms per vendor type
        sla_terms = {
            "critical": {"allowed_delay_days": 0, "penalty_rate": 0.05},
            "flexible": {"allowed_delay_days": 7, "penalty_rate": 0.02},
            "non_essential": {"allowed_delay_days": 14, "penalty_rate": 0.01},
        }

    signals = []
    today = datetime.now().date()

    for p in payables:
        vendor = p.get("vendor", "Unknown")
        amount = p.get("amount", 0)
        due_date_str = p.get("due_date", "")
        ptype = p.get("type", "flexible")

        try:
            due_date = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
        except Exception:
            continue

        days_until_due = (due_date - today).days
        terms = sla_terms.get(ptype, sla_terms.get("flexible", {}))
        allowed_delay = terms.get("allowed_delay_days", 7)
        penalty_rate = terms.get("penalty_rate", 0.02)

        # Check if we're at risk of breaching SLA
        if days_until_due < 3 and ptype == "critical":
            # Critical payment due within 3 days — SLA risk
            penalty_risk = penalty_rate * amount
            signals.append({
                "signal": "sla_risk",
                "type": "sla_penalty",
                "vendor": vendor,
                "description": f"SLA penalty risk for {vendor} — payment due in {max(0, days_until_due)} day(s)",
                "days_until_due": max(0, days_until_due),
                "penalty_risk_amount": round(penalty_risk, 2),
                "impact": round(penalty_risk, 2),
                "severity": "high" if penalty_risk > 1000 else "medium",
                "recommendation": f"Prioritize payment to {vendor} to avoid ₹{penalty_risk:,.0f} penalty",
                "formula": f"₹{amount:,.0f} × {penalty_rate*100:.0f}% = ₹{penalty_risk:,.0f}"
            })
        elif days_until_due < 0:
            # Already overdue
            overdue_days = abs(days_until_due)
            penalty_risk = penalty_rate * amount * (1 + overdue_days * 0.01)
            signals.append({
                "signal": "sla_breach",
                "type": "sla_penalty",
                "vendor": vendor,
                "description": f"SLA BREACHED for {vendor} — payment overdue by {overdue_days} day(s)",
                "days_overdue": overdue_days,
                "penalty_risk_amount": round(penalty_risk, 2),
                "impact": round(penalty_risk, 2),
                "severity": "high",
                "recommendation": f"Immediate payment required to {vendor} — penalty accruing at ₹{amount * penalty_rate * 0.01:,.0f}/day",
                "formula": f"₹{amount:,.0f} × {penalty_rate*100:.0f}% × (1 + {overdue_days} × 1%) = ₹{penalty_risk:,.0f}"
            })

    return signals


# ─── Vendor Benchmarking ─────────────────────────────────────────────────────

def benchmark_vendors(procurement_orders: List[Dict], vendor_insights: List[Dict]) -> List[Dict]:
    """
    FR2: Vendor Benchmarking
    if vendor_price > market_avg: suggest_switch = True
    """
    signals = []

    for order in procurement_orders:
        material = order.get("material", "")
        vendor = order.get("vendor", "")
        unit_cost = order.get("unit_cost", 0)
        quantity = order.get("quantity", 0)

        # Find market benchmark
        benchmark = None
        for key, bench in MARKET_BENCHMARKS.items():
            if key.lower() in material.lower() or material.lower() in key.lower():
                benchmark = bench
                break

        if benchmark and unit_cost > 0:
            market_avg = benchmark["market_avg_price"]
            if unit_cost > market_avg * 1.1:  # 10% above market
                premium_pct = ((unit_cost - market_avg) / market_avg) * 100
                potential_savings = (unit_cost - market_avg) * quantity

                signals.append({
                    "signal": "vendor_overpriced",
                    "type": "vendor_benchmark",
                    "vendor": vendor,
                    "material": material,
                    "description": f"{vendor} charges {premium_pct:.0f}% above market for {material}",
                    "vendor_price": unit_cost,
                    "market_avg_price": market_avg,
                    "premium_percentage": round(premium_pct, 1),
                    "potential_savings": round(potential_savings, 2),
                    "impact": round(potential_savings, 2),
                    "severity": "high" if premium_pct > 25 else "medium",
                    "recommendation": f"Consider switching vendor for {material} — potential savings ₹{potential_savings:,.0f}",
                    "formula": f"(₹{unit_cost} - ₹{market_avg}) × {quantity} = ₹{potential_savings:,.0f}"
                })

    # Check vendor reliability vs cost
    for vi in vendor_insights:
        reliability = vi.get("reliability_score", 0.8)
        cost_eff = vi.get("cost_efficiency_score", 0.8)

        if reliability < 0.7 and cost_eff < 0.7:
            signals.append({
                "signal": "vendor_underperforming",
                "type": "vendor_benchmark",
                "vendor": vi["vendor"],
                "description": f"{vi['vendor']} has both low reliability ({reliability:.0%}) and poor cost efficiency ({cost_eff:.0%})",
                "reliability_score": reliability,
                "cost_efficiency_score": cost_eff,
                "impact": 0,
                "severity": "high",
                "recommendation": f"Evaluate alternatives to {vi['vendor']} — double underperformance detected"
            })

    return signals


# ─── Inventory Turnover Signal ────────────────────────────────────────────────

def analyze_inventory_turnover(
    inventory_status: List[Dict],
    production_data: Dict = None,
    ledger_summary: Dict = None
) -> List[Dict]:
    """
    FR3: Inventory Turnover Signal
    turnover_ratio = sales / inventory
    if low: inefficiency_flag = True
    """
    signals = []

    # Calculate total inventory value
    total_inventory_value = 0
    for item in inventory_status:
        qty = item.get("available_quantity", 0) or 0
        cost = item.get("unit_cost", 0) or 0
        total_inventory_value += qty * cost

    # Estimate monthly sales (from ledger or production)
    monthly_sales = 0
    if ledger_summary:
        monthly_sales = ledger_summary.get("monthly_income", 0)
    elif production_data:
        units = production_data.get("units_this_month", 0) or 0
        price = production_data.get("selling_price_per_unit", 185) or 185
        monthly_sales = units * price

    if total_inventory_value > 0 and monthly_sales > 0:
        # Monthly turnover ratio
        turnover_ratio = monthly_sales / total_inventory_value
        annual_turnover = turnover_ratio * 12

        if turnover_ratio < 1.5:
            # Low turnover — inventory is slow-moving
            signals.append({
                "signal": "low_inventory_turnover",
                "type": "inventory_efficiency",
                "description": f"Inventory turnover is low ({turnover_ratio:.2f}x monthly, {annual_turnover:.1f}x annual)",
                "turnover_ratio_monthly": round(turnover_ratio, 2),
                "turnover_ratio_annual": round(annual_turnover, 1),
                "total_inventory_value": round(total_inventory_value, 2),
                "monthly_sales": round(monthly_sales, 2),
                "impact": round(total_inventory_value * 0.1, 2),  # 10% carrying cost
                "severity": "high" if turnover_ratio < 0.8 else "medium",
                "recommendation": f"Reduce inventory levels — current ₹{total_inventory_value:,.0f} stock turns over only {annual_turnover:.1f}x/year",
                "formula": f"₹{monthly_sales:,.0f} / ₹{total_inventory_value:,.0f} = {turnover_ratio:.2f}x monthly"
            })

    # Per-item analysis
    for item in inventory_status:
        excess = item.get("excess", 0) or 0
        required = item.get("required_quantity", 0) or 0
        available = item.get("available_quantity", 0) or 0

        if required > 0 and available > 0:
            utilization = min(required, available) / available
            if utilization < 0.5 and excess > 0:
                signals.append({
                    "signal": "overstocked_item",
                    "type": "inventory_efficiency",
                    "item": item.get("item", "Unknown"),
                    "description": f"'{item.get('item', 'Unknown')}' is overstocked — only {utilization:.0%} utilization",
                    "available": available,
                    "required": required,
                    "excess": excess,
                    "utilization": round(utilization, 2),
                    "impact": round(excess * item.get("unit_cost", 0) * 0.15, 2),  # Annual holding cost
                    "severity": "medium" if utilization > 0.3 else "high",
                    "recommendation": f"Reduce '{item.get('item', 'Unknown')}' stock by {excess:.0f} units"
                })

    return signals


# ─── Cash Flow Velocity Signal ────────────────────────────────────────────────

def analyze_cash_velocity(ledger_summary: Dict = None, receivables: List[Dict] = None, payables: List[Dict] = None) -> List[Dict]:
    """
    Additional enterprise signal: Cash conversion cycle analysis
    """
    signals = []

    if ledger_summary:
        avg_collection = ledger_summary.get("avg_collection_days", 10)
        avg_payment = ledger_summary.get("avg_payment_cycle_days", 7)

        # Cash conversion cycle = collection days - payment days
        cash_cycle = avg_collection - avg_payment

        if cash_cycle > 5:
            signals.append({
                "signal": "slow_cash_conversion",
                "type": "cash_velocity",
                "description": f"Cash conversion gap: collecting in {avg_collection:.0f} days but paying in {avg_payment:.0f} days",
                "avg_collection_days": avg_collection,
                "avg_payment_days": avg_payment,
                "cash_conversion_gap": round(cash_cycle, 1),
                "impact": 0,
                "severity": "medium",
                "recommendation": f"Reduce collection cycle by {max(1, int(cash_cycle))} days or negotiate longer payment terms"
            })

    return signals


# ─── Operational SLA Signal (Factory/Resource Routing) ────────────────────────

def detect_operational_slas(factory_status: List[Dict], procurement_orders: List[Dict]) -> List[Dict]:
    """
    FR7: Operational SLA mitigation & Resource Routing.
    Detects delayed materials for active factories and recommends rerouting.
    """
    signals = []
    
    for fs in factory_status:
        delay = fs.get("delay_days", 0)
        penalty = fs.get("idle_penalty_per_day", 0)
        line = fs.get("line_name", "Unknown Line")
        product = fs.get("current_product", "Unknown Product")
        
        if delay > 0 and penalty > 0:
            impact = delay * penalty
            signals.append({
                "signal": "operational_sla_risk",
                "type": "sla_penalty",
                "description": f"Raw material delay of {delay} days for {line} risks ₹{impact:,.0f} idle penalty.",
                "line_name": line,
                "delay_days": delay,
                "idle_penalty_per_day": penalty,
                "impact": impact,
                "severity": "high" if impact > 25000 else "medium",
                "recommendation": f"Reroute {line} capacity to alternate demanding product to mitigate ₹{impact:,.0f} penalty.",
                "action_type": "reroute_production",
                "formula": f"{delay} days × ₹{penalty:,.0f}/day = ₹{impact:,.0f}"
            })
            
    return signals


# ─── Master Signal Engine ─────────────────────────────────────────────────────

def run_signal_engine(state_dict: Dict) -> Dict:
    """
    Main entry point. Runs all enterprise signal analyzers.
    Returns categorized signals with impact and recommendations.
    """
    payables = state_dict.get("payables", [])
    receivables = state_dict.get("receivables", [])
    inventory_status = state_dict.get("inventory_status", [])
    procurement_orders = state_dict.get("procurement_orders", [])
    vendor_insights = state_dict.get("vendor_insights", [])
    production_data = state_dict.get("production", {})
    ledger_summary = state_dict.get("ledger_summary", {})
    factory_status = state_dict.get("factory_status", [])

    # Run all signal analyzers
    sla_risks = detect_sla_risks(payables)
    vendor_benchmarks = benchmark_vendors(procurement_orders, vendor_insights)
    inventory_signals = analyze_inventory_turnover(inventory_status, production_data, ledger_summary)
    cash_velocity = analyze_cash_velocity(ledger_summary, receivables, payables)
    op_slas = detect_operational_slas(factory_status, procurement_orders)

    all_signals = sla_risks + vendor_benchmarks + inventory_signals + cash_velocity + op_slas

    # Sort by impact DESC
    all_signals.sort(key=lambda x: -x.get("impact", 0))

    total_impact = sum(s.get("impact", 0) for s in all_signals)

    return {
        "signals": all_signals,
        "total_signals": len(all_signals),
        "total_impact": round(total_impact, 2),
        "by_type": {
            "sla_risks": len(sla_risks) + len(op_slas),
            "vendor_benchmarks": len(vendor_benchmarks),
            "inventory_signals": len(inventory_signals),
            "cash_velocity": len(cash_velocity),
            "operational_slas": len(op_slas),
        },
        "by_severity": {
            "high": len([s for s in all_signals if s.get("severity") == "high"]),
            "medium": len([s for s in all_signals if s.get("severity") == "medium"]),
            "low": len([s for s in all_signals if s.get("severity") == "low"]),
        },
        "summary": f"Detected {len(all_signals)} enterprise signal(s) with ₹{total_impact:,.0f} total impact. "
                   f"{len(sla_risks) + len(op_slas)} SLA risk(s), {len(vendor_benchmarks)} vendor insight(s), "
                   f"{len(inventory_signals)} inventory signal(s)."
    }
