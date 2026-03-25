"""
Action Generator Service
Converts decision engine outputs into actionable plans and email drafts.
Tone adapts based on counterparty relationship profile.
"""
from datetime import datetime, timedelta
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import DecisionOutput, EmailDraft, PaymentSchedule, ActionPlan, FinancialState


RELATIONSHIP_TONES = {
    "long_term":  "semi-formal",
    "new":        "formal",
    "delinquent": "urgent",
    "preferred":  "semi-formal",
    "default":    "formal",
}


def _get_tone(vendor_or_client: str, relationship: str = "default") -> str:
    return RELATIONSHIP_TONES.get(relationship, "formal")


def draft_early_payment_request(client: str, amount: float, due_date: str, tone: str = "semi-formal") -> EmailDraft:
    incentive = round(amount * 0.05)
    if tone == "formal":
        body = f"""Dear {client},

I hope this message finds you well.

We are writing to request an early settlement of the outstanding amount of ₹{amount:,.0f}, currently due on {due_date}.

As a gesture of appreciation for your continued partnership, we are pleased to offer a 5% early payment discount (₹{incentive:,.0f}) if payment is received by {(datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")}.

Kindly arrange the transfer at your earliest convenience and share the payment confirmation with us.

Warm regards,
Finance Team"""
    else:
        body = f"""Hi {client},

Quick note — we'd appreciate an early settlement on the ₹{amount:,.0f} due {due_date}. We're offering a ₹{incentive:,.0f} discount (5%) if you can process it by {(datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")}.

Would you be able to do that? Let me know!

Thanks,
Finance Team"""

    return EmailDraft(
        recipient_type="client",
        recipient_name=client,
        subject=f"Early Payment Request – Invoice Due {due_date}",
        body=body,
        tone=tone,
    )


def draft_payment_delay_request(vendor: str, amount: float, due_date: str, tone: str = "formal", days_requested: int = 7) -> EmailDraft:
    new_date = (datetime.strptime(due_date, "%Y-%m-%d") + timedelta(days=days_requested)).strftime("%Y-%m-%d")

    if tone == "urgent":
        body = f"""Dear {vendor},

We acknowledge the outstanding payment of ₹{amount:,.0f} due on {due_date}.

Due to temporary liquidity constraints, we respectfully request an extension of {days_requested} days, making the revised due date {new_date}. We assure you that payment will be made on or before this date.

We sincerely apologize for any inconvenience caused and value our ongoing partnership.

Regards,
Finance Team"""
    else:
        body = f"""Dear {vendor},

We hope you are doing well.

We are writing regarding our upcoming payment of ₹{amount:,.0f} scheduled for {due_date}. We would like to request a brief extension of {days_requested} days, with a revised payment date of {new_date}.

We remain committed to maintaining our strong business relationship and appreciate your understanding.

Best regards,
Finance Team"""

    return EmailDraft(
        recipient_type="vendor",
        recipient_name=vendor,
        subject=f"Payment Extension Request – Due {due_date}",
        body=body,
        tone=tone,
    )


def build_payment_schedule(decision: DecisionOutput, state: FinancialState) -> List[PaymentSchedule]:
    schedule = []
    today = datetime.today().date()

    payable_map = {p.vendor: p for p in (state.payables or [])}

    for sp in decision.scored_payables:
        if sp.action == "pay_now":
            date_str = today.strftime("%Y-%m-%d")
            notes    = f"Immediate payment. {sp.reason}"
            priority = "high"
        elif sp.action == "partial":
            date_str = today.strftime("%Y-%m-%d")
            notes    = f"Partial ₹{sp.partial_amount:,.0f}. Remainder to be rescheduled. {sp.reason}"
            priority = "high"
        else:  # delay
            orig_due = payable_map.get(sp.vendor)
            if orig_due:
                delayed  = datetime.strptime(orig_due.due_date, "%Y-%m-%d") + timedelta(days=7)
                date_str = delayed.strftime("%Y-%m-%d")
            else:
                date_str = (today + timedelta(days=7)).strftime("%Y-%m-%d")
            notes    = f"Rescheduled. {sp.reason}"
            priority = "low"

        amount = sp.partial_amount if sp.action == "partial" else sp.amount

        schedule.append(PaymentSchedule(
            date=date_str,
            vendor=sp.vendor,
            amount=round(amount, 2),
            priority=priority,
            notes=notes,
        ))

    # Sort by date, then priority
    schedule.sort(key=lambda x: (x.date, {"high": 0, "medium": 1, "low": 2}[x.priority]))
    return schedule


def generate_action_plan(decision: DecisionOutput, state: FinancialState) -> ActionPlan:
    emails: List[EmailDraft] = []

    # Early payment requests to clients
    for r in (state.receivables or []):
        if decision.risk_level in ("high", "critical"):
            tone = "urgent" if decision.risk_level == "critical" else "formal"
            emails.append(draft_early_payment_request(r.client, r.amount, r.expected_date, tone))

    # Delay requests to vendors
    payable_map = {p.vendor: p for p in (state.payables or [])}
    for vendor_name in decision.delay:
        p = payable_map.get(vendor_name)
        if p:
            tone = "urgent" if p.type == "critical" else "formal"
            emails.append(draft_payment_delay_request(vendor_name, p.amount, p.due_date, tone))

    # Payment schedule
    schedule = build_payment_schedule(decision, state)

    # Summary
    summary_lines = [
        f"📊 Risk Level: {decision.risk_level.upper()}",
        f"💰 Current Cash: ₹{state.cash_balance:,.0f}",
        f"📅 Runway: {decision.runway_days} days",
        f"✅ Pay Now: {', '.join(decision.pay_now) or 'None'}",
        f"🕐 Delay: {', '.join(decision.delay) or 'None'}",
        f"⚡ Partial: {', '.join(decision.partial) or 'None'}",
        f"📧 {len(emails)} email draft(s) generated",
        f"📋 {len(schedule)} payment(s) scheduled",
    ]

    return ActionPlan(
        payment_schedule=schedule,
        email_drafts=emails,
        summary="\n".join(summary_lines),
    )
