from fastapi import APIRouter
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import FinancialState
from services.decision_engine import run_decision_engine
from services.action_service import generate_action_plan

router = APIRouter()

@router.post("/generate")
def generate_actions(state: FinancialState):
    """Run decision engine and generate full action plan with emails and payment schedule."""
    decision = run_decision_engine(state)
    action_plan = generate_action_plan(decision, state)
    return {
        "decision_summary": {
            "risk_level":     decision.risk_level,
            "runway_days":    decision.runway_days,
            "is_safe":        decision.is_safe,
            "confidence":     decision.confidence_score,
            "explanation":    decision.explanation,
        },
        "action_plan": action_plan.dict(),
    }
