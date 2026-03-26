import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_KEY not found in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def clear_db():
    print("Clearing database...")
    # List of tables to clear in order (due to FK constraints)
    tables = [
        "document_parses",
        "procurement_orders",
        "inventory_items",
        "daily_production",
        "transactions",
        "payables",
        "receivables",
        "ledger_summaries",
        "monthly_summaries",
        "clients",
        "vendors",
        "businesses"
    ]
    
    for table in tables:
        try:
            # We use a query that delete all with a dummy filter if needed or just use truncate if possible
            # But Supabase client delete usually needs a filter.
            print(f"  - Clearing {table}...")
            supabase.table(table).delete().neq("business_id", -1).execute() # dummy filter
        except Exception as e:
            # specifically for tables without business_id like businesses
            try:
                 supabase.table(table).delete().neq("id", -1).execute()
            except:
                 print(f"    Warning clearing {table}: {e}")

if __name__ == "__main__":
    clear_db()
    print("Database cleared. Now seeding...")
    # Call the original seed script
    import seed
    seed.seed()
    print("Reset and seed complete.")
