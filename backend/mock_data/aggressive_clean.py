import json
import os
import re

MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_data")

def clean_data(data):
    if isinstance(data, list):
        seen = set()
        cleaned = []
        for item in data:
            if not isinstance(item, dict):
                cleaned.append(item)
                continue
            
            # Create a more robust key to catch near-duplicates
            # Normalize description (remove weird chars)
            desc = str(item.get("description", "")).lower()
            desc = re.sub(r'[^a-z0-9]', '', desc)
            
            # Key: date + normalized desc + amount
            # If it's a transaction, amount could be credit or debit
            amount = float(item.get("amount", item.get("debit", 0.0) + item.get("credit", 0.0)))
            key = (item.get("date"), desc, round(amount, 2))
            
            if key not in seen:
                seen.add(key)
                cleaned.append(item)
        return cleaned
    return data

def process_file(filename):
    path = os.path.join(MOCK_DIR, filename)
    if not os.path.exists(path):
        return
    
    print(f"Aggressive cleaning: {filename}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    if isinstance(data, dict):
        for k in ["transactions", "payables", "receivables", "active_payables", "active_receivables"]:
            if k in data:
                print(f"  Processing key: {k}")
                data[k] = clean_data(data[k])
    else:
        data = clean_data(data)
        
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    process_file("normalized_financial_state.json")
    process_file("ledger_data.json")
    process_file("invoices.json")
