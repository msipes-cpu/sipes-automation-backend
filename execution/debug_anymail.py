
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ANYMAILFINDER_URL = "https://api.anymailfinder.com/v5.1/verify-email"
API_KEY = os.getenv("ANYMAILFINDER_API_KEY")

def verify(email):
    print(f"Verifying {email}...")
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"email": email}
    
    try:
        response = requests.post(ANYMAILFINDER_URL, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not API_KEY:
        print("API Key missing!")
    else:
        verify("msipes@sipesautomation.com")
        verify("support@google.com")
