import requests

endpoints = [
    "/api/dashboard",
    "/api/cash-flow?days=14",
    "/api/analyze",
    "/api/recommendations",
    "/api/payables",
    "/api/receivables",
    "/api/vendors",
    "/api/inventory",
    "/api/forecast",
    "/api/ledger",
    "/api/transactions",
    "/api/financial-state",
    "/api/calendar"
]

for ep in endpoints:
    print(f"Testing {ep}...")
    try:
        r = requests.get(f"http://localhost:8000{ep}")
        if r.status_code != 200:
            print(f"FAILED {ep}: {r.status_code}")
            print(r.text)
        else:
            print("OK")
    except Exception as e:
        print(f"EXCEPTION {ep}: {e}")
