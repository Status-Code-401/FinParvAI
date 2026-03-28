import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from app.routers.financial import _load_state

state = _load_state()
print("Software Subscriptions:", len(state.software_subscriptions))
print("Factory Status:", len(state.factory_status))
print("Transactions count:", len(state.transactions))
