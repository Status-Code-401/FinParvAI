"""
Cost Leakage Detection API Router
POST /api/leakage/detect — Detects hidden financial inefficiencies
"""
from fastapi import APIRouter
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(prefix="/api/leakage", tags=["Cost Leakage Detection"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mock_data")


@router.post("/detect")
def detect_leakage():
    """
    Scan financial data for cost leakages:
    - Duplicate payments/invoices
    - Vendor rate anomalies
    - Idle inventory capital lock
    - Receivable collection risk
    """
    from services.leakage_engine import run_leakage_engine

    try:
        from app.services.data_ingestion import _parse_normalized_state, enrich_from_ledger_dict
        from app.services.database import db

        state_dict = db.get_financial_state(1)
        state = _parse_normalized_state(state_dict)
        ledger_dict = db.get_ledger(1)
        state = enrich_from_ledger_dict(state, ledger_dict)

        # Build state dict for leakage engine
        with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
            inv_data = json.load(f)

        leak_input = {
            "transactions": [t.dict() for t in state.transactions],
            "payables": [p.dict() for p in state.payables],
            "receivables": [r.dict() for r in state.receivables],
            "inventory_status": [i.dict() for i in state.inventory_status],
            "procurement_orders": inv_data.get("procurement_orders", []),
            "vendor_insights": [v.dict() for v in state.vendor_insights],
        }

        result = run_leakage_engine(leak_input)
        return result

    except Exception as e:
        return {"error": str(e), "leakages": [], "total_leakage_amount": 0}


@router.get("/detect")
def detect_leakage_get():
    """GET version for easy browser testing."""
    return detect_leakage()
