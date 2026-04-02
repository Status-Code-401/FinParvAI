from app.routers.financial import get_cash_flow
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing get_cash_flow()...")
    res = get_cash_flow()
    print("SUCCESS, keys:", res.keys())
except Exception as e:
    import traceback
    traceback.print_exc()
