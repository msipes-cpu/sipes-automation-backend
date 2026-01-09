
import sys
import os
# Add execution dir
sys.path.append("/Users/michaelsipes/Coding/SA Workspace/execution")
from universal_deliverability_manager import InstantlyProvider

API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="

def debug_provider():
    print("--- Debugging InstantlyProvider ---")
    provider = InstantlyProvider(API_KEY)
    
    print("1. Testing _scan_tags()...")
    provider.tags_map = {}
    provider._scan_tags()
    print(f"Tags Map: {provider.tags_map}")
    
    print("\n2. Testing get_all_accounts()...")
    accounts = provider.get_all_accounts()
    print(f"Accounts found: {len(accounts)}")
    if accounts:
        print(f"Sample: {accounts[0]}")
    else:
        print("No accounts returned from provider method.")

if __name__ == "__main__":
    debug_provider()
