
import os
import requests
from dotenv import load_dotenv

load_dotenv()

MV_KEY = os.getenv("MILLION_VERIFIER_API_KEY")
AMF_KEY = os.getenv("ANYMAILFINDER_API_KEY")

print(f"MV Key present: {bool(MV_KEY)}")
print(f"AMF Key present: {bool(AMF_KEY)}")

def check_mv():
    if not MV_KEY: return
    # Check credits or simple verify
    url = f"https://api.millionverifier.com/api/v3/?api_key={MV_KEY}&email=test@example.com"
    try:
        resp = requests.get(url)
        print(f"MillionVerifier Test: Code {resp.status_code}")
        if resp.status_code == 200:
            print(f"  Result: {resp.json().get('result')}")
    except Exception as e:
        print(f"MV Error: {e}")

def check_amf():
    if not AMF_KEY: return
    # Check status
    headers = {"Authorization": AMF_KEY, "Content-Type": "application/json"}
    # Search for a dummy
    payload = {"domain": "google.com", "first_name": "Sundar", "last_name": "Pichai"}
    try:
        resp = requests.post("https://api.anymailfinder.com/v5.1/search", headers=headers, json=payload)
        print(f"AnymailFinder Test: Code {resp.status_code}")
        if resp.status_code == 200:
             print(f"  Result: {resp.json().get('email')}")
    except Exception as e:
        print(f"AMF Error: {e}")

if __name__ == "__main__":
    check_mv()
    check_amf()
