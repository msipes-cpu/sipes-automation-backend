
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="

headers = {"Authorization": f"Bearer {API_KEY}"}

def check(endpoint):
    url = f"https://api.instantly.ai/api/v2/{endpoint}"
    print(f"GET {endpoint}")
    resp = requests.get(url, headers=headers)
    print(resp.status_code)
    if resp.status_code == 200:
        print(resp.text[:500])

check("timezones")
check("constants")
check("campaign/timezones")
