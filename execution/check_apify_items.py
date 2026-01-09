
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACTOR_RUN_ID = "TSd4Av5BQ1kp5GnOy"
APIFY_API_BASE = "https://api.apify.com/v2"

def main():
    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        print("Token missing")
        return

    # Get run details to find dataset ID
    url = f"{APIFY_API_BASE}/actor-runs/{ACTOR_RUN_ID}"
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Error getting run: {resp.text}")
        return
        
    data = resp.json().get("data", {})
    dataset_id = data.get("defaultDatasetId")
    status = data.get("status")
    
    print(f"Run Status: {status}")
    print(f"Dataset ID: {dataset_id}")
    
    if dataset_id:
        # Check dataset metadata for count
        meta_url = f"{APIFY_API_BASE}/datasets/{dataset_id}"
        meta_resp = requests.get(meta_url, headers=headers)
        if meta_resp.status_code == 200:
             count = meta_resp.json().get("data", {}).get("itemCount")
             print(f"Total Items in Dataset: {count}")
        
        # Check items sample
        item_url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items?format=json&limit=1"
        item_resp = requests.get(item_url, headers=headers)
        if item_resp.status_code == 200:
            items = item_resp.json()
            if items:
                print(f"Sample Item Keys: {list(items[0].keys())}")
        else:
            print(f"Error checking items: {item_resp.text}")

if __name__ == "__main__":
    main()
