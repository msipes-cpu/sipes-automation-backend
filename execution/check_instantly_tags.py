
import os
import sys
import requests

# Add execution dir to path to import provider
sys.path.append("/Users/michaelsipes/Coding/SA Workspace/execution")
from universal_deliverability_manager import InstantlyProvider

API_KEY = "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="
REQUIRED_TAGS = ['Warming', 'Sick', 'Bench', 'Sending']

def check_tags():
    print("🔍 Checking Instantly Tags...")
    provider = InstantlyProvider(API_KEY)
    
    # Manually trigger scan (normally happens on get_all_accounts)
    provider.tags_map = {}
    provider._scan_tags()
    
    found = []
    missing = []
    
    normalized_map = {k.lower(): v for k, v in provider.tags_map.items()}
    
    for tag in REQUIRED_TAGS:
        if tag.lower() in normalized_map:
            found.append(f"{tag} (ID: {normalized_map[tag.lower()]})")
        else:
            missing.append(tag)
            
    print("\n--- Results ---")
    if found:
        print("✅ Found:")
        for f in found: print(f"  - {f}")
        
    if missing:
        print("❌ Missing:")
        for m in missing: print(f"  - {m}")
        
    if not missing:
        print("\n🎉 All tags are set up correctly!")
    else:
        print("\n⚠️  Please create the missing tags in Instantly UI.")

if __name__ == "__main__":
    check_tags()
