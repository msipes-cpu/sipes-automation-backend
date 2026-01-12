import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
print(f"API Key present: {bool(APOLLO_API_KEY)}")

APOLLO_API_URL = "https://api.apollo.io/v1/mixed_people/search"

payload = {
    "page": 1,
    "per_page": 10,
    "person_titles": ["ceo"],
    "person_locations": ["United States"],
    "contact_email_status": ["verified"]
}

headers = {
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "X-Api-Key": APOLLO_API_KEY
}

try:
    print("Sending request...")
    resp = requests.post(APOLLO_API_URL, headers=headers, json=payload, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
