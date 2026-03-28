"""Debug the combined cost-intelligence endpoint step by step."""
import sys, os, json, traceback
sys.path.insert(0, os.path.dirname(__file__))

from app.services.data_ingestion import _parse_normalized_state, enrich_from_ledger_dict
from app.services.database import db
from app.services.decision_engine import run_engine

print("Step 1: Loading state...")
state_dict = db.get_financial_state(1)
state = _parse_normalized_state(state_dict)
ledger_dict = db.get_ledger(1)
state = enrich_from_ledger_dict(state, ledger_dict)
print(f"  Cash: {state.cash_balance}, Payables: {len(state.payables)}, Receivables: {len(state.receivables)}")

print("\nStep 2: Running decision engine...")
result = run_engine(state)
print(f"  Risk: {result.get('risk_level')}, Actions: {len(result.get('actions', {}).get('actions', []))}")

print("\nStep 3: Loading inventory data...")
MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_data")
with open(os.path.join(MOCK_DATA_DIR, "inventory_procurement.json")) as f:
    inv_data = json.load(f)
print(f"  Procurement orders: {len(inv_data.get('procurement_orders', []))}")

print("\nStep 4: Running Impact Engine...")
from services.impact_engine import run_impact_engine
actions = result.get("actions", {}).get("actions", [])
state_context = {
    "cash_balance": state.cash_balance,
    "shortfall": result.get("shortfall", {}).get("gap", 0),
    "inventory_status": [i.dict() for i in state.inventory_status],
}
impact_result = run_impact_engine(state_context, actions)
print(f"  Total savings: {impact_result.get('total_potential_savings')}")

print("\nStep 5: Running Leakage Engine...")
from services.leakage_engine import run_leakage_engine
leak_input = {
    "transactions": [t.dict() for t in state.transactions],
    "payables": [p.dict() for p in state.payables],
    "receivables": [r.dict() for r in state.receivables],
    "inventory_status": [i.dict() for i in state.inventory_status],
    "procurement_orders": inv_data.get("procurement_orders", []),
    "vendor_insights": [v.dict() for v in state.vendor_insights],
}
try:
    leakage_result = run_leakage_engine(leak_input)
    print(f"  Leakages: {leakage_result.get('leakage_count')}")
except Exception as e:
    print(f"  LEAKAGE FAILED: {e}")
    traceback.print_exc()

print("\nStep 6: Running Signal Engine...")
from services.signal_engine import run_signal_engine
signal_input = {
    "payables": [p.dict() for p in state.payables],
    "receivables": [r.dict() for r in state.receivables],
    "inventory_status": [i.dict() for i in state.inventory_status],
    "procurement_orders": inv_data.get("procurement_orders", []),
    "vendor_insights": [v.dict() for v in state.vendor_insights],
    "production": state.production.dict() if state.production else {},
    "ledger_summary": state.ledger_summary.dict() if state.ledger_summary else {},
}
try:
    signal_result = run_signal_engine(signal_input)
    print(f"  Signals: {signal_result.get('total_signals')}")
except Exception as e:
    print(f"  SIGNAL FAILED: {e}")
    traceback.print_exc()

print("\nStep 7: Running Execution Engine...")
from services.execution_engine import run_execution_engine
try:
    exec_result = run_execution_engine(impact_result.get("actions_with_impact", []))
    print(f"  Actions registered: {exec_result.get('total_actions')}")
except Exception as e:
    print(f"  EXECUTION FAILED: {e}")
    traceback.print_exc()

print("\nAll steps completed!")
