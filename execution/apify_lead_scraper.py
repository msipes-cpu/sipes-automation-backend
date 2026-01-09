import os
import sys
import time
import requests
import json
import argparse
from datetime import datetime

# Configuration
ACTOR_ID = "T1XDXWc1L92AfIJtd"  # Leads Scraper
APIFY_API_BASE = "https://api.apify.com/v2"

def load_env():
    """Load environment variables from .env file manually."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

def get_api_token():
    load_env()
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        print("❌ Error: APIFY_API_TOKEN is not set in .env")
        sys.exit(1)
    return token

def run_actor(token, inputs):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{APIFY_API_BASE}/acts/{ACTOR_ID}/runs"
    
    print(f"🚀 Starting Apify execution for Actor: {ACTOR_ID}")
    try:
        response = requests.post(url, headers=headers, json=inputs)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to start actor: {e}")
        print(f"Response: {response.text}")
        sys.exit(1)
        
    run_data = response.json().get("data", {})
    run_id = run_data.get("id")
    print(f"✅ Run started! ID: {run_id}")
    print(f"🔗 Monitor manually: https://console.apify.com/view/runs/{run_id}")
    
    return run_id

def wait_for_run(token, run_id):
    print("⏳ Waiting for run to complete...")
    url = f"{APIFY_API_BASE}/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Error checking status: {response.text}")
            time.sleep(10)
            continue
            
        data = response.json().get("data", {})
        status = data.get("status")
        
        if status == "SUCCEEDED":
            print("✅ Run succeeded!")
            return data.get("defaultDatasetId")
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"❌ Run failed with status: {status}")
            sys.exit(1)
        else:
            print(f"Still running... (Status: {status})")
            time.sleep(15)

def fetch_dataset(token, dataset_id, output_path):
    print(f"📥 Fetching results from dataset {dataset_id}...")
    url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items?format=csv&clean=true"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"💾 Results saved to: {output_path}")
    else:
        print(f"❌ Failed to download dataset: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Fetch leads using Apify Actor T1XDXWc1L92AfIJtd")
    parser.add_argument("--job_titles", nargs="+", help="List of job titles", default=[])
    parser.add_argument("--locations", nargs="+", help="List of locations (Country/State)", default=[])
    parser.add_argument("--industries", nargs="+", help="List of industries/keywords", default=[])
    parser.add_argument("--seniority", nargs="+", help="List of seniority levels", default=[])
    parser.add_argument("--employee_size", nargs="+", help="List of employee size ranges", default=[])
    parser.add_argument("--revenue", nargs="+", help="List of revenue ranges", default=[])
    parser.add_argument("--limit", type=int, help="Max number of leads", default=100)
    parser.add_argument("--output", help="Output CSV file path", default=None)
    parser.add_argument("--fetch_run_id", help="Fetch results for an existing run ID", default=None)

    args = parser.parse_args()
    
    token = get_api_token()
    
    if args.fetch_run_id:
        print(f"🔄 Resuming fetch for Run ID: {args.fetch_run_id}")
        dataset_id = wait_for_run(token, args.fetch_run_id)
        if args.output:
            output_file = args.output
        else:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs(".tmp", exist_ok=True)
            output_file = os.path.join(".tmp", f"apify_leads_{now}.csv")
        
        fetch_dataset(token, dataset_id, output_file)
        return

    # Construct Actor Input
    actor_inputs = {
        "totalResults": args.limit,
        "includeEmails": True
    }
    
    if args.job_titles:
        actor_inputs["personTitle"] = args.job_titles
    if args.locations:
        # Simple heuristic: assume first is country if known, else put in country. 
        # The actor has personCountry and personState. Let's map loosely to personCountry for now 
        # as it's the most common filter. 
        actor_inputs["personCountry"] = args.locations
    if args.industries:
        actor_inputs["industryKeywords"] = args.industries
    if args.seniority:
        actor_inputs["seniority"] = args.seniority
    if args.employee_size:
        actor_inputs["companyEmployeeSize"] = args.employee_size
    if args.revenue:
        actor_inputs["revenue"] = args.revenue

    run_id = run_actor(token, actor_inputs)
    dataset_id = wait_for_run(token, run_id)
    
    if args.output:
        output_file = args.output
    else:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(".tmp", exist_ok=True)
        output_file = os.path.join(".tmp", f"apify_leads_{now}.csv")
    
    fetch_dataset(token, dataset_id, output_file)

if __name__ == "__main__":
    main()
