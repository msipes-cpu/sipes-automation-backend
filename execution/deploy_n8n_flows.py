import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

N8N_URL = os.getenv("N8N_URL", "https://sallc.app.n8n.cloud")
N8N_API_KEY = os.getenv("N8N_API_KEY")

TEMPLATES_DIR = "delivery_frameworks/speed_to_lead/n8n_templates"
WORKFLOW_FILES = [
    "01_Lead_Ingest.json",
    "02_Router_and_Sync.json",
    "03_Communications.json",
    "04_Backup_Watchdog.json",
    "07_Sales_Call_Automation.json"
]

def deploy_workflow(filename):
    if not N8N_URL or not N8N_API_KEY:
        print("❌ Error: N8N_URL or N8N_API_KEY not set in .env")
        return

    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    try:
        with open(filepath, 'r') as f:
            workflow_json = json.load(f)
            
        # n8n API expects the workflow object directly or wrapped. 
        # Our templates are the workflow object itself (nodes, connections, etc).
        
        # Check if we need to remove ID to force creation of new workflow or update existing?
        # For this script, we'll just create new ones to be safe.
        if 'id' in workflow_json:
            del workflow_json['id']

        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers={"X-N8N-API-KEY": N8N_API_KEY},
            json=workflow_json
        )
        
        if response.status_code == 200:
            wf_data = response.json()
            print(f"✅ Successfully deployed: {filename} (ID: {wf_data['id']})")
            if not wf_data['active']:
                print(f"   ⚠️  Note: Workflow is currently inactive. Please activate it in the UI.")
        else:
            print(f"❌ Failed to deploy {filename}: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error processing {filename}: {str(e)}")

def main():
    print(f"🚀 Starting deployment to n8n at {N8N_URL}...")
    
    # Check directory
    if not os.path.exists(TEMPLATES_DIR):
         print(f"❌ Template directory not found: {TEMPLATES_DIR}")
         return

    for wf_file in WORKFLOW_FILES:
        deploy_workflow(wf_file)
    
    print("\nTriggering complete.")

if __name__ == "__main__":
    main()
