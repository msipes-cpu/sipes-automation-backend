
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("MILLION_VERIFIER_API_KEY")

print(f"Loaded Key: '{KEY}'")
if KEY:
    print(f"Key Length: {len(KEY)}")
    print(f"Key Hex: {KEY.encode().hex()}")

def test_mv():
    # Attempt 1: Params dict
    print("\n--- Attempt 1: params dict ---")
    url = "https://api.millionverifier.com/api/v3/"
    params = {
        "api": KEY,
        "email": "test@example.com"
    }
    try:
        resp = requests.get(url, params=params)
        print(f"URL: {resp.url}")
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")
    except Exception as e:
        print(e)
        
    # Attempt 2: Manual string
    print("\n--- Attempt 2: Manual f-string ---")
    url2 = f"https://api.millionverifier.com/api/v3/?api_key={KEY.strip()}&email=test@example.com"
    try:
        resp = requests.get(url2)
        print(f"URL: {url2}")
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    if KEY:
        test_mv()
    else:
        print("No Key found in env.")
