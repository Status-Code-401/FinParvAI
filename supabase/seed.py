"""
FinParvai — Supabase Seed Script
=================================
Seeds all mock data from mock_data/ into Supabase.

Usage:
    cd e:\\finparvai\\backend
    venv\\Scripts\\python ..\\supabase\\seed.py

Requirements:
    - SUPABASE_URL and SUPABASE_ANON_KEY set in backend/.env
    - supabase-py installed  (pip install supabase)
"""

import os
import sys
import json

# ── Make sure backend packages are importable ─────────────────────────────────
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
# Seed needs the service role key (bypasses RLS).
# Get it from: Supabase Dashboard → Settings → API → service_role key
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ["SUPABASE_ANON_KEY"]

if "service" not in SUPABASE_KEY and len(SUPABASE_KEY) < 200:
    print("⚠️  Using anon key — RLS may block writes.")
    print("   Set SUPABASE_SERVICE_KEY in backend/.env for full access.\n")
MOCK_DIR     = os.path.join(os.path.dirname(__file__), "..", "mock_data")

client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUSINESS_ID = 1   # single-tenant — all rows belong to business 1


def load(filename: str):
    with open(os.path.join(MOCK_DIR, filename)) as f:
        return json.load(f)


def upsert(table: str, rows: list, conflict_col: str | None = None):
    if not rows:
        return
    try:
        if conflict_col:
            client.table(table).upsert(rows, on_conflict=conflict_col).execute()
        else:
            client.table(table).upsert(rows).execute()
        print(f"  ✓  {table}: {len(rows)} row(s)")
    except Exception as exc:
        print(f"  ✗  {table}: {exc}")


def seed():
    ledger = load("ledger_data.json")
    inv    = load("inventory_procurement.json")
    norm   = load("normalized_financial_state.json")

    # ── 1. Business ───────────────────────────────────────────────────────────
    bp = ledger["business_profile"]
    ls = ledger["ledger_summary"]
    pd = ledger["production_data"]
    upsert("businesses", [{
        "id":                     BUSINESS_ID,
        "name":                   bp.get("name", "Sri Lakshmi Garments"),
        "owner":                  bp.get("owner"),
        "gstin":                  bp.get("gstin"),
        "industry":               bp.get("industry"),
        "location":               bp.get("location"),
        "established":            bp.get("established"),
        "cash_balance":           ls.get("current_cash_balance", 45000),
        "cost_per_unit":          pd.get("cost_per_unit", 95),
        "selling_price_per_unit": pd.get("selling_price_per_unit", 185),
        "monthly_target":         pd.get("target_monthly_units", 2200),
        # New: cost_breakdown and production estimates
        "internal_monthly_obligation": norm.get("cost_breakdown", {}).get("internal_monthly", 0),
        "external_monthly_obligation": norm.get("cost_breakdown", {}).get("external_monthly", 0),
        "total_monthly_obligation":    norm.get("cost_breakdown", {}).get("total_monthly_obligations", 0),
        "production_avg_per_day":      norm.get("production", {}).get("daily_output", {}).get("avg_per_day", 0),
        "production_yesterday":        norm.get("production", {}).get("daily_output", {}).get("yesterday", 0),
        "production_today_estimate":   norm.get("production", {}).get("daily_output", {}).get("today_estimate", 0),
    }], conflict_col="id")

    # ── 2. Ledger summary ─────────────────────────────────────────────────────
    upsert("ledger_summaries", [{
        "business_id":            BUSINESS_ID,
        "period":                 ls.get("period"),
        "total_income":           ls.get("total_income", 0),
        "total_expense":          ls.get("total_expense", 0),
        "net_profit":             ls.get("net_profit", 0),
        "monthly_avg_income":     ls.get("monthly_avg_income", 0),
        "monthly_avg_expense":    ls.get("monthly_avg_expense", 0),
        "monthly_income":         ls.get("monthly_avg_income", 0),
        "monthly_expense":        ls.get("monthly_avg_expense", 0),
        "avg_payment_cycle_days": ls.get("avg_payment_cycle_days", 7),
        "avg_collection_days":    9.8,
    }])

    # ── 3. Monthly summaries ──────────────────────────────────────────────────
    monthly = [
        {**m, "business_id": BUSINESS_ID}
        for m in ledger.get("monthly_summary", [])
    ]
    upsert("monthly_summaries", monthly, conflict_col="business_id,month")

    # ── 4. Full Transactions (from CSV) ───────────────────────────────────────
    import csv
    txns = []
    try:
        csv_path = os.path.join(MOCK_DIR, "bank_statement.csv")
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                txns.append({
                    "business_id": BUSINESS_ID,
                    "date":        row.get("Date") or row.get("date"),
                    "description": row.get("Description") or row.get("description"),
                    "debit":       float(row.get("Debit") or 0) if (row.get("Debit") and row.get("Debit") != '0') else 0,
                    "credit":      float(row.get("Credit") or 0) if (row.get("Credit") and row.get("Credit") != '0') else 0,
                    "balance":     float(row.get("Balance") or 0) if row.get("Balance") else None,
                    "category":    row.get("Category"),
                    "type":        row.get("Type", "transaction"),
                })
        upsert("transactions", txns)
    except Exception as e:
        print(f"  ✗  CSV Transactions: {e}")

    # ── 5. Clients (client_ledger) — including full payment_history ──────────
    clients = [
        {**c, "business_id": BUSINESS_ID}
        for c in ledger.get("client_ledger", [])
    ]
    upsert("clients", clients, conflict_col="business_id,client_id")

    # ── 6. Active Receivables (from invoices.json) ──────────────────────────
    try:
        raw_invoices = load("invoices.json")
        receivables_list = []
        # Filter for only unpaid or recently paid ones
        for inv_doc in raw_invoices:
             receivables_list.append({
                "business_id": BUSINESS_ID,
                "invoice_id":  inv_doc.get("invoice_id"),
                "client":      inv_doc.get("client"),
                "amount":      inv_doc.get("amount"),
                "invoice_date":inv_doc.get("date"),
                "due_date":    inv_doc.get("due_date"),
                "status":      inv_doc.get("status"),
                "collection_probability": 0.9 if inv_doc.get("status") == "paid" else 0.7
            })
        upsert("receivables", receivables_list, conflict_col="business_id,invoice_id")
    except:
        # fallback to ledger file if invoices.json fails
        receivables = [
            {**r, "business_id": BUSINESS_ID}
            for r in ledger.get("active_receivables", [])
        ]
        upsert("receivables", receivables, conflict_col="business_id,invoice_id")

    # ── 7. Active payables — now including linked_orders ARRAY! ───────────────
    payables = [
        {**p, "business_id": BUSINESS_ID}
        for p in ledger.get("active_payables", [])
    ]
    upsert("payables", payables, conflict_col="business_id,payable_id")

    # ── 8. Overheads ──────────────────────────────────────────────────────────
    overheads = [
        {**o, "business_id": BUSINESS_ID}
        for o in ledger.get("overheads", [])
    ]
    upsert("overheads", overheads, conflict_col="business_id,type")

    # ── 9. Daily production ───────────────────────────────────────────────────
    prod_dict = pd.get("daily_production", {})
    prod_rows = [
        {"business_id": BUSINESS_ID, "date": date, "units": units}
        for date, units in prod_dict.items()
    ]
    upsert("daily_production", prod_rows, conflict_col="business_id,date")

    # ── 10. Vendors ───────────────────────────────────────────────────────────
    vendors = [
        {**v, "business_id": BUSINESS_ID}
        for v in inv.get("vendor_insights", [])
    ]
    upsert("vendors", vendors, conflict_col="business_id,vendor_id")

    # ── 11. Inventory items ───────────────────────────────────────────────────
    items = [
        {**i, "business_id": BUSINESS_ID}
        for i in inv.get("inventory_status", [])
    ]
    upsert("inventory_items", items, conflict_col="business_id,item_id")

    # ── 12. Procurement orders ────────────────────────────────────────────────
    orders = [
        {**o, "business_id": BUSINESS_ID}
        for o in inv.get("procurement_orders", [])
    ]
    upsert("procurement_orders", orders, conflict_col="business_id,order_id")

    # ── 13. Collection predictions ────────────────────────────────────────────
    preds = ledger.get("payment_cycle_analysis", {}).get(
        "predicted_collections_next_30_days", []
    )
    pred_rows = [
        {
            "business_id":  BUSINESS_ID,
            "client":       p.get("client"),
            "amount":       p.get("amount"),
            "expected_date":p.get("expected_date"),
            "probability":  p.get("probability"),
        }
        for p in preds
    ]
    upsert("collection_predictions", pred_rows)

    print("\n✅  Seed complete!")


if __name__ == "__main__":
    print("🌱  Seeding FinParvai data into Supabase…\n")
    seed()
