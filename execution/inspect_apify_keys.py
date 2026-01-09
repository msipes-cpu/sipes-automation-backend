
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

APIFY_API_BASE = "https://api.apify.com/v2"
# Use the same token
TOKEN = os.getenv("APIFY_API_TOKEN")
# Run ID from the execution
RUN_ID = "ykUuP4HL9n2CQnpBY"

def main():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # Get Dataset ID from Run
    print(f"Fetching run info for {RUN_ID}...")
    run_url = f"{APIFY_API_BASE}/actor-runs/{RUN_ID}"
    resp = requests.get(run_url, headers=headers)
    run_data = resp.json().get("data", {})
    
    print("--- Cost Info ---")
    print(f"Total Cost (USD): {run_data.get('usageTotalUsd')}")
    print(f"Pricing Info: {json.dumps(run_data.get('pricingInfo'), indent=2)}")
    # Some actors charge by result, others by CU. Let's look for cost if available.
    # Note: precise cost is often in the user's dashboard, but usage gives us CUs.
    
    dataset_id = run_data.get("defaultDatasetId")
    print(f"Dataset ID: {dataset_id}")
    
    # Fetch 10 items
    print("Fetching 10 items...")
    dataset_url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items?limit=10&format=json"
    resp = requests.get(dataset_url, headers=headers)
    items = resp.json()
    
    for item in items:
        if "email" in item or "workEmail" in item or "emails" in item:
            print(json.dumps(item, indent=2))
            break

if __name__ == "__main__":
    main()
