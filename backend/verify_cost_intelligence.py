"""Verification script for the combined Cost Intelligence endpoint."""
import urllib.request
import json
import sys
import time

# Ensure UTF-8 output for Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = f"{BASE_URL}/api/cost-intelligence"

def check_cost_intelligence():
    print(f"\n[INFO] Checking Cost Intelligence Endpoint: {ENDPOINT}")
    
    try:
        # Fetch the data
        response = urllib.request.urlopen(ENDPOINT)
        data = json.loads(response.read().decode())
        
        print(f"[SUCCESS] Received successful response (200 OK)")
        
        # 1. Verify Top-Level Modules
        required_modules = ["impact", "leakage", "signals", "execution", "combined_summary"]
        print("\n--- Verifying Top-Level Modules ---")
        for module in required_modules:
            if module in data:
                print(f"  [PASS] Module '{module}' found")
            else:
                print(f"  [FAIL] Module '{module}' MISSING!")
        
        # 2. Verify Combined Summary Metrics
        required_summary_metrics = [
            "total_potential_savings",
            "total_leakage_detected",
            "total_signal_impact",
            "grand_total_financial_impact",
            "actions_count",
            "leakages_count",
            "signals_count",
            "execution_ready_count"
        ]
        
        summary = data.get("combined_summary", {})
        print("\n--- Verifying Combined Summary Metrics ---")
        for metric in required_summary_metrics:
            if metric in summary:
                val = summary[metric]
                print(f"  [PASS] Metric '{metric}': {val}")
            else:
                print(f"  [FAIL] Metric '{metric}' MISSING from summary!")
        
        # 3. Verify Module Details (Samples)
        print("\n--- Verifying Module Details (Samples) ---")
        
        # Impact
        impact = data.get("impact", {})
        if "total_potential_savings" in impact:
            print(f"  [PASS] Impact: total_potential_savings = {impact['total_potential_savings']}")
            
        # Leakage
        leakage = data.get("leakage", {})
        if "leakage_count" in leakage:
            print(f"  [PASS] Leakage: leakage_count = {leakage['leakage_count']}")
            
        # Signals
        signals = data.get("signals", {})
        if "total_signals" in signals:
            print(f"  [PASS] Signals: total_signals = {signals['total_signals']}")
            
        # Execution
        execution = data.get("execution", {})
        if "auto_eligible_count" in execution:
            print(f"  [PASS] Execution: auto_eligible_count = {execution['auto_eligible_count']}")
            
        print("\n[CONCLUSION] Verification Completed.")
        
    except Exception as e:
        print(f"\n[ERROR] Verification Failed: {e}")
        if hasattr(e, 'read'):
            try:
                err_body = e.read().decode()[:500]
                print(f"  Error Response Body: {err_body}")
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    # Wait a moment for server to be ready just in case
    time.sleep(2)
    check_cost_intelligence()
