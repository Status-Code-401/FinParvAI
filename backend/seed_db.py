import os
import json
import sys

# Ensure the app is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.database import db
from app.services.data_ingestion import _days_from_today

BUSINESS_ID = 1
MOCK_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mock_data")

def seed_from_financial_state():
    path = os.path.join(MOCK_DATA_DIR, "normalized_financial_state.json")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Seeding from {path}...")
    
    # 1. Transactions
    txns = data.get("transactions", [])
    for t in txns:
        # Standardize for DB (db.upsert_transaction)
        db.upsert_transaction(BUSINESS_ID, t)
    print(f"  Seeded {len(txns)} transactions.")

    # 2. Payables
    payables = data.get("payables", [])
    for p in payables:
        db.upsert_payable(BUSINESS_ID, p)
    print(f"  Seeded {len(payables)} payables.")

    # 3. Receivables
    receivables = data.get("receivables", [])
    for r in receivables:
        db.upsert_receivable(BUSINESS_ID, r)
    print(f"  Seeded {len(receivables)} receivables.")

def seed_from_ledger():
    path = os.path.join(MOCK_DATA_DIR, "ledger_data.json")
    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Seeding from {path}...")
    
    # Active payables/receivables from ledger
    active_payables = data.get("active_payables", [])
    for p in active_payables:
        db.upsert_payable(BUSINESS_ID, p)
    
    active_receivables = data.get("active_receivables", [])
    for r in active_receivables:
        db.upsert_receivable(BUSINESS_ID, r)
    
    print(f"  Seeded {len(active_payables)} active payables and {len(active_receivables)} active receivables from ledger.")

if __name__ == "__main__":
    if not db.is_connected:
        print("Note: DB not connected. Upserts will be ignored as they only affect Supabase.")
        print("However, the dashboards will now work because of the router fix and the mock-data fallback.")
    else:
        seed_from_financial_state()
        seed_from_ledger()
        print("Seeding complete.")
