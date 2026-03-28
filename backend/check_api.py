import urllib.request
import json
try:
    with urllib.request.urlopen("http://localhost:8000/api/cost-intelligence") as response:
        data = json.loads(response.read().decode())
        
        # Check executions
        registered = data.get("execution", {}).get("registered_actions", [])
        print("Total registered actions:", len(registered))
        found_zoom = any("Zoom" in r.get("action", "") or "Zoom" in r.get("description", "") for r in registered)
        print("Zoom found in actions?", found_zoom)
        
        # Check leakages
        leakages = data.get("leakage", {}).get("leakages", [])
        print("Total leakages:", len(leakages))
        found_zoom_leak = any("Zoom" in l.get("description", "") for l in leakages)
        print("Zoom found in leakages?", found_zoom_leak)
        
        # Check signals for SLA
        signals = data.get("signals", {}).get("signals", [])
        print("Total signals:", len(signals))
        found_factory = any("Line B" in s.get("description", "") for s in signals)
        print("Line B Factory found in signals?", found_factory)

except Exception as e:
    print("Error:", e)
