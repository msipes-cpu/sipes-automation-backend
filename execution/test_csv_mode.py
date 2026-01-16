import os
import sys

# Mock Env
os.environ["GOOGLE_CREDENTIALS_JSON"] = ""
os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"] = "nonexistent.json"
os.environ["SENDER_EMAIL"] = "test@example.com"
os.environ["SENDER_PASSWORD"] = "dummy"

# Import orchestrator
from execution.lead_gen_orchestrator import run_orchestrator

print(">>> Starting Test Run (CSV Mode)...")
try:
    # Use mock mode to avoid hitting Apollo API
    run_orchestrator("https://app.apollo.io/mock", "test@example.com", limit=5, mock_mode=True)
    print(">>> Test Run Completed Successfully")
except Exception as e:
    print(f">>> Test Run CRASHED: {e}")
    import traceback
    traceback.print_exc()
