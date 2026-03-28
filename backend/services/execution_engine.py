"""
Autonomous Execution Layer (Module 3)
Moves FinParvai from recommendation → action execution.
Supports approval workflows, auto-execution, and audit logging.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ─── In-Memory Stores (Mock persistent layer) ────────────────────────────────
# In production these would be database tables.
_execution_log: List[Dict] = []
_pending_actions: Dict[str, Dict] = {}
_auto_execute_enabled: bool = False
_auto_execute_threshold: float = 0.85


def _generate_action_id() -> str:
    return f"EXEC-{uuid.uuid4().hex[:8].upper()}"


def _now_iso() -> str:
    return datetime.now().isoformat()


# ─── Action Registration ─────────────────────────────────────────────────────

def register_action(action: Dict, confidence: float = 0.75) -> Dict:
    """
    Register an action for approval/execution.
    Returns the action with an execution ID and status.
    """
    action_id = _generate_action_id()

    execution_record = {
        "action_id": action_id,
        "action": action.get("action", "Unknown action"),
        "type": action.get("type", "unknown"),
        "vendor": action.get("vendor", ""),
        "client": action.get("client", ""),
        "amount": action.get("amount", 0),
        "impact": action.get("impact", {}),
        "confidence": confidence,
        "status": "pending",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "executed_at": None,
        "execution_result": None,
        "auto_eligible": confidence >= _auto_execute_threshold,
    }

    _pending_actions[action_id] = execution_record
    return execution_record


# ─── Approval System ─────────────────────────────────────────────────────────

def approve_action(action_id: str) -> Dict:
    """
    FR1: Action Approval System
    Approve a pending action.
    """
    if action_id not in _pending_actions:
        return {"error": f"Action {action_id} not found", "success": False}

    action = _pending_actions[action_id]
    if action["status"] != "pending":
        return {"error": f"Action {action_id} is already {action['status']}", "success": False}

    action["status"] = "approved"
    action["updated_at"] = _now_iso()

    return {"success": True, "action_id": action_id, "status": "approved"}


def reject_action(action_id: str, reason: str = "") -> Dict:
    """Reject a pending action."""
    if action_id not in _pending_actions:
        return {"error": f"Action {action_id} not found", "success": False}

    action = _pending_actions[action_id]
    action["status"] = "rejected"
    action["updated_at"] = _now_iso()
    action["execution_result"] = {"reason": reason}

    _log_execution(action, "rejected", reason)

    return {"success": True, "action_id": action_id, "status": "rejected"}


# ─── Execution Engine ────────────────────────────────────────────────────────

def execute_action(action_id: str) -> Dict:
    """
    FR3: Execute a specific action.
    Simulates execution based on action type.
    """
    if action_id not in _pending_actions:
        return {"error": f"Action {action_id} not found", "success": False}

    action = _pending_actions[action_id]
    if action["status"] not in ("pending", "approved"):
        return {"error": f"Action {action_id} cannot be executed (status: {action['status']})", "success": False}

    # Simulate execution based on type
    execution_result = _simulate_execution(action)

    action["status"] = "executed"
    action["executed_at"] = _now_iso()
    action["updated_at"] = _now_iso()
    action["execution_result"] = execution_result

    _log_execution(action, "executed", execution_result.get("message", ""))

    return {
        "success": True,
        "action_id": action_id,
        "status": "executed",
        "result": execution_result
    }


def _simulate_execution(action: Dict) -> Dict:
    """
    FR3: Execution Types
    Simulates different execution types:
    - Delay Payment → Send email + update schedule
    - Collect Receivable → Send incentive email
    - Cut Overhead → Flag + simulate reduction
    """
    action_type = action.get("type", "")
    action_text = action.get("action", "")
    vendor = action.get("vendor", "")
    client = action.get("client", "")
    amount = action.get("amount", 0)

    if action_type in ("negotiate_delay", "delay_payment"):
        return {
            "execution_type": "payment_delay",
            "message": f"✅ Payment delay email sent to {vendor}. Schedule updated with 7-day extension.",
            "email_sent": True,
            "recipient": vendor,
            "email_subject": f"Payment Extension Request – {vendor}",
            "schedule_updated": True,
            "new_due_date": "Extended by 7 days",
            "timestamp": _now_iso()
        }

    elif action_type in ("early_collection", "pull_receivable"):
        return {
            "execution_type": "receivable_collection",
            "message": f"✅ Early payment incentive email sent to {client}. 5% discount offered for payment within 3 days.",
            "email_sent": True,
            "recipient": client,
            "email_subject": f"Early Payment Incentive – 5% Discount",
            "incentive_offered": "5% early payment discount",
            "timestamp": _now_iso()
        }

    elif action_type in ("cost_reduction", "cut_overhead"):
        return {
            "execution_type": "overhead_cut",
            "message": f"✅ Overhead flagged for reduction. {action_text}. Budget updated.",
            "flagged": True,
            "budget_updated": True,
            "simulation": f"Projected monthly savings: ₹{amount:,.0f}",
            "timestamp": _now_iso()
        }

    elif action_type in ("payment", "pay_now"):
        return {
            "execution_type": "immediate_payment",
            "message": f"✅ Payment of ₹{amount:,.0f} to {vendor} processed. Reference ID generated.",
            "payment_processed": True,
            "reference_id": f"PAY-{uuid.uuid4().hex[:6].upper()}",
            "amount": amount,
            "vendor": vendor,
            "timestamp": _now_iso()
        }

    elif action_type in ("partial_payment",):
        return {
            "execution_type": "partial_payment",
            "message": f"✅ Partial payment processed to {vendor}. Remainder rescheduled.",
            "payment_processed": True,
            "amount_paid": action.get("amount_paid", amount),
            "remainder_scheduled": True,
            "timestamp": _now_iso()
        }

    elif action_type in ("inventory_action",):
        return {
            "execution_type": "inventory_liquidation",
            "message": f"✅ Inventory liquidation initiated. {action_text}.",
            "liquidation_initiated": True,
            "estimated_recovery": amount,
            "timestamp": _now_iso()
        }

    else:
        return {
            "execution_type": "generic",
            "message": f"✅ Action executed: {action_text}",
            "timestamp": _now_iso()
        }


# ─── Auto-Execution ──────────────────────────────────────────────────────────

def auto_execute_eligible(actions: List[Dict]) -> Dict:
    """
    FR2: Auto-execution for high-confidence actions.
    if confidence > 0.85: auto_execute = True
    """
    global _auto_execute_enabled

    auto_executed = []
    skipped = []

    for action_id, action in _pending_actions.items():
        if action["status"] == "pending" and action["auto_eligible"]:
            if _auto_execute_enabled:
                result = execute_action(action_id)
                if result.get("success"):
                    auto_executed.append(result)
            else:
                skipped.append({
                    "action_id": action_id,
                    "action": action["action"],
                    "confidence": action["confidence"],
                    "reason": "Auto-execute is disabled"
                })

    return {
        "auto_executed": auto_executed,
        "skipped": skipped,
        "auto_execute_enabled": _auto_execute_enabled,
        "threshold": _auto_execute_threshold
    }


def set_auto_execute(enabled: bool, threshold: float = 0.85) -> Dict:
    """Toggle auto-execution on/off."""
    global _auto_execute_enabled, _auto_execute_threshold
    _auto_execute_enabled = enabled
    _auto_execute_threshold = threshold
    return {
        "auto_execute_enabled": _auto_execute_enabled,
        "threshold": _auto_execute_threshold
    }


# ─── Audit Log ────────────────────────────────────────────────────────────────

def _log_execution(action: Dict, status: str, details: str = ""):
    """FR4: Audit Log"""
    _execution_log.append({
        "action_id": action.get("action_id", ""),
        "action": action.get("action", ""),
        "type": action.get("type", ""),
        "amount": action.get("amount", 0),
        "status": status,
        "timestamp": _now_iso(),
        "details": details,
        "impact": action.get("impact", {})
    })


def get_execution_logs(limit: int = 50) -> List[Dict]:
    """Get audit trail of all executions."""
    return sorted(_execution_log, key=lambda x: x["timestamp"], reverse=True)[:limit]


def get_pending_actions() -> List[Dict]:
    """Get all pending actions awaiting approval."""
    return [a for a in _pending_actions.values() if a["status"] == "pending"]


def get_all_actions() -> List[Dict]:
    """Get all registered actions regardless of status."""
    return list(_pending_actions.values())


# ─── Master Execution Runner ─────────────────────────────────────────────────

def run_execution_engine(actions_with_impact: List[Dict]) -> Dict:
    """
    Main entry point. Takes actions (already enriched with impact from M1),
    registers them for approval/execution, and returns the execution state.
    """
    # Clear previous pending actions for fresh run
    _pending_actions.clear()

    registered = []
    for action in actions_with_impact:
        confidence = action.get("impact", {}).get("confidence", 0.75)
        record = register_action(action, confidence)
        registered.append(record)

    # Categorize
    auto_eligible = [r for r in registered if r["auto_eligible"]]
    manual_review = [r for r in registered if not r["auto_eligible"]]

    return {
        "registered_actions": registered,
        "total_actions": len(registered),
        "auto_eligible_count": len(auto_eligible),
        "manual_review_count": len(manual_review),
        "auto_eligible": auto_eligible,
        "manual_review": manual_review,
        "auto_execute_enabled": _auto_execute_enabled,
        "auto_execute_threshold": _auto_execute_threshold,
        "execution_logs": get_execution_logs(10),
        "summary": f"{len(registered)} actions registered. "
                   f"{len(auto_eligible)} eligible for auto-execution (confidence ≥ {_auto_execute_threshold}). "
                   f"{len(manual_review)} require manual approval."
    }
