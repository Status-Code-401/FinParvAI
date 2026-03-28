"""Quick test for v2 Cost Intelligence endpoints - ASCII only for Windows."""
import urllib.request
import json
import traceback
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = "http://127.0.0.1:8000"

def test_endpoint(name, url):
    print(f"\nTesting: {name} -> {url}")
    try:
        r = urllib.request.urlopen(url)
        data = json.loads(r.read())
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (str, int, float, bool)):
                    val = str(v)[:100]
                    print(f"  {k}: {val}")
                elif isinstance(v, dict):
                    print(f"  {k}: [dict with {len(v)} keys]")
                elif isinstance(v, list):
                    print(f"  {k}: [list with {len(v)} items]")
        print(f"  [PASS] {name}")
        return True
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        # Try to read error body
        if hasattr(e, 'read'):
            try:
                err_body = e.read().decode()[:500]
                print(f"  Error body: {err_body}")
            except:
                pass
        return False

results = []
results.append(test_endpoint("Health", f"{BASE}/health"))
results.append(test_endpoint("Impact", f"{BASE}/api/impact/calculate"))
results.append(test_endpoint("Leakage", f"{BASE}/api/leakage/detect"))
results.append(test_endpoint("Signals", f"{BASE}/api/signals/analyze"))
results.append(test_endpoint("Execution", f"{BASE}/api/execution/run"))
results.append(test_endpoint("Exec Logs", f"{BASE}/api/execution/logs"))
results.append(test_endpoint("Combined", f"{BASE}/api/cost-intelligence"))

print(f"\n=== Results: {sum(results)}/{len(results)} passed ===")
