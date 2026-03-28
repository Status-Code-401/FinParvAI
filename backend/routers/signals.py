"""
Enterprise Signal API Router  
POST /api/signals/analyze — Analyze enterprise-grade signals
"""
from fastapi import APIRouter
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(prefix="/api/signals", tags=["Enterprise Signals"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mock_data")


@router.post("/analyze")
def analyze_signals():
    """
    Run enterprise signal analysis:
    - SLA risk detection
    - Vendor benchmarking
    - Inventory turnover signals
    - Cash velocity analysis
    """
    from services.signal_engine import run_signal_engine

    try:
        from app.services.data_ingestion import _parse_normalized_state, enrich_from_ledger_dict
        from app.services.database import db

        state_dict = db.get_financial_state(1)
        state = _parse_normalized_state(state_dict)
        ledger_dict = db.get_ledger(1)
        state = enrich_from_ledger_dict(state, ledger_dict)

        with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
            inv_data = json.load(f)

        signal_input = {
            "payables": [p.dict() for p in state.payables],
            "receivables": [r.dict() for r in state.receivables],
            "inventory_status": [i.dict() for i in state.inventory_status],
            "procurement_orders": inv_data.get("procurement_orders", []),
            "vendor_insights": [v.dict() for v in state.vendor_insights],
            "production": state.production.dict() if state.production else {},
            "ledger_summary": state.ledger_summary.dict() if state.ledger_summary else {},
        }

        result = run_signal_engine(signal_input)
        return result

    except Exception as e:
        return {"error": str(e), "signals": [], "total_signals": 0}


@router.get("/analyze")
def analyze_signals_get():
    """GET version for easy browser testing."""
    return analyze_signals()
