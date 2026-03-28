"""
Cost Impact API Router
POST /api/impact/calculate — Quantifies financial benefit of every action
"""
from fastapi import APIRouter
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(prefix="/api/impact", tags=["Cost Impact Engine"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mock_data")


def _load_state_for_impact():
    """Load state using the app-level data ingestion (same as financial router)."""
    try:
        from app.services.data_ingestion import load_normalized_state, _parse_normalized_state, enrich_from_ledger_dict
        from app.services.database import db
        state_dict = db.get_financial_state(1)
        state = _parse_normalized_state(state_dict)
        ledger_dict = db.get_ledger(1)
        state = enrich_from_ledger_dict(state, ledger_dict)
        return state, ledger_dict
    except Exception as e:
        print(f"Impact router fallback: {e}")
        with open(os.path.join(MOCK_DATA_DIR, "normalized_financial_state.json")) as f:
            return json.load(f), {}


@router.post("/calculate")
def calculate_impact():
    """
    Run the decision engine, then quantify the impact of every action.
    Returns actions enriched with ₹ impact amounts + confidence scores.
    """
    from services.impact_engine import run_impact_engine

    try:
        from app.services.decision_engine import run_engine
        from app.services.data_ingestion import _parse_normalized_state, enrich_from_ledger_dict
        from app.services.database import db

        state_dict = db.get_financial_state(1)
        state = _parse_normalized_state(state_dict)
        ledger_dict = db.get_ledger(1)
        state = enrich_from_ledger_dict(state, ledger_dict)

        # Run existing decision engine
        result = run_engine(state)
        actions = result.get("actions", {}).get("actions", [])

        # Build context
        state_context = {
            "cash_balance": state.cash_balance,
            "shortfall": result.get("shortfall", {}).get("gap", 0),
            "inventory_status": [i.dict() for i in state.inventory_status],
        }

        # Run impact engine
        impact_result = run_impact_engine(state_context, actions)
        return impact_result

    except Exception as e:
        return {"error": str(e), "actions_with_impact": [], "total_potential_savings": 0}


@router.get("/calculate")
def calculate_impact_get():
    """GET version for easy browser testing."""
    return calculate_impact()
