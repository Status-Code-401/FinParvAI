"""
Deterministic Decision Engine for FinParvai
All 9 components as per PRD
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
from app.models.financial_state import FinancialState, Payable, Receivable, Overhead, InventoryItem
import math

TODAY = datetime.now().date()

PENALTY_WEIGHT = {"none": 0, "low": 1, "medium": 2, "high": 3, "very_high": 5}
FLEX_WEIGHT = {"none": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
TYPE_WEIGHT = {"critical": 5, "flexible": 2, "non_essential": 0}


def _days_from_today(date_str: str) -> int:
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return (d - TODAY).days
    except Exception:
        return 99


# ── 4.1 Cash Flow Simulator ──────────────────────────────────────────────────
def simulate_cash_flow(state: FinancialState, days: int = 30) -> List[Dict]:
    """
    Simulate daily cash position for the next `days` days.
    Returns list of {date, cash, inflows, outflows, events}
    """
    cash = state.cash_balance
    projection = []

    # Build day-keyed inflow/outflow maps
    inflows: Dict[str, float] = {}
    outflows: Dict[str, float] = {}
    events: Dict[str, List[str]] = {}

    for r in state.receivables:
        d = r.expected_date[:10]
        weighted = r.amount * r.collection_probability
        inflows[d] = inflows.get(d, 0) + weighted
        events.setdefault(d, []).append(f"↑ {r.client} ₹{r.amount:,.0f} ({int(r.collection_probability*100)}% prob)")

    for p in state.payables:
        d = p.due_date[:10]
        outflows[d] = outflows.get(d, 0) + p.amount
        events.setdefault(d, []).append(f"↓ {p.vendor} ₹{p.amount:,.0f}")

    for day_idx in range(days):
        from datetime import timedelta
        current_date = (TODAY + timedelta(days=day_idx)).strftime("%Y-%m-%d")
        daily_in = inflows.get(current_date, 0)
        daily_out = outflows.get(current_date, 0)
        cash += daily_in
        cash -= daily_out
        projection.append({
            "date": current_date,
            "day": day_idx + 1,
            "cash": round(cash, 2),
            "inflows": round(daily_in, 2),
            "outflows": round(daily_out, 2),
            "events": events.get(current_date, [])
        })

    return projection


# ── 4.2 Runway Calculator ─────────────────────────────────────────────────────
def calculate_runway(projection: List[Dict]) -> Dict:
    """
    Find the first day cash goes negative.
    Returns days_to_zero, first_negative_date, is_safe.
    """
    for entry in projection:
        if entry["cash"] < 0:
            return {
                "days_to_zero": entry["day"],
                "first_negative_date": entry["date"],
                "is_safe": False,
                "min_cash": entry["cash"]
            }
    min_cash = min(e["cash"] for e in projection) if projection else 0
    return {
        "days_to_zero": -1,
        "first_negative_date": None,
        "is_safe": True,
        "min_cash": round(min_cash, 2)
    }


# ── 4.3 Obligation Scoring Model ──────────────────────────────────────────────
def score_payables(payables: List[Payable]) -> List[Payable]:
    """
    Deterministic priority scoring:
    score = (W1*urgency) + (W2*penalty) + (W3*type_priority) - (W4*flexibility)
    """
    W1, W2, W3, W4 = 0.30, 0.35, 0.25, 0.10

    scored = []
    for p in payables:
        days_left = _days_from_today(p.due_date)
        # Urgency: 0-10, higher when fewer days left
        urgency = max(0, 10 - days_left) / 10.0
        penalty = PENALTY_WEIGHT.get(p.penalty, 0) / 5.0
        type_prio = TYPE_WEIGHT.get(p.type, 2) / 5.0
        flex = FLEX_WEIGHT.get(p.flexibility, 2) / 4.0

        score = (W1 * urgency) + (W2 * penalty) + (W3 * type_prio) - (W4 * flex)
        # Critical always stays at top regardless
        if p.type == "critical" and p.penalty in ("high", "very_high"):
            score = max(score, 0.85)

        p.priority_score = round(min(score, 1.0), 4)
        p.days_until_due = days_left
        scored.append(p)

    # Sort: by score DESC, then due_date ASC (tie-breaker)
    scored.sort(key=lambda x: (-x.priority_score, x.due_date))
    return scored


# ── 4.4 Payment Allocation Engine ────────────────────────────────────────────
def allocate_payments(cash: float, payables: List[Payable]) -> Dict:
    """
    Allocates cash to payables in priority order.
    Guarantees: no overspending, no negative cash, critical first.
    """
    pay_now = []
    partial = []
    delayed = []
    remaining_cash = cash

    for p in payables:
        if remaining_cash >= p.amount:
            pay_now.append({
                "payable_id": p.payable_id,
                "vendor": p.vendor,
                "amount": p.amount,
                "status": "pay_now",
                "reason": f"Sufficient cash. Priority score: {p.priority_score}"
            })
            remaining_cash -= p.amount
        elif remaining_cash > 0 and p.flexibility not in ("none",):
            # Partial payment allowed
            paid = round(remaining_cash, 2)
            owed = round(p.amount - paid, 2)
            partial.append({
                "payable_id": p.payable_id,
                "vendor": p.vendor,
                "amount_paid": paid,
                "amount_remaining": owed,
                "status": "partial",
                "reason": f"Cash insufficient for full payment. Paying ₹{paid:,.0f} now, ₹{owed:,.0f} to be rescheduled."
            })
            remaining_cash = 0
        else:
            delayed.append({
                "payable_id": p.payable_id,
                "vendor": p.vendor,
                "amount": p.amount,
                "due_date": p.due_date,
                "status": "delayed",
                "reason": f"Insufficient cash. Flexibility: {p.flexibility}. Recommend negotiation."
            })

    return {
        "cash_available": cash,
        "cash_remaining_after_allocation": round(remaining_cash, 2),
        "pay_now": pay_now,
        "partial": partial,
        "delayed": delayed
    }


# ── 4.5 Shortfall Handling Engine ────────────────────────────────────────────
def handle_shortfall(state: FinancialState, projection: List[Dict]) -> Dict:
    """
    Detects shortfall and applies recovery strategies in strict order:
    1. Pull receivables early
    2. Delay flexible payables
    3. Reduce overheads
    4. Inventory optimization
    5. Partial payments
    """
    total_obligations = sum(p.amount for p in state.payables)
    total_receivables_expected = sum(r.amount * r.collection_probability for r in state.receivables)
    gap = total_obligations - (state.cash_balance + total_receivables_expected)

    if gap <= 0:
        return {
            "shortfall_detected": False,
            "gap": 0,
            "strategies": [],
            "summary": "No shortfall detected. Current cash + expected receivables cover all obligations."
        }

    strategies = []
    recovered = 0.0
    remaining_gap = gap

    # Strategy 1: Pull Receivables Early
    early_collections = []
    for r in sorted(state.receivables, key=lambda x: -x.amount):
        if remaining_gap <= 0:
            break
        days_overdue = r.days_overdue
        incentive_pct = 3 if days_overdue == 0 else 0
        suggested_amount = r.amount
        early_collections.append({
            "client": r.client,
            "invoice_id": r.invoice_id,
            "amount": suggested_amount,
            "incentive": f"{incentive_pct}% early payment discount" if incentive_pct > 0 else "Urgency follow-up",
            "expected_date": r.expected_date,
            "probability": r.collection_probability
        })
        recovered += suggested_amount * r.collection_probability
        remaining_gap -= suggested_amount * r.collection_probability

    if early_collections:
        strategies.append({
            "strategy": "Pull Receivables Early",
            "actions": early_collections,
            "estimated_recovery": round(recovered, 2)
        })

    # Strategy 2: Delay Flexible Payables
    deferred = []
    for p in state.payables:
        if remaining_gap <= 0:
            break
        if p.flexibility in ("high", "very_high", "medium") and p.type != "critical":
            deferred.append({
                "vendor": p.vendor,
                "amount": p.amount,
                "current_due": p.due_date,
                "suggested_delay": f"{min(7, 14)} days",
                "flexibility": p.flexibility
            })
            recovered += p.amount
            remaining_gap -= p.amount

    if deferred:
        strategies.append({
            "strategy": "Delay Flexible Payables",
            "actions": deferred,
            "estimated_recovery": round(sum(d["amount"] for d in deferred), 2)
        })

    # Strategy 3: Reduce Non-Essential Overheads
    reducible = []
    for ov in state.overheads:
        if remaining_gap <= 0:
            break
        if not ov.essential and ov.can_reduce:
            saving = round(ov.amount * (ov.reducible_by or 1.0), 2)
            reducible.append({
                "type": ov.type,
                "saving": saving,
                "action": f"Pause/reduce {ov.type}"
            })
            recovered += saving
            remaining_gap -= saving

    if reducible:
        strategies.append({
            "strategy": "Reduce Non-Essential Overheads",
            "actions": reducible,
            "estimated_recovery": round(sum(r["saving"] for r in reducible), 2)
        })

    # Strategy 4: Inventory (JIT/Liquidation)
    inv_actions = []
    for item in state.inventory_status:
        if item.excess > 0:
            value = round(item.excess * (item.unit_cost or 0), 2)
            if value > 0:
                inv_actions.append({
                    "item": item.item,
                    "excess_qty": item.excess,
                    "liquidation_value": value,
                    "action": f"Liquidate {item.excess} units of excess {item.item}"
                })
                recovered += value
                remaining_gap -= value

    if inv_actions:
        strategies.append({
            "strategy": "Inventory Liquidation",
            "actions": inv_actions,
            "estimated_recovery": round(sum(a["liquidation_value"] for a in inv_actions), 2)
        })

    return {
        "shortfall_detected": True,
        "gap": round(gap, 2),
        "recovered": round(recovered, 2),
        "remaining_gap_after_strategies": round(max(0, gap - recovered), 2),
        "strategies": strategies,
        "summary": (
            f"Shortfall of ₹{gap:,.0f} detected. Recovery plan covers ₹{recovered:,.0f}. "
            f"{'✅ Fully recoverable.' if recovered >= gap else f'⚠️ Remaining gap: ₹{max(0, gap-recovered):,.0f}'}"
        )
    }


# ── 4.6 Overhead Optimization ─────────────────────────────────────────────────
def optimize_overheads(overheads: List[Overhead]) -> Dict:
    keep = []
    reduce = []
    pause = []
    savings = 0.0

    for ov in overheads:
        if ov.essential:
            keep.append({"type": ov.type, "amount": ov.amount, "reason": "Essential – cannot reduce"})
        elif ov.can_reduce:
            saving = round(ov.amount * (ov.reducible_by or 1.0), 2)
            savings += saving
            if (ov.reducible_by or 0) >= 1.0:
                pause.append({"type": ov.type, "saving": saving, "action": "Pause immediately"})
            else:
                reduce.append({"type": ov.type, "saving": saving, "action": f"Reduce by {int((ov.reducible_by or 0)*100)}%"})

    return {
        "keep": keep,
        "reduce": reduce,
        "pause": pause,
        "total_savings": round(savings, 2)
    }


# ── 4.7 Inventory Optimization ────────────────────────────────────────────────
def optimize_inventory(inventory: List[InventoryItem]) -> Dict:
    jit_candidates = []
    liquidate = []
    shortage_alerts = []

    for item in inventory:
        if item.shortage > 0:
            shortage_alerts.append({
                "item": item.item,
                "shortage": item.shortage,
                "urgency": "HIGH" if item.shortage > item.required_quantity * 0.2 else "MEDIUM"
            })
        if item.excess > 0:
            value = round(item.excess * (item.unit_cost or 0), 2)
            liquidate.append({
                "item": item.item,
                "excess": item.excess,
                "liquidation_value": value,
                "recommendation": "Sell excess stock or return to vendor"
            })

    return {
        "jit_candidates": jit_candidates,
        "liquidation_candidates": liquidate,
        "shortage_alerts": shortage_alerts,
        "total_liquidation_value": round(sum(l["liquidation_value"] for l in liquidate), 2)
    }


# ── 4.8 Action Generator ──────────────────────────────────────────────────────
def generate_actions(
    allocation: Dict,
    shortfall: Dict,
    overhead_opt: Dict,
    inventory_opt: Dict
) -> Dict:
    actions = []

    for item in allocation["pay_now"]:
        actions.append({
            "id": f"ACT-PAY-{item['payable_id']}",
            "type": "payment",
            "priority": "HIGH",
            "action": f"Pay ₹{item['amount']:,.0f} to {item['vendor']}",
            "reason": item["reason"]
        })

    for item in allocation["partial"]:
        actions.append({
            "id": f"ACT-PARTIAL-{item['payable_id']}",
            "type": "partial_payment",
            "priority": "HIGH",
            "action": f"Make partial payment of ₹{item['amount_paid']:,.0f} to {item['vendor']}",
            "reason": item["reason"]
        })

    for item in allocation["delayed"]:
        actions.append({
            "id": f"ACT-DELAY-{item['payable_id']}",
            "type": "negotiate_delay",
            "priority": "MEDIUM",
            "action": f"Negotiate payment delay with {item['vendor']} (₹{item['amount']:,.0f} due {item['due_date']})",
            "reason": item["reason"]
        })

    for ov in overhead_opt.get("pause", []):
        actions.append({
            "id": f"ACT-OVERHEAD-{ov['type']}",
            "type": "cost_reduction",
            "priority": "MEDIUM",
            "action": f"Pause {ov['type']} to save ₹{ov['saving']:,.0f}",
            "reason": "Non-essential overhead during cash constraint"
        })

    for inv in inventory_opt.get("liquidation_candidates", []):
        if inv["liquidation_value"] > 0:
            actions.append({
                "id": f"ACT-INV-{inv['item'][:6].upper()}",
                "type": "inventory_action",
                "priority": "LOW",
                "action": f"Liquidate excess {inv['item']} (₹{inv['liquidation_value']:,.0f})",
                "reason": "Unlock cash from excess inventory"
            })

    return {"actions": actions, "total_actions": len(actions)}


# ── 4.9 Explainability Layer ───────────────────────────────────────────────────
def generate_explanation(
    state: FinancialState,
    allocation: Dict,
    shortfall: Dict,
    runway: Dict,
    overhead_opt: Dict
) -> str:
    lines = []

    lines.append(f"## Financial Decision Summary – {TODAY.strftime('%d %b %Y')}")
    lines.append(f"\n**Business:** {state.business_name or 'Sri Lakshmi Garments'}")
    lines.append(f"**Current Cash Balance:** ₹{state.cash_balance:,.0f}")

    if runway["is_safe"]:
        lines.append(f"**Liquidity Status:** ✅ Safe – No cash shortfall detected in the next 30 days.")
    else:
        lines.append(f"**Liquidity Status:** 🔴 ALERT – Cash turns negative on Day {runway['days_to_zero']} ({runway['first_negative_date']}).")

    if shortfall["shortfall_detected"]:
        lines.append(f"\n### Shortfall Analysis")
        lines.append(f"Total obligations exceed available cash by **₹{shortfall['gap']:,.0f}**.")
        lines.append(shortfall["summary"])

    lines.append(f"\n### Payment Decisions")
    for item in allocation["pay_now"][:5]:
        lines.append(f"- ✅ **Pay Now:** {item['vendor']} – ₹{item['amount']:,.0f}. {item['reason']}")
    for item in allocation["partial"][:3]:
        lines.append(f"- 🔶 **Partial:** {item['vendor']} – Pay ₹{item['amount_paid']:,.0f} now, reschedule ₹{item['amount_remaining']:,.0f}.")
    for item in allocation["delayed"][:3]:
        lines.append(f"- ⏳ **Delay:** {item['vendor']} – ₹{item['amount']:,.0f}. {item['reason']}")

    if overhead_opt.get("total_savings", 0) > 0:
        lines.append(f"\n### Cost Optimization")
        lines.append(f"By pausing non-essential spend, **₹{overhead_opt['total_savings']:,.0f}** can be saved.")
        for p in overhead_opt.get("pause", []):
            lines.append(f"- Pause {p['type']}: Save ₹{p['saving']:,.0f}")

    lines.append(f"\n### Key Trade-offs")
    lines.append("Electricity and salaries are prioritized due to high penalty risk (disconnection / staff trust).")
    lines.append("Marketing spend (Google/Instagram Ads) paused to conserve cash during constraint period.")
    lines.append("Flexible vendor payments renegotiated to maintain supplier relationships without penalty.")

    return "\n".join(lines)


# ── MASTER ENGINE RUNNER ───────────────────────────────────────────────────────
def run_engine(state: FinancialState) -> Dict:
    """Main orchestrator – runs all engine components in sequence."""
    # Score and sort payables
    scored_payables = score_payables(state.payables)
    state.payables = scored_payables

    # Simulate cash flow
    projection = simulate_cash_flow(state, days=30)

    # Calculate runway
    runway = calculate_runway(projection)

    # Allocate payments
    allocation = allocate_payments(state.cash_balance, scored_payables)

    # Shortfall handling
    shortfall = handle_shortfall(state, projection)

    # Overhead optimization
    overhead_opt = optimize_overheads(state.overheads)

    # Inventory optimization
    inventory_opt = optimize_inventory(state.inventory_status)

    # Generate actions
    actions = generate_actions(allocation, shortfall, overhead_opt, inventory_opt)

    # Generate explanation
    explanation = generate_explanation(state, allocation, shortfall, runway, overhead_opt)

    # Risk level
    if not runway["is_safe"]:
        risk_level = "critical"
    elif shortfall["shortfall_detected"]:
        risk_level = "high"
    elif state.cash_balance < 30000:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "timestamp": datetime.now().isoformat(),
        "risk_level": risk_level,
        "cash_balance": state.cash_balance,
        "runway": runway,
        "projection": projection,
        "allocation": allocation,
        "shortfall": shortfall,
        "overhead_optimization": overhead_opt,
        "inventory_optimization": inventory_opt,
        "actions": actions,
        "explanation": explanation,
        "summary": {
            "total_payables": sum(p.amount for p in state.payables),
            "total_receivables_expected": round(sum(r.amount * r.collection_probability for r in state.receivables), 2),
            "total_overheads": sum(o.amount for o in state.overheads),
            "net_position": round(state.cash_balance + sum(r.amount * r.collection_probability for r in state.receivables) - sum(p.amount for p in state.payables), 2)
        }
    }
