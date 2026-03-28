"""
Autonomous Execution API Router
POST /api/execution/run — Register and manage action execution
POST /api/execution/approve — Approve a pending action
POST /api/execution/execute — Execute a specific action
POST /api/execution/auto-toggle — Toggle auto-execution
GET  /api/execution/logs — Get audit trail
GET  /api/execution/pending — Get pending actions
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

router = APIRouter(prefix="/api/execution", tags=["Autonomous Execution"])

MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "mock_data")


class ActionIdRequest(BaseModel):
    action_id: str
    reason: Optional[str] = ""


class AutoToggleRequest(BaseModel):
    enabled: bool
    threshold: Optional[float] = 0.85


@router.post("/run")
def run_execution():
    """
    Run the full pipeline: Decision Engine → Impact Engine → Execution Engine.
    Registers all actions for approval/auto-execution.
    """
    from services.impact_engine import run_impact_engine
    from services.execution_engine import run_execution_engine

    try:
        from app.services.decision_engine import run_engine
        from app.services.data_ingestion import _parse_normalized_state, enrich_from_ledger_dict
        from app.services.database import db

        state_dict = db.get_financial_state(1)
        state = _parse_normalized_state(state_dict)
        ledger_dict = db.get_ledger(1)
        state = enrich_from_ledger_dict(state, ledger_dict)

        # Decision engine
        result = run_engine(state)
        actions = result.get("actions", {}).get("actions", [])

        # Impact engine
        state_context = {
            "cash_balance": state.cash_balance,
            "shortfall": result.get("shortfall", {}).get("gap", 0),
            "inventory_status": [i.dict() for i in state.inventory_status],
        }
        impact_result = run_impact_engine(state_context, actions)

        # Execution engine
        exec_result = run_execution_engine(impact_result.get("actions_with_impact", []))

        return exec_result

    except Exception as e:
        return {"error": str(e), "registered_actions": [], "total_actions": 0}


@router.get("/run")
def run_execution_get():
    """GET version for browser testing."""
    return run_execution()


@router.post("/approve")
def approve(req: ActionIdRequest):
    """Approve a pending action."""
    from services.execution_engine import approve_action
    return approve_action(req.action_id)


@router.post("/execute")
def execute(req: ActionIdRequest):
    """Execute a specific action (approved or pending)."""
    from services.execution_engine import execute_action
    return execute_action(req.action_id)


@router.post("/reject")
def reject(req: ActionIdRequest):
    """Reject a pending action."""
    from services.execution_engine import reject_action
    return reject_action(req.action_id, req.reason)


@router.post("/auto-toggle")
def auto_toggle(req: AutoToggleRequest):
    """Toggle auto-execution on/off."""
    from services.execution_engine import set_auto_execute
    return set_auto_execute(req.enabled, req.threshold)


@router.get("/logs")
def get_logs(limit: int = 50):
    """Get the execution audit trail."""
    from services.execution_engine import get_execution_logs
    logs = get_execution_logs(limit)
    return {"logs": logs, "total": len(logs)}


@router.get("/pending")
def get_pending():
    """Get all actions awaiting approval."""
    from services.execution_engine import get_pending_actions
    pending = get_pending_actions()
    return {"pending": pending, "total": len(pending)}


@router.get("/all")
def get_all():
    """Get all registered actions."""
    from services.execution_engine import get_all_actions
    actions = get_all_actions()
    return {"actions": actions, "total": len(actions)}
