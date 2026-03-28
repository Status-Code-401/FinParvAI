"""
Data Ingestion & Normalization Service
Parses CSV bank statements, JSON invoices/ledger/inventory into
a normalized FinancialState object.
"""
import json
import csv
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.financial_state import (
    FinancialState, Transaction, Payable, Receivable,
    Overhead, InventoryItem, ProcurementOrder, VendorInsight,
    LedgerSummary, Production, SoftwareSubscription, FactoryStatus
)

TODAY = datetime.now().date()


def _days_from_today(date_str: str) -> int:
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        return (d - TODAY).days
    except Exception:
        return 99


def load_normalized_state(path: str) -> FinancialState:
    """Load from normalized_financial_state.json directly."""
    with open(path) as f:
        data = json.load(f)
    return _parse_normalized_state(data)


def _parse_normalized_state(data: Dict) -> FinancialState:
    transactions = [Transaction(**t) for t in data.get("transactions", [])]

    payables = []
    for p in data.get("payables", []):
        payables.append(Payable(
            payable_id=p.get("payable_id", f"PAY-{len(payables)}"),
            vendor=p.get("vendor", ""),
            amount=p.get("amount", 0),
            due_date=p.get("due_date", ""),
            days_until_due=_days_from_today(p.get("due_date", "")),
            penalty=p.get("penalty", "none"),
            type=p.get("type", "flexible"),
            flexibility=p.get("flexibility", "medium"),
            linked_orders=p.get("linked_orders", []),
            priority_score=p.get("priority_score", 0.5),
            status=p.get("status", "unpaid"),
            description=p.get("description"),
            penalty_amount=p.get("penalty_amount", 0)
        ))

    receivables = []
    for r in data.get("receivables", []):
        days_overdue = _days_from_today(r.get("expected_date", ""))
        receivables.append(Receivable(
            invoice_id=r.get("invoice_id", ""),
            client=r.get("client", ""),
            amount=r.get("amount", 0),
            expected_date=r.get("expected_date", ""),
            collection_probability=r.get("collection_probability", 0.8),
            status=r.get("status", "upcoming"),
            days_overdue=max(0, -days_overdue) if days_overdue < 0 else r.get("days_overdue", 0),
            action_required=r.get("action_required")
        ))

    overheads = [Overhead(**o) for o in data.get("overheads", [])]

    ls = data.get("ledger_summary", {})
    ledger = LedgerSummary(
        monthly_income=ls.get("monthly_income", 0),
        monthly_expense=ls.get("monthly_expense", 0),
        avg_payment_cycle_days=ls.get("avg_payment_cycle_days", 7),
        avg_collection_days=ls.get("avg_collection_days", 9.8)
    ) if ls else None

    inv_procurement = []
    for po in data.get("inventory_procurement", []):
        inv_procurement.append(ProcurementOrder(
            order_id=po.get("order_id", ""),
            vendor=po.get("vendor", ""),
            material=po.get("material", ""),
            quantity=po.get("quantity", 0),
            unit_cost=po.get("unit_cost", 0),
            total_cost=po.get("total_cost", 0),
            order_date=po.get("order_date", ""),
            delivery_date=po.get("delivery_date"),
            lead_time=po.get("lead_time", 3),
            status=po.get("status", "pending"),
            payment_status=po.get("payment_status", "unpaid"),
            payment_due=po.get("payment_due")
        ))

    inv_status = []
    for item in data.get("inventory_status", []):
        inv_status.append(InventoryItem(
            item_id=item.get("item_id"),
            item=item.get("item", ""),
            unit=item.get("unit"),
            available_quantity=item.get("available_quantity", 0),
            required_quantity=item.get("required_quantity", 0),
            shortage=item.get("shortage", 0),
            excess=item.get("excess", 0),
            unit_cost=item.get("unit_cost"),
            total_value=item.get("total_value")
        ))

    vendor_insights = []
    for v in data.get("vendor_insights", []):
        vendor_insights.append(VendorInsight(
            vendor=v.get("vendor", ""),
            vendor_id=v.get("vendor_id"),
            total_orders=v.get("total_orders", 0),
            avg_lead_time=v.get("avg_lead_time", 3),
            payment_delay_avg=v.get("payment_delay_avg", 0),
            reliability_score=v.get("reliability_score", 0.8),
            cost_efficiency_score=v.get("cost_efficiency_score", 0.8),
            negotiation_flexibility=v.get("negotiation_flexibility", "medium"),
            contact_person=v.get("contact_person"),
            email=v.get("email"),
            phone=v.get("phone"),
            allows_credit=v.get("allows_credit", False),
            credit_limit=v.get("credit_limit", 0)
        ))

    prod_data = data.get("production", {})
    production = Production(
        daily_output=prod_data.get("daily_output", {}),
        cost_per_unit=prod_data.get("cost_per_unit", 95),
        selling_price_per_unit=prod_data.get("selling_price_per_unit", 185),
        units_this_month=prod_data.get("units_this_month"),
        monthly_target=prod_data.get("monthly_target")
    ) if prod_data else None

    software = [SoftwareSubscription(**s) for s in data.get("software_subscriptions", [])]
    factory = [FactoryStatus(**f) for f in data.get("factory_status", [])]

    return FinancialState(
        business_name=data.get("_meta", {}).get("business", "Sri Lakshmi Garments"),
        cash_balance=data.get("cash_balance", 0),
        transactions=transactions,
        payables=payables,
        receivables=receivables,
        overheads=overheads,
        ledger_summary=ledger,
        inventory_procurement=inv_procurement,
        inventory_status=inv_status,
        vendor_insights=vendor_insights,
        production=production,
        cost_breakdown=data.get("cost_breakdown"),
        software_subscriptions=software,
        factory_status=factory
    )


def parse_bank_statement_csv(content: str) -> List[Transaction]:
    """Parse CSV bank statement into Transaction objects."""
    transactions = []
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        try:
            if not row.get("date") or not row.get("description"):
                continue
            transactions.append(Transaction(
                date=row.get("date", ""),
                description=row.get("description", ""),
                debit=float(row.get("debit") or 0),
                credit=float(row.get("credit") or 0),
                balance=float(row.get("balance") or 0) if row.get("balance") else None,
                category=row.get("category")
            ))
        except Exception:
            continue
    return transactions


def parse_invoices_json(content: str) -> Dict:
    """Parse invoice JSON into payables and receivables."""
    data = json.loads(content)
    invoices = data.get("invoices", [])

    payables = []
    receivables = []

    for inv in invoices:
        if inv.get("type") == "vendor_invoice":
            days = _days_from_today(inv.get("due_date", ""))
            payables.append(Payable(
                payable_id=inv.get("invoice_id", ""),
                vendor=inv.get("vendor", ""),
                amount=inv.get("total", 0),
                due_date=inv.get("due_date", ""),
                days_until_due=days,
                penalty="high" if inv.get("penalty_on_late") else "low",
                type="critical" if inv.get("penalty_on_late") else "flexible",
                flexibility="none" if inv.get("penalty_on_late") else "medium",
                status=inv.get("status", "unpaid")
            ))
        elif inv.get("type") == "client_invoice":
            days_overdue = inv.get("days_overdue", 0)
            days_left = _days_from_today(inv.get("due_date", ""))
            receivables.append(Receivable(
                invoice_id=inv.get("invoice_id", ""),
                client=inv.get("client", ""),
                amount=inv.get("total", 0),
                expected_date=inv.get("due_date", ""),
                collection_probability=0.65 if inv.get("status") == "overdue" else 0.85,
                status=inv.get("status", "upcoming"),
                days_overdue=days_overdue
            ))

    return {"payables": payables, "receivables": receivables}


def enrich_from_ledger_dict(state: FinancialState, ledger: Dict) -> FinancialState:
    """Merge client ledger data into state for richer insights using provided dictionary."""
    try:
        # Update vendor insights from inventory data if available in ledger
        # (In our mock, ledger doesn't have inventory_procurement, but db.get_ledger might)
        
        # Note: inventory_status and vendor_insights are already handled 
        # by db.get_financial_state for Supabase mode.
        # This function is mainly for additional enrichment if needed.
        pass
    except Exception:
        pass
    return state


def enrich_from_ledger(state: FinancialState, ledger_path: str) -> FinancialState:
    """Merge client ledger data into state for richer insights."""
    try:
        with open(ledger_path) as f:
            ledger = json.load(f)
        return enrich_from_ledger_dict(state, ledger)
    except Exception:
        pass
    return state
