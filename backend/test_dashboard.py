import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.routers.financial import get_dashboard

try:
    print("Testing get_dashboard()...")
    res = get_dashboard()
    print("SUCCESS, keys:", res.keys())
except Exception as e:
    import traceback
    traceback.print_exc()
