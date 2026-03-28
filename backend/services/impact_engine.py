"""
Cost Impact Engine (Module 1)
Quantifies the financial benefit of every recommended action.
All impact calculations are deterministic with full math transparency.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─── Impact Type Calculators ──────────────────────────────────────────────────

def calculate_liquidity_protection(shortfall: float, interest_rate: float = 0.12, days: int = 30) -> Dict:
    """
    avoided_borrowing_cost = shortfall * interest_rate * (days / 365)
    If the company avoids dipping into negative cash, it avoids emergency borrowing.
    """
    if shortfall <= 0:
        return {"type": "liquidity_savings", "amount": 0, "breakdown": {}}

    avoided_cost = shortfall * interest_rate * (days / 365)
    return {
        "type": "liquidity_savings",
        "amount": round(avoided_cost, 2),
        "breakdown": {
            "shortfall": shortfall,
            "interest_rate": interest_rate,
            "days": days,
            "formula": f"{shortfall} × {interest_rate} × ({days}/365) = ₹{avoided_cost:,.2f}"
        }
    }


def calculate_holding_cost_savings(excess_units: float, unit_cost: float, holding_rate: float = 0.15) -> Dict:
    """
    holding_cost = excess_inventory * unit_cost * holding_rate
    Savings from liquidating idle inventory.
    """
    if excess_units <= 0 or unit_cost <= 0:
        return {"type": "holding_cost_savings", "amount": 0, "breakdown": {}}

    holding_cost = excess_units * unit_cost * holding_rate
    return {
        "type": "holding_cost_savings",
        "amount": round(holding_cost, 2),
        "breakdown": {
            "excess_units": excess_units,
            "unit_cost": unit_cost,
            "holding_rate": holding_rate,
            "formula": f"{excess_units} × ₹{unit_cost} × {holding_rate} = ₹{holding_cost:,.2f}"
        }
    }


def calculate_payment_delay_benefit(payable_amount: float, cost_of_capital: float = 0.10, delay_days: int = 7) -> Dict:
    """
    benefit = payable_amount * cost_of_capital * (delay_days / 365)
    The time-value benefit of delaying a payment.
    """
    if payable_amount <= 0 or delay_days <= 0:
        return {"type": "payment_delay_savings", "amount": 0, "breakdown": {}}

    benefit = payable_amount * cost_of_capital * (delay_days / 365)
    return {
        "type": "payment_delay_savings",
        "amount": round(benefit, 2),
        "breakdown": {
            "payable_amount": payable_amount,
            "cost_of_capital": cost_of_capital,
            "delay_days": delay_days,
            "formula": f"₹{payable_amount:,.0f} × {cost_of_capital} × ({delay_days}/365) = ₹{benefit:,.2f}"
        }
    }


def calculate_early_collection_benefit(receivable_amount: float, cost_of_capital: float = 0.10, days_early: int = 7, discount_offered: float = 0.05) -> Dict:
    """
    Net benefit of collecting receivable early:
    benefit = receivable_amount * cost_of_capital * (days_early / 365)  (time-value gain)
    cost   = receivable_amount * discount_offered  (incentive cost)
    net    = benefit - cost + liquidity_value
    """
    if receivable_amount <= 0:
        return {"type": "early_collection_savings", "amount": 0, "breakdown": {}}

    time_value = receivable_amount * cost_of_capital * (days_early / 365)
    incentive_cost = receivable_amount * discount_offered
    net_benefit = max(0, time_value + receivable_amount * 0.01 - incentive_cost)  # Include liquidity premium

    return {
        "type": "early_collection_savings",
        "amount": round(net_benefit, 2),
        "breakdown": {
            "receivable_amount": receivable_amount,
            "time_value_gain": round(time_value, 2),
            "incentive_cost": round(incentive_cost, 2),
            "net_benefit": round(net_benefit, 2),
            "formula": f"Time value: ₹{time_value:,.2f} - Incentive: ₹{incentive_cost:,.2f}"
        }
    }


def calculate_overhead_cut_savings(overhead_amount: float, cut_percentage: float = 1.0, monthly: bool = True) -> Dict:
    """
    Savings from cutting/reducing overhead.
    """
    if overhead_amount <= 0:
        return {"type": "overhead_savings", "amount": 0, "breakdown": {}}

    savings = overhead_amount * cut_percentage
    if not monthly:
        savings = savings / 12  # annualize to monthly

    return {
        "type": "overhead_savings",
        "amount": round(savings, 2),
        "breakdown": {
            "overhead_amount": overhead_amount,
            "cut_percentage": f"{int(cut_percentage * 100)}%",
            "monthly_savings": round(savings, 2),
            "formula": f"₹{overhead_amount:,.0f} × {int(cut_percentage * 100)}% = ₹{savings:,.2f}/month"
        }
    }


# ─── Confidence Calculator ────────────────────────────────────────────────────

def calculate_confidence(action_type: str, data_quality: float = 0.9, historical_accuracy: float = 0.85) -> float:
    """
    confidence = base_confidence * data_quality * historical_accuracy_factor
    """
    base_confidence = {
        "pay_now": 0.95,
        "delay_payment": 0.85,
        "early_collection": 0.75,
        "cut_overhead": 0.90,
        "liquidate_inventory": 0.70,
        "partial_payment": 0.80,
    }.get(action_type, 0.75)

    confidence = base_confidence * data_quality * (0.5 + 0.5 * historical_accuracy)
    return round(min(confidence, 0.99), 2)


# ─── Per-Action Impact Calculator ─────────────────────────────────────────────

def calculate_action_impact(action: Dict, state_context: Dict) -> Dict:
    """
    Given an action dict from the decision engine, compute its quantified impact.
    Returns the action enriched with an 'impact' object.
    """
    action_type = action.get("type", "")
    amount = action.get("amount", 0)
    vendor = action.get("vendor", "")

    impact = {"amount": 0, "type": "unknown", "confidence": 0.75, "breakdown": {}}

    if action_type in ("payment", "pay_now"):
        # Paying on time avoids penalty — penalty is the impact
        penalty_amount = action.get("penalty_amount", 0)
        if penalty_amount > 0:
            impact = {
                "amount": penalty_amount,
                "type": "penalty_avoidance",
                "confidence": 0.95,
                "breakdown": {"penalty_avoided": penalty_amount}
            }
        else:
            impact = {
                "amount": round(amount * 0.02, 2),  # relationship value
                "type": "relationship_preservation",
                "confidence": 0.90,
                "breakdown": {"estimated_goodwill_value": round(amount * 0.02, 2)}
            }

    elif action_type in ("negotiate_delay", "delay_payment"):
        delay_benefit = calculate_payment_delay_benefit(amount, delay_days=7)
        impact = {
            "amount": delay_benefit["amount"],
            "type": "payment_delay_savings",
            "confidence": calculate_confidence("delay_payment"),
            "breakdown": delay_benefit["breakdown"]
        }

    elif action_type == "partial_payment":
        amount_paid = action.get("amount_paid", 0)
        amount_remaining = action.get("amount_remaining", amount)
        delay_benefit = calculate_payment_delay_benefit(amount_remaining, delay_days=7)
        impact = {
            "amount": delay_benefit["amount"],
            "type": "partial_delay_savings",
            "confidence": calculate_confidence("partial_payment"),
            "breakdown": delay_benefit["breakdown"]
        }

    elif action_type == "cost_reduction":
        saving = action.get("saving", 0)
        oh_impact = calculate_overhead_cut_savings(saving)
        impact = {
            "amount": oh_impact["amount"],
            "type": "overhead_savings",
            "confidence": calculate_confidence("cut_overhead"),
            "breakdown": oh_impact["breakdown"]
        }

    elif action_type == "inventory_action":
        liq_value = action.get("liquidation_value", 0)
        impact = {
            "amount": round(liq_value * 0.15, 2),  # holding cost saved
            "type": "holding_cost_savings",
            "confidence": calculate_confidence("liquidate_inventory"),
            "breakdown": {
                "liquidation_value": liq_value,
                "annual_holding_cost_rate": "15%",
                "holding_cost_saved": round(liq_value * 0.15, 2)
            }
        }

    elif action_type == "early_collection":
        ec_impact = calculate_early_collection_benefit(amount, days_early=7)
        impact = {
            "amount": ec_impact["amount"],
            "type": "early_collection_savings",
            "confidence": calculate_confidence("early_collection"),
            "breakdown": ec_impact["breakdown"]
        }

    return {
        **action,
        "impact": impact
    }


# ─── Master Impact Engine ─────────────────────────────────────────────────────

def run_impact_engine(state_dict: Dict, actions: List[Dict]) -> Dict:
    """
    Main entry point. Takes the financial state context and list of actions,
    returns all actions enriched with quantified impact.
    """
    enriched_actions = []
    total_savings = 0.0

    for action in actions:
        enriched = calculate_action_impact(action, state_dict)
        enriched_actions.append(enriched)
        total_savings += enriched.get("impact", {}).get("amount", 0)

    # Calculate liquidity protection if shortfall exists
    shortfall = state_dict.get("shortfall", 0)
    liquidity_impact = calculate_liquidity_protection(shortfall)

    # Calculate inventory holding costs
    inventory_items = state_dict.get("inventory_status", [])
    total_holding_savings = 0.0
    for item in inventory_items:
        excess = item.get("excess", 0) or 0
        unit_cost = item.get("unit_cost", 0) or 0
        if excess > 0 and unit_cost > 0:
            h = calculate_holding_cost_savings(excess, unit_cost)
            total_holding_savings += h["amount"]

    return {
        "actions_with_impact": enriched_actions,
        "total_potential_savings": round(total_savings + liquidity_impact["amount"] + total_holding_savings, 2),
        "liquidity_protection": liquidity_impact,
        "inventory_holding_savings": round(total_holding_savings, 2),
        "summary": {
            "actions_analyzed": len(enriched_actions),
            "total_savings_rupees": round(total_savings + liquidity_impact["amount"] + total_holding_savings, 2),
            "avg_confidence": round(
                sum(a.get("impact", {}).get("confidence", 0) for a in enriched_actions) / max(len(enriched_actions), 1),
                2
            ),
            "currency": "INR"
        }
    }
