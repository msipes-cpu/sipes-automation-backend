"""
Simulation Script
Runs the 'Master Scheduler' logic LOCALLY to verify Supabase connection and Loop.
"""

from dotenv import load_dotenv
import os
import sys

# Explicitly load the file
env_path = os.path.join(os.getcwd(), 'smartguard-saas', '.env.local')
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

sys.path.append('execution')
from supabase import create_client
from inbox_bench_core import InboxBench

def simulate():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Missing Supabase Credentials in environment.")
        return

    print(f"🔌 Connecting to Supabase: {url}")
    try:
        supabase = create_client(url, key)
        
        # 1. Fetch Users
        response = supabase.table("user_settings").select("*").eq("is_active", True).execute()
        users = response.data
        
        print(f"🔎 Found {len(users)} active users.")
        
        for user in users:
            print(f"\n--- Processing User {user.get('user_id')} ---")
            
            # 2. Instantiate Guard
            guard = InboxBench(
                smartlead_api_key=user.get('smartlead_api_key'),
                instantly_api_key=user.get('instantly_api_key'),
                plusvibe_api_key=user.get('plusvibe_api_key'),
                notification_email=user.get('notification_email')
            )
            
            # 3. DRY RUN Check (Don't crash if keys are invalid)
            # We just print what we would do
            print("   Running Checks...")
            guard.execute_all()
            print("   ✅ Done.")
            
    except Exception as e:
        print(f"❌ Simulation Failed: {e}")

if __name__ == "__main__":
    simulate()
