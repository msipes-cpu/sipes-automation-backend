import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")
MILLION_VERIFIER_URL = "https://api.millionverifier.com/api/v3/"

def test_mv(email):
    print(f"Testing {email}...")
    params = {
        "api": MILLION_VERIFIER_API_KEY,
        "email": email,
        "timeout": 10
    }
    resp = requests.get(MILLION_VERIFIER_URL, params=params)
    print(f"Status: {resp.status_code}")
    print(f"Body: {resp.text}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except:
        pass

if __name__ == "__main__":
    if not MILLION_VERIFIER_API_KEY:
        print("No API Key")
    else:
        test_mv("michael@sipesautomation.com") # Likely valid or catch_all
        test_mv("invalid_email_123456@gmail.com")
