
import requests
import os
import csv
import json
from dotenv import load_dotenv

load_dotenv()

# Instantly Config
API_KEY = os.getenv("INSTANTLY_API_KEY") or "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="
BASE_URL = "https://api.instantly.ai/api/v2"
CAMPAIGN_NAME = "First 5 Clients"
CSV_PATH = "marketing/first_five_tracking.csv"

def req(method, endpoint, json_data=None, params=None):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/{endpoint}"
    print(f"DEBUG: {method} {url}") # Debug print
    try:
        resp = requests.request(method, url, headers=headers, json=json_data, params=params)
        print(f"DEBUG Response: {resp.status_code}")
        return resp
    except Exception as e:
        print(f"Request Error Caught: {e}")
        return None

def main():
    print(f"🚀 Starting Instantly Campaign Setup: '{CAMPAIGN_NAME}'")

    # 1. Get Accounts & Org ID
    print("Listing Accounts...")
    accounts = []
    org_id = None
    resp = req('GET', 'accounts', params={'limit': 100})
    if resp and resp.status_code == 200:
        accounts = resp.json().get('items', [])
        print(f"Found {len(accounts)} accounts.")
        if accounts:
             org_id = accounts[0].get('organization')
             print(f"Organization ID: {org_id}")
    else:
        print(f"Failed to list accounts. Status: {resp.status_code if resp else 'None'}")
        return

    account_ids = [acc['email'] for acc in accounts]

    # 2. Find or Create Campaign
    print("Checking Campaigns...")
    campaign_id = None
    existing_schedule = None
    
    resp = req('GET', 'campaigns')
    if resp and resp.status_code == 200:
        campaigns = resp.json().get('items', []) 
        if isinstance(campaigns, list):
             if campaigns:
                 existing_schedule = campaigns[0].get('campaign_schedule')
                 print("Found existing schedule to copy.")
             for c in campaigns:
                 c_name = c.get('name')
                 c_id = c.get('id')
                 print(f"DEBUG: Found campaign '{c_name}' ({c_id})")
                 if CAMPAIGN_NAME in c_name:
                     campaign_id = c_id
                     print(f"Found match: {campaign_id}")
                     break
    
    if not campaign_id:
        print(f"Error: Campaign '{CAMPAIGN_NAME}' not found. Please create it manually.")
        return

    # 3. Add Accounts to Campaign (PATCH)
    if account_ids:
        print(f"Adding {len(account_ids)} accounts to campaign...")
        # Try PATCH to update campaign accounts
        # Note: Instantly V2 uses 'email_list' for existing email accounts
        resp = req('PATCH', f"campaigns/{campaign_id}", json_data={'email_list': account_ids})
        if resp and resp.status_code == 200:
             print("Accounts added successfully.")
        else:
             print(f"Failed to add accounts via PATCH. Status: {resp.status_code if resp else 'None'}, Body: {resp.text if resp else ''}")

    # 4. Parse CSV & Upload Leads
    print(f"Reading leads from {CSV_PATH}...")
    # ... (CSV reading logic remains sending to list, but we change upload)
    
    # Reading Logic is fine, but let's just skip to the upload block modification
    # Need to keep the CSV reading part. I'll just replace the block after reading.
    # Ah, I'm replacing lines 101-149 which covers adding accounts and reading leads and uploading. 
    # I need to keep the CSV reading logic. I will re-include it.
    
    leads_to_upload = []
    valid_count = 0
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('Email', '').strip()
                if not email: continue
                full_name = row.get('Name', '').strip()
                parts = full_name.split(' ', 1)
                first = parts[0]
                last = parts[1] if len(parts) > 1 else ''

                lead = {
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "company_name": row.get('Company', ''),
                    "personalization": row.get('Personalized_Line_Context', ''),
                    "custom_variables": {
                        "role": row.get('Role', ''),
                        "linkedin": row.get('LinkedIn', '')
                    },
                    "campaign_id": campaign_id,
                    "skip_if_in_workspace": False
                }
                leads_to_upload.append(lead)
                valid_count += 1
    except FileNotFoundError:
        print("CSV file not found.")
        return

    # 5. Upload Leads (One by One or /leads endpoint)
    # Trying POST /leads with bulk list first if allowed, otherwise loop.
    # Documentation implied "Add leads in bulk" might be supported. 
    # Let's try sending the list to /leads. If that fails (400), we loop.
    if leads_to_upload:
        print(f"Uploading {len(leads_to_upload)} leads...")
        
        # Try Bulk POST /leads
        resp = req('POST', "leads", json_data={'leads': leads_to_upload})
        if resp and resp.status_code == 200:
            print(f"Successfully uploaded {len(leads_to_upload)} leads (Bulk).")
        else:
            print(f"Bulk upload failed ({resp.status_code if resp else '?'}). Falling back to single uploads...")
            success_count = 0
            for lead in leads_to_upload:
                 r = req('POST', "leads", json_data=lead)
                 if r and r.status_code == 200:
                     success_count += 1
                 # print(f"Lead {lead['email']}: {r.status_code}")
            print(f"Uploaded {success_count}/{len(leads_to_upload)} leads individually.")

    print("✅ Setup Complete.")

if __name__ == "__main__":
    main()
