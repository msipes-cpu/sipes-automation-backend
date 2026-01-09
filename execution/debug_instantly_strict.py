
import requests

API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="
BASE_URL = "https://api.instantly.ai/api/v2"

def test_call():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    endpoint = "accounts"
    url = f"{BASE_URL}/{endpoint}"
    params = {'limit': 1000}
    
    print(f"Calling {url} with params={params}")
    try:
        resp = requests.get(url, headers=headers, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Text len: {len(resp.text)}")
        d = resp.json()
        print(f"Items: {len(d.get('items', []))}")
        print(f"Accounts (old key): {len(d.get('accounts', []))}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_call()
