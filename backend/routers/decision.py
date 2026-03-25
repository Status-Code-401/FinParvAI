from fastapi import APIRouter
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import FinancialState
from services.decision_engine import run_decision_engine

router = APIRouter()

@router.post("/run")
def run_decision(state: FinancialState):
    """Run the deterministic decision engine on a financial state."""
    result = run_decision_engine(state)
    return result

@router.post("/simulate")
def simulate_cash_flow_only(state: FinancialState, days: int = 14):
    """Simulate cash flow for a given number of days."""
    from services.decision_engine import simulate_cash_flow, runway_days
    projection = simulate_cash_flow(state, days=days)
    safe, runway = runway_days(projection)
    return {
        "is_safe": safe,
        "runway_days": runway,
        "projection": [p.dict() for p in projection],
    }

@router.post("/score-payables")
def score_payables(state: FinancialState):
    """Score and rank payables by priority."""
    from services.decision_engine import score_payable
    scored = []
    for p in (state.payables or []):
        score = score_payable(p)
        scored.append({"vendor": p.vendor, "amount": p.amount, "due_date": p.due_date, "score": score})
    scored.sort(key=lambda x: -x["score"])
    return {"scored_payables": scored}
