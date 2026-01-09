
import requests
import json

API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="

def debug_accounts():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    print("--- Debugging Instantly Accounts ---")
    
    # 1. V2 Accounts
    url_v2 = "https://api.instantly.ai/api/v2/accounts"
    print(f"\nGET {url_v2}")
    try:
        resp = requests.get(url_v2, headers=headers, params={'limit': 100, 'skip': 0})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            print(f"Items found: {len(items)}")
            if items:
                print("First item sample:", json.dumps(items[0], indent=2))
            else:
                print("Raw Response:", resp.text)
        else:
            print("Error Response:", resp.text)
    except Exception as e:
        print(f"Exception: {e}")

    # 2. V2 Accounts (No params)
    print(f"\nGET {url_v2} (No params)")
    try:
        resp = requests.get(url_v2, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Items found: {len(resp.json().get('items', []))}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_accounts()
