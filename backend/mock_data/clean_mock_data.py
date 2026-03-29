import json
import os

MOCK_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_data")

def clean_file(filename: str, unique_keys: list):
    path = os.path.join(MOCK_DIR, filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    print(f"Cleaning {filename}...")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Determine if it's a list or a nested dict
    if isinstance(data, list):
        items = data
        original_count = len(items)
        seen = set()
        cleaned = []
        for item in items:
            key = tuple(item.get(k) for k in unique_keys)
            if key not in seen:
                seen.add(key)
                cleaned.append(item)
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cleaned, f, indent=4, ensure_ascii=False)
        print(f"  {filename}: Reduced from {original_count} to {len(cleaned)} items.")
    elif isinstance(data, dict):
        for key_in_dict, items in data.items():
            if isinstance(items, list) and items:
                original_count = len(items)
                seen = set()
                cleaned = []
                for item in items:
                    # Some items might be strings or simple values
                    if not isinstance(item, dict):
                         cleaned.append(item)
                         continue
                    key = tuple(item.get(k) for k in unique_keys if k in item)
                    if not key: # fallback
                         cleaned.append(item)
                         continue
                    if key not in seen:
                        seen.add(key)
                        cleaned.append(item)
                data[key_in_dict] = cleaned
                print(f"  {filename} > {key_in_dict}: Reduced from {original_count} to {len(cleaned)} items.")
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    # Remove redundancies from main state files
    # Deduplicate by vendor/client and amount to remove redundant mock entries
    clean_file("normalized_financial_state.json", ["vendor", "client", "amount"])
    clean_file("ledger_data.json", ["vendor", "client", "amount"])
    clean_file("invoices.json", ["vendor", "client", "amount"])
