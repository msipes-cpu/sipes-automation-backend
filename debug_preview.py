import sys
import os

# Add root to sys.path
sys.path.append(os.getcwd())

try:
    from execution.lead_gen_orchestrator import get_preview_leads
    print("Import Successful")
except Exception as e:
    print(f"Import Failed: {e}")
    sys.exit(1)

url = "https://app.apollo.io/#/people?page=1&contactEmailStatusV2[]=verified"
try:
    print("Running get_preview_leads...")
    leads = get_preview_leads(url)
    print(f"Success! Found {len(leads)} leads.")
    print(leads)
except Exception as e:
    print(f"Execution Failed: {e}")
    import traceback
    traceback.print_exc()
