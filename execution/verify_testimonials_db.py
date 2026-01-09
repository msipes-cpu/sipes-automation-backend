import os
import requests
import json

# Load env vars manually or assume they are exported in shell
# We will use the ones printed in .env earlier if running via agent, 
# but for the user running this, they likely need python-dotenv or just exported vars.
# Here we will try to read from .env file directly if vars are missing.

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '../.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if not os.environ.get(key):
                        os.environ[key] = value

load_env()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    exit(1)

print(f"Checking Supabase at {SUPABASE_URL}...")

# Try to fetch from testimonials table
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(f"{SUPABASE_URL}/rest/v1/testimonials?select=*&limit=1", headers=headers)

if response.status_code == 200:
    print("✅ Success! 'testimonials' table found and accessible.")
    data = response.json()
    print(f"Count of records: {len(data)}")
elif response.status_code == 404:
    print("❌ Error: 'testimonials' table not found (404). Did you run the migration SQL?")
else:
    print(f"❌ Error: Unexpected status code {response.status_code}")
    print(response.text)
