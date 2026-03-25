"""
Email Generator – Context-aware email drafts for clients and vendors.
Tone and strategy dynamically adapt based on counterparty relationship profile.
"""
from datetime import datetime
from app.models.financial_state import Receivable, Payable, VendorInsight
from typing import Dict, List, Optional

TODAY = datetime.now().strftime("%d %B %Y")
BUSINESS_NAME = "Sri Lakshmi Garments"
OWNER_NAME = "Anand Babu"


def _relationship_tone(months: int = 12, risk_level: str = "low") -> str:
    if months >= 18 and risk_level == "low":
        return "warm_partner"
    elif months >= 10 and risk_level in ("low", "medium"):
        return "professional"
    else:
        return "formal"


def draft_early_collection_email(receivable: Receivable, client_info: Optional[Dict] = None) -> Dict:
    """Generate early payment request email to client."""
    client = receivable.client
    amount = receivable.amount
    due_date = receivable.expected_date
    days_overdue = receivable.days_overdue

    months = client_info.get("relationship_months", 6) if client_info else 6
    risk = client_info.get("risk_level", "medium") if client_info else "medium"
    tone = _relationship_tone(months, risk)
    contact = client_info.get("contact", "") if client_info else ""

    if days_overdue > 0:
        # Overdue – more urgent
        if tone == "warm_partner":
            subject = f"Friendly Reminder – Invoice #{receivable.invoice_id} Overdue by {days_overdue} Days"
            body = f"""Dear {contact or client} Team,

I hope you're doing well! I'm reaching out regarding our Invoice #{receivable.invoice_id} for ₹{amount:,.0f}, which was due on {due_date}. It appears to be {days_overdue} day(s) overdue.

Given our long-standing relationship, I'm confident this is just an oversight. Could you please process the payment at your earliest convenience or let us know if there's anything on your end we can help resolve?

Your continued partnership means a great deal to us at {BUSINESS_NAME}.

Warm regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""
        elif tone == "professional":
            subject = f"Payment Reminder – Invoice #{receivable.invoice_id} (Overdue)"
            body = f"""Dear {contact or client} Team,

This is a reminder that Invoice #{receivable.invoice_id} for ₹{amount:,.0f} is currently {days_overdue} day(s) overdue (original due date: {due_date}).

We request you to arrange payment at the earliest possible time to avoid any disruption to your orders.

Please do not hesitate to reach out if you need any clarification on the invoice.

Best regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""
        else:
            subject = f"URGENT: Overdue Payment – Invoice #{receivable.invoice_id}"
            body = f"""Dear {client} Team,

We wish to bring to your immediate attention that Invoice #{receivable.invoice_id} for ₹{amount:,.0f} is {days_overdue} day(s) overdue as of today, {TODAY}.

We request immediate settlement or a payment commitment within 48 hours. Failure to do so may require us to place future orders on hold.

Please arrange the payment urgently.

Regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""
    else:
        # Early payment incentive
        subject = f"Early Payment Request – Invoice #{receivable.invoice_id} | 3% Discount Offer"
        body = f"""Dear {contact or client} Team,

I hope this message finds you well. I'm writing regarding our Invoice #{receivable.invoice_id} for ₹{amount:,.0f}, due on {due_date}.

As part of our ongoing partnership, we'd like to offer you a **3% early payment discount** if payment is received within the next 3 business days. This translates to a saving of ₹{amount * 0.03:,.0f} for you.

Should you choose to proceed, the discounted amount would be ₹{amount * 0.97:,.0f}.

Please let us know if this works for you, and we will update the invoice accordingly.

With warm regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""

    return {
        "email_id": f"EMAIL-AR-{receivable.invoice_id}",
        "type": "receivable_collection",
        "to": client_info.get("email", f"accounts@{client.lower().replace(' ', '')}.com") if client_info else f"accounts@{client.lower().replace(' ', '')}.com",
        "subject": subject,
        "body": body.strip(),
        "priority": "HIGH" if days_overdue > 0 else "MEDIUM",
        "tone": tone
    }


def draft_payment_delay_email(payable: Payable, vendor_info: Optional[Dict] = None) -> Dict:
    """Generate payment delay request email to vendor."""
    vendor = payable.vendor
    amount = payable.amount
    due_date = payable.due_date
    flexibility = payable.flexibility

    months = vendor_info.get("relationship_duration_months", 6) if vendor_info else 6
    neg_flex = vendor_info.get("negotiation_flexibility", flexibility) if vendor_info else flexibility
    contact = vendor_info.get("contact_person", "") if vendor_info else ""
    tone = _relationship_tone(months, "low" if neg_flex == "high" else "medium")

    delay_days = 7 if flexibility in ("high", "very_high") else 5

    if tone == "warm_partner":
        subject = f"Request for Payment Extension – Invoice due {due_date}"
        body = f"""Dear {contact or vendor} Team,

I hope you're doing well. I'm writing to you regarding our upcoming payment of ₹{amount:,.0f} due on {due_date}.

Due to a temporary cash flow constraint caused by a few delayed client receivables, we would like to kindly request an extension of {delay_days} business days for this payment.

I want to assure you that this is a short-term situation, and we remain fully committed to our partnership. We will settle the full amount by {due_date} + {delay_days} days without fail.

Thank you for your understanding and continued support.

Warm regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""
    elif tone == "professional":
        subject = f"Payment Deferral Request – ₹{amount:,.0f} Due {due_date}"
        body = f"""Dear {contact or vendor} Team,

I am writing to request a brief extension on our payment of ₹{amount:,.0f} that is due on {due_date}.

We are currently experiencing a temporary delay in receiving payments from some of our clients. In light of this, we request an extension of {delay_days} days to ensure a complete and timely settlement.

We greatly value our business relationship and want to ensure transparency about our situation. Please let us know if this arrangement is acceptable.

Best regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""
    else:
        subject = f"Payment Extension Request – Invoice {due_date}"
        body = f"""Dear {vendor} Team,

This is to formally request a payment extension for our outstanding amount of ₹{amount:,.0f} due on {due_date}.

We request an extension of {delay_days} days due to unforeseen delays in client payments. We will ensure full payment by the extended date.

Please confirm your acceptance at the earliest.

Regards,
{OWNER_NAME}
{BUSINESS_NAME}
"""

    return {
        "email_id": f"EMAIL-AP-{payable.payable_id}",
        "type": "payment_delay_request",
        "to": vendor_info.get("email", f"accounts@{vendor.lower().replace(' ', '').replace('&', '')[:12]}.in") if vendor_info else f"accounts@vendor.in",
        "subject": subject,
        "body": body.strip(),
        "priority": "HIGH" if payable.type == "critical" else "MEDIUM",
        "tone": tone,
        "delay_requested_days": delay_days
    }


def generate_all_emails(
    receivables: List[Receivable],
    delayed_payables: List[Dict],
    payables: List[Payable],
    vendor_insights: List[VendorInsight],
    client_ledger: Optional[List[Dict]] = None
) -> List[Dict]:
    """Generate all relevant emails."""
    emails = []

    # Build lookup maps
    vendor_map = {v.vendor: v.dict() for v in vendor_insights}
    client_map = {}
    if client_ledger:
        for c in client_ledger:
            client_map[c.get("client", "")] = c

    # AR collection emails (overdue + due soon)
    for r in receivables:
        if r.status in ("overdue", "due_soon") or r.days_overdue > 0:
            ci = client_map.get(r.client)
            emails.append(draft_early_collection_email(r, ci))

    # AP delay emails (for delayed payables)
    delayed_ids = {d["payable_id"] for d in delayed_payables}
    for p in payables:
        if p.payable_id in delayed_ids and p.flexibility not in ("none",):
            vi = vendor_map.get(p.vendor)
            emails.append(draft_payment_delay_email(p, vi))

    return emails
