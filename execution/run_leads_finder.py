
import os
import sys
import time
import requests
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuration
ACTOR_ID = "IoSHqwTR9YGhzccez" # Leads Finder (Apollo Alternative)
APIFY_API_BASE = "https://api.apify.com/v2"

def get_api_token():
    token = os.getenv("APIFY_API_TOKEN") or os.getenv("APIFY_API_KEY")
    if not token:
        print("❌ Error: APIFY_API_TOKEN (or APIFY_API_KEY) is not set in .env")
        sys.exit(1)
    return token

def run_actor(token, inputs):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{APIFY_API_BASE}/acts/{ACTOR_ID}/runs"
    
    print(f"🚀 Starting Apify execution for Actor: {ACTOR_ID}")
    print(f"Input: {json.dumps(inputs, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=inputs)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to start actor: {e}")
        try:
            err_json = response.json()
            print(f"Server Response: {json.dumps(err_json, indent=2)}")
        except:
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
        try:
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
                print(f"❌ Run failed with status: {status}. (Fetching partial results anyway...)")
                return data.get("defaultDatasetId")
            else:
                print(f"Status: {status}...", end="\r")
                time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user. Run might still be active on Apify.")
            sys.exit(0)

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
    parser = argparse.ArgumentParser(description="Run Apify Leads Finder")
    parser.add_argument("--keywords", nargs="+", help="Keywords to search", default=["Marketing Agency"])
    parser.add_argument("--location", help="Location", default="United States")
    parser.add_argument("--limit", type=int, help="Max items", default=50)
    parser.add_argument("--output", help="Output CSV", default=None)
    parser.add_argument("--fetch_run_id", help="Fetch results for an existing run ID")
    parser.add_argument("--dataset_id", help="Directly fetch results from a dataset ID")
    
    args = parser.parse_args()
    token = get_api_token()
    
    if args.dataset_id:
        print(f"📥 Fetching directly from Dataset ID: {args.dataset_id}")
        dataset_id = args.dataset_id
        if args.output:
            outfile = args.output
        else:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            outfile = f"marketing/apify_leads_{now}.csv"
        
        fetch_dataset(token, dataset_id, outfile)
        return

    if args.fetch_run_id:
        print(f"🔄 Resuming fetch for Run ID: {args.fetch_run_id}")
        dataset_id = wait_for_run(token, args.fetch_run_id)
        if args.output:
            outfile = args.output
        else:
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            outfile = f"marketing/apify_leads_{now}.csv"
            
        fetch_dataset(token, dataset_id, outfile)
        return

    # Construct Inputs
    inputs = {
        "search": " ".join(args.keywords),
        "location": args.location,
        "maxItems": args.limit
    }
    
    run_id = run_actor(token, inputs)
    dataset_id = wait_for_run(token, run_id)
    
    # Save output
    if args.output:
        outfile = args.output
    else:
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        outfile = f"marketing/apify_leads_{now}.csv"
        
    fetch_dataset(token, dataset_id, outfile)

if __name__ == "__main__":
    main()
