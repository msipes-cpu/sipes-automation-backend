
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Try to get key from env, fallback to the one found in debug file if needed (but env is best practice)
API_KEY = os.getenv("INSTANTLY_API_KEY")

# Fallback from debug file if env is empty (just for this session's consistency)
if not API_KEY:
    # Extracted from debug_instantly_accounts.py
    API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ==" 

BASE_URL = "https://api.instantly.ai/api/v1" # V1 is often standard for campaigns, V2 for accounts. I'll try V1 first for campaigns.

def test_endpoints():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # 1. List Campaigns (V1)
    print("\n--- Testing GET /api/v1/campaign/list ---")
    try:
        resp = requests.get(f"{BASE_URL}/campaign/list", headers=headers, params={'limit': 5})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # Handle list or dict response
            limit_show = 3
            if isinstance(data, list):
                print(f"Found {len(data)} campaigns (List).")
                print(json.dumps(data[:limit_show], indent=2))
            elif isinstance(data, dict):
                items = data.get('items', [])
                print(f"Found {len(items)} campaigns (Dict).")
                print(json.dumps(items[:limit_show], indent=2))
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_endpoints()
