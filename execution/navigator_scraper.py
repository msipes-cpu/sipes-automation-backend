import os
import sys
import time
import requests
import json
from datetime import datetime
import argparse

# Configuration
ACTOR_ID = "curious_coder/linkedin-sales-navigator-search-scraper" 
# Official ID: curious_coder/linkedin-sales-navigator-search-scraper
# Alternate reliable one is 'curious_programmer/linkedin-sales-navigator-scraper' -> actorId usually starts with something specific. 
# Let's use "curious_programmer/linkedin-sales-navigator-scraper" explicit name for lookup or hardcode a known good one.
# For now, we will use a generic placeholder or the user's preferred one. 
# Actually, let's use the 'apify' python client pattern via requests for simplicity.
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
        print("Please fetch your API token from https://console.apify.com/account/integrations and add it to .env")
        sys.exit(1)
    return token

def run_actor(token, search_url, max_items=50, cookie=None):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Input for the actor
    # Note: Schema depends on the specific actor. This input is common for many scraper actors.
    actor_input = {
        "startUrls": [{"url": search_url}],
        "maxItems": int(max_items),
    }
    
    if cookie:
        actor_input["li_at"] = cookie

    print(f"🚀 Starting Apify execution for URL: {search_url}")
    
    # Start the actor
    # Using 'curious_programmer/linkedin-sales-navigator-scraper' -> 'kfiWxhSKp35u35iK9' is a common ID for checking, 
    # but best to use the name ~ 'curious_programmer/linkedin-sales-navigator-scraper'
    # We will try to run by name shorthand which Apify API supports usually via acts/USERNAME~ACTORNAME/runs
    
    actor_name = "curious_coder~linkedin-sales-navigator-search-scraper" 
    # Using the user~actorname format for the API URL
    
    url = f"{APIFY_API_BASE}/acts/{actor_name}/runs"
    
    try:
        response = requests.post(url, headers=headers, json=actor_input)
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
    parser = argparse.ArgumentParser(description="Scrape Sales Navigator using Apify")
    parser.add_argument("--url", help="Sales Navigator Search URL", required=True)
    parser.add_argument("--max", help="Max profiles to scrape", default=50)
    parser.add_argument("--cookie", help="li_at cookie (optional, triggers stricter mode if missing depending on actor)", default=None)
    
    args = parser.parse_args()
    
    token = get_api_token()
    run_id = run_actor(token, args.url, args.max, args.cookie)
    dataset_id = wait_for_run(token, run_id)
    
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(".tmp", f"leads_navigator_{now}.csv")
    os.makedirs(".tmp", exist_ok=True)
    
    fetch_dataset(token, dataset_id, output_file)

if __name__ == "__main__":
    main()
