
import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Key that worked for V2 accounts
API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="

def debug_campaigns():
    print(f"Testing Key: {API_KEY[:10]}...")
    
    # 1. GET V1 List with Bearer
    try:
        url = "https://api.instantly.ai/api/v1/campaign/list"
        resp = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"}, params={'limit': 5})
        print(f"GET V1 /campaign/list (Bearer): {resp.status_code}")
        if resp.status_code == 200: print(resp.text[:200])
    except Exception as e: print(e)

    # 2. GET V1 List with Query Param
    try:
        url = "https://api.instantly.ai/api/v1/campaign/list"
        resp = requests.get(url, params={'api_key': API_KEY, 'limit': 5})
        print(f"GET V1 /campaign/list (Query): {resp.status_code}")
    except Exception as e: print(e)

    # 3. POST V1 List (Sometimes needed)
    try:
        url = "https://api.instantly.ai/api/v1/campaign/list"
        resp = requests.post(url, headers={"Authorization": f"Bearer {API_KEY}"}) # No body
        print(f"POST V1 /campaign/list: {resp.status_code}")
    except Exception as e: print(e)

    # 4. GET V2 Campaigns (Guessing)
    try:
        url = "https://api.instantly.ai/api/v2/campaigns"
        resp = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
        print(f"GET V2 /campaigns: {resp.status_code}")
    except Exception as e: print(e)

    # 5. Get V1 Analytics (Often easiest endpoint)
    try:
         url = "https://api.instantly.ai/api/v1/analytics/campaign/summary"
         resp = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
         print(f"GET V1 /analytics/campaign/summary: {resp.status_code}")
    except Exception as e: print(e)

if __name__ == "__main__":
    debug_campaigns()
