import json
import os

path = os.path.join(os.path.dirname(__file__), "..", "mock_data", "normalized_financial_state.json")

with open(path, "r", encoding='utf-8') as f:
    data = json.load(f)

# 1. Add Software Subscriptions
data["software_subscriptions"] = [
    {
        "tool_name": "Zoom Pro",
        "category": "Communications",
        "monthly_cost": 1500,
        "utilization_percent": 0,
        "active": True,
        "renewal_date": "2026-04-10"
    },
    {
        "tool_name": "Microsoft Teams (Enterprise)",
        "category": "Communications",
        "monthly_cost": 4500,
        "utilization_percent": 85,
        "active": True,
        "renewal_date": "2026-04-15"
    },
    {
        "tool_name": "AWS EC2 Test Environment",
        "category": "Cloud Infrastructure",
        "monthly_cost": 3200,
        "utilization_percent": 0,
        "active": True,
        "renewal_date": "2026-03-30"
    }
]

# 2. Add Factory Status
data["factory_status"] = [
    {
        "line_name": "Line A (Cotton Standard)",
        "status": "active",
        "current_product": "T-Shirts Basic",
        "delay_days": 0,
        "idle_penalty_per_day": 0
    },
    {
        "line_name": "Line B (Premium Dyes)",
        "status": "warning",
        "current_product": "Premium Hoodies",
        "delay_days": 3,
        "idle_penalty_per_day": 12500
    }
]

# 3. Add a Reconciliation Variance (Bank says X, Receivable says Y)
# We find a settled transaction or just append an explicit settled invoice
data["receivables"].append({
    "invoice_id": "INV-2045",
    "client": "Metro Retailers",
    "amount": 50000,
    "expected_date": "2026-03-24",
    "collection_probability": 1.0,
    "status": "paid",
    "days_overdue": 0
})

data["transactions"].append({
    "date": "2026-03-25T10:00:00Z",
    "description": "NEFT - Metro Retailers Settlemnt",
    "debit": 0,
    "credit": 48500,  # 1500 missing!
    "balance": 2048500,
    "category": "income",
    "type": "transfer"
})

with open(path, "w", encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Successfully injected mock edge cases into normalized_financial_state.json")
