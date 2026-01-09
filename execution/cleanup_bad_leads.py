
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INSTANTLY_API_KEY") or "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="
BASE_URL = "https://api.instantly.ai/api/v2"

def req(method, endpoint, params=None, json_data=None):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.request(method, url, headers=headers, params=params, json=json_data, verify=False)
        return resp
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("🧹 Cleaning up 'email_not_unlocked' leads...")
    
    # 1. Search for them
    # We can try search by email? 
    target = "email_not_unlocked@domain.com"
    
    # Since we uploaded multiple, searching by email might only return one or all?
    # Let's list leads and filter if needed, OR try delete by email directly.
    # DELETE /leads?email=...
    
    print(f"Attempting direct delete for {target} from campaign f774f3f0-6570-4521-a68c-0a01e587dea0...")
    resp = req('DELETE', 'leads', params={'email': target}, json_data={"campaign_id": "f774f3f0-6570-4521-a68c-0a01e587dea0"})
    
    if resp is not None:
         print(f"Delete Status: {resp.status_code}")
         print(f"Body: {resp.text}")
    else:
         print("Request failed (None).")

    # Also try delete by email query just in case
    # req('DELETE', 'leads', params={'email': target}) 

if __name__ == "__main__":
    main()
