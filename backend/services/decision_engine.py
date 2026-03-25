"""
Deterministic Decision Engine
Same input → same output. Constraint-first. Priority-driven. Fallback-safe.
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import (
    FinancialState, DailyCashFlow, ScoredPayable, RecoveryStrategy, DecisionOutput
)

# ─── Weights for obligation scoring ──────────────────────────────────────────
W_URGENCY   = 0.35
W_PENALTY   = 0.30
W_TYPE      = 0.25
W_FLEX      = 0.10

PENALTY_MAP   = {"low": 0.2, "medium": 0.5, "high": 1.0}
TYPE_MAP      = {"critical": 1.0, "flexible": 0.3}
FLEX_MAP      = {"critical": 0.0, "flexible": 1.0}


def _days_until(due_date_str: str) -> int:
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        return max((due - today).days, 0)
    except Exception:
        return 7


def _urgency_score(days: int) -> float:
    """More urgent = higher score. Clamp at 0-1."""
    if days <= 0:
        return 1.0
    if days >= 30:
        return 0.0
    return 1.0 - (days / 30.0)


def score_payable(payable) -> float:
    days = _days_until(payable.due_date)
    urgency  = _urgency_score(days)
    penalty  = PENALTY_MAP.get(payable.penalty, 0.5)
    type_p   = TYPE_MAP.get(payable.type, 0.3)
    flex     = FLEX_MAP.get(payable.type, 1.0)
    score = (W_URGENCY * urgency) + (W_PENALTY * penalty) + (W_TYPE * type_p) - (W_FLEX * flex)
    return round(score, 4)


# ─── Cash Flow Simulator ──────────────────────────────────────────────────────

def simulate_cash_flow(state: FinancialState, days: int = 14) -> List[DailyCashFlow]:
    today = datetime.today().date()
    cash = state.cash_balance
    projection = []

    for i in range(days):
        day_date = today + timedelta(days=i)
        day_str  = day_date.strftime("%Y-%m-%d")
        events   = []
        inflows  = 0.0
        outflows = 0.0

        # Check receivables
        for r in (state.receivables or []):
            if r.expected_date == day_str:
                expected = r.amount * r.collection_probability
                inflows += expected
                events.append(f"Receivable from {r.client}: ₹{expected:,.0f}")

        # Check payables
        for p in (state.payables or []):
            if p.due_date == day_str:
                outflows += p.amount
                events.append(f"Payable to {p.vendor}: ₹{p.amount:,.0f}")

        # Distribute overheads evenly (assume monthly → divide by 30)
        daily_overhead = sum(o.amount for o in (state.overheads or [])) / 30
        outflows += daily_overhead
        if daily_overhead > 0:
            events.append(f"Daily overheads: ₹{daily_overhead:,.0f}")

        opening = cash
        cash = cash + inflows - outflows
        projection.append(DailyCashFlow(
            day=i,
            date=day_str,
            opening_cash=round(opening, 2),
            inflows=round(inflows, 2),
            outflows=round(outflows, 2),
            closing_cash=round(cash, 2),
            events=events,
        ))

    return projection


def runway_days(projection: List[DailyCashFlow]) -> Tuple[bool, int]:
    for p in projection:
        if p.closing_cash < 0:
            return False, p.day
    return True, len(projection)


# ─── Payment Allocation ───────────────────────────────────────────────────────

def allocate_payments(state: FinancialState) -> List[ScoredPayable]:
    payables = state.payables or []
    cash = state.cash_balance

    scored = []
    for p in payables:
        s = score_payable(p)
        scored.append((s, p))

    # Sort by score DESC; tie-break: earlier due date
    scored.sort(key=lambda x: (-x[0], x[1].due_date))

    result = []
    for score, p in scored:
        days = _days_until(p.due_date)
        if cash >= p.amount:
            action = "pay_now"
            reason = f"Sufficient cash. Score {score:.2f}. Due in {days}d."
            cash  -= p.amount
            partial = None
        elif cash > 0 and p.type != "critical":
            # partial only for flexible
            partial = round(cash, 2)
            action  = "partial"
            reason  = f"Insufficient full cash. Partial ₹{partial:,.0f} allocated. Remainder delayed."
            cash    = 0
        elif cash > 0 and p.type == "critical":
            partial = round(cash, 2)
            action  = "partial"
            reason  = f"CRITICAL obligation. Partial payment ₹{partial:,.0f}. Emergency collection needed."
            cash    = 0
        else:
            action  = "delay"
            reason  = f"No cash available. Mark for delay/negotiation."
            partial = None

        result.append(ScoredPayable(
            vendor=p.vendor,
            amount=p.amount,
            due_date=p.due_date,
            score=score,
            action=action,
            reason=reason,
            partial_amount=partial,
        ))

    return result


# ─── Shortfall Recovery ───────────────────────────────────────────────────────

def build_recovery_strategies(state: FinancialState, shortfall: float) -> List[RecoveryStrategy]:
    strategies = []
    remaining  = shortfall

    # 1. Pull receivables early
    ar_total = sum(r.amount * r.collection_probability for r in (state.receivables or []))
    if ar_total > 0 and remaining > 0:
        impact = min(ar_total, remaining)
        strategies.append(RecoveryStrategy(
            type="early_collection",
            description=f"Request early payment from clients (offer ~5% incentive). Potential recovery: ₹{ar_total:,.0f}",
            estimated_impact=impact,
        ))
        remaining -= impact

    # 2. Delay flexible payables
    flexible_total = sum(p.amount for p in (state.payables or []) if p.type == "flexible")
    if flexible_total > 0 and remaining > 0:
        impact = min(flexible_total, remaining)
        strategies.append(RecoveryStrategy(
            type="delay_flexible",
            description=f"Reschedule flexible payables (₹{flexible_total:,.0f}) to next cycle.",
            estimated_impact=impact,
        ))
        remaining -= impact

    # 3. Reduce non-essential overheads
    non_essential = sum(o.amount for o in (state.overheads or []) if not o.essential)
    if non_essential > 0 and remaining > 0:
        impact = min(non_essential, remaining)
        strategies.append(RecoveryStrategy(
            type="cut_overheads",
            description=f"Pause/reduce non-essential overheads (ads, travel). Saves ₹{non_essential:,.0f}",
            estimated_impact=impact,
        ))
        remaining -= impact

    # 4. Inventory optimization
    excess_val = 0.0
    for inv in (state.inventory_status or []):
        if inv.excess > 0:
            # Rough liquidation value
            for proc in (state.inventory_procurement or []):
                if proc.material.lower() == inv.item.lower():
                    excess_val += inv.excess * proc.unit_cost * 0.7  # 70% liquidation
    if excess_val > 0 and remaining > 0:
        impact = min(excess_val, remaining)
        strategies.append(RecoveryStrategy(
            type="inventory_liquidation",
            description=f"Liquidate excess inventory at ~70% value. Estimated recovery: ₹{excess_val:,.0f}",
            estimated_impact=impact,
        ))
        remaining -= impact

    return strategies


# ─── Overhead & Inventory Actions ─────────────────────────────────────────────

def overhead_actions(state: FinancialState) -> List[str]:
    actions = []
    for o in (state.overheads or []):
        if not o.essential:
            actions.append(f"⚠️ Pause '{o.type}' overhead (₹{o.amount:,.0f}) – non-essential")
        else:
            actions.append(f"✅ Keep '{o.type}' overhead (₹{o.amount:,.0f}) – essential")
    return actions


def inventory_actions(state: FinancialState) -> List[str]:
    actions = []
    for inv in (state.inventory_status or []):
        if inv.shortage > 0:
            actions.append(f"🔴 SHORTAGE: {inv.item} – need {inv.shortage:.0f} more units. Expedite procurement.")
        elif inv.excess > 0:
            actions.append(f"🟡 EXCESS: {inv.item} – {inv.excess:.0f} units surplus. Consider JIT or liquidation.")
        else:
            actions.append(f"🟢 OK: {inv.item} – inventory balanced.")
    return actions


# ─── Explanation Generator ─────────────────────────────────────────────────────

def generate_explanation(
    state: FinancialState,
    is_safe: bool,
    runway: int,
    scored: List[ScoredPayable],
    strategies: List[RecoveryStrategy],
) -> str:
    lines = []
    lines.append(f"💰 Current cash balance: ₹{state.cash_balance:,.0f}")

    if is_safe:
        lines.append(f"✅ Cash flow is SAFE for the next {runway} days based on current obligations and expected receivables.")
    else:
        lines.append(f"⚠️ Cash shortfall projected in {runway} days. Immediate action required.")

    pay_now = [s for s in scored if s.action == "pay_now"]
    delayed = [s for s in scored if s.action == "delay"]
    partial = [s for s in scored if s.action == "partial"]

    if pay_now:
        lines.append(f"✅ Pay immediately: {', '.join(s.vendor for s in pay_now)} – highest priority obligations.")
    if partial:
        lines.append(f"⚡ Partial payments: {', '.join(s.vendor for s in partial)} – cash insufficient for full amount.")
    if delayed:
        lines.append(f"🕐 Delayed: {', '.join(s.vendor for s in delayed)} – low-priority or flexible obligations.")

    if strategies:
        lines.append("🔄 Recovery strategies activated:")
        for st in strategies:
            lines.append(f"   • {st.description} (estimated ₹{st.estimated_impact:,.0f} recovery)")

    return "\n".join(lines)


# ─── Main Entry Point ─────────────────────────────────────────────────────────

def run_decision_engine(state: FinancialState) -> DecisionOutput:
    # 1. Simulate cash flow
    projection = simulate_cash_flow(state, days=14)
    safe, runway = runway_days(projection)

    # 2. Risk level
    if safe:
        risk = "low" if runway >= 14 else "medium"
    else:
        risk = "critical" if runway <= 2 else "high"

    # 3. Score and allocate payments
    scored = allocate_payments(state)

    # 4. Shortfall recovery
    min_cash = min(p.closing_cash for p in projection)
    shortfall = abs(min_cash) if min_cash < 0 else 0
    strategies = build_recovery_strategies(state, shortfall) if shortfall > 0 else []

    # 5. Categorize actions
    pay_now = [s.vendor for s in scored if s.action == "pay_now"]
    delay   = [s.vendor for s in scored if s.action == "delay"]
    partial = [s.vendor for s in scored if s.action == "partial"]

    # 6. Overhead + inventory actions
    oh_actions  = overhead_actions(state)
    inv_actions = inventory_actions(state)

    # 7. Explanation
    explanation = generate_explanation(state, safe, runway, scored, strategies)

    # 8. Confidence score (simple heuristic)
    confidence = 0.90 if safe else max(0.50, 0.90 - (shortfall / max(state.cash_balance, 1)) * 0.4)

    return DecisionOutput(
        runway_days=runway,
        is_safe=safe,
        risk_level=risk,
        cash_flow_projection=projection,
        scored_payables=scored,
        pay_now=pay_now,
        delay=delay,
        partial=partial,
        recovery_strategies=strategies,
        overhead_actions=oh_actions,
        inventory_actions=inv_actions,
        explanation=explanation,
        confidence_score=round(confidence, 2),
    )
