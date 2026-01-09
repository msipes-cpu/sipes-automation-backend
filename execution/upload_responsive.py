
import requests
import os
import csv
import json
import argparse
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("INSTANTLY_API_KEY") or "YTA5NTM0NzgtZTgzNC00OGFmLWJlZmMtNzdiMzkxZDg1ZGE2OkRFaWx2aG1hU3d5aQ=="
BASE_URL = "https://api.instantly.ai/api/v2"

def req(method, endpoint, json_data=None, params=None):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    url = f"{BASE_URL}/{endpoint}"
    # SSL verify=False needed for current environment
    try:
        resp = requests.request(method, url, headers=headers, json=json_data, params=params, verify=False)
        return resp
    except Exception as e:
        print(f"Request Error: {e}")
        return None

def upload_leads(csv_path, campaign_id):
    print(f"🚀 Starting Upload to Campaign {campaign_id}")
    print(f"📄 Reading from: {csv_path}")

    leads_list = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('Email', '').strip()
                if not email: continue
                
                full_name = row.get('Name', '').strip()
                parts = full_name.split(' ', 1)
                first = parts[0]
                last = parts[1] if len(parts) > 1 else ''

                custom_vars = {
                    "role": row.get('Role') or row.get('Title', ''),
                    "linkedin": row.get('LinkedIn', ''),
                    "company": row.get('Company', ''),
                    "draft_variant": row.get('Generated_Draft_Variant', ''),
                    "draft_subject": row.get('Generated_Draft_Subject', ''),
                    "draft_body": row.get('Generated_Draft_Body', ''),
                     # Fallbacks for other potential columns
                    "location": row.get("Location", ""),
                    "website": row.get("Website", "")
                }

                lead = {
                    "email": email,
                    "first_name": first,
                    "last_name": last,
                    "company_name": row.get('Company', ''),
                    "personalization": row.get('Personalized_Line_Context', ''),
                    "website": row.get("Website", ""),
                    "custom_variables": custom_vars,
                    # We add these to payload for safety, though query param does the heavy lifting usually
                    "campaign_id": campaign_id,
                    "skip_if_in_workspace": False
                }
                leads_list.append(lead)

    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        return

    if not leads_list:
        print("No leads found to upload.")
        return

    print(f"Processing {len(leads_list)} leads...")
    
    success_count = 0
    endpoint = "leads"
    
    # Using Single Loop with URL Param + Body Param (The "Responsive/Robust" Method)
    for i, lead in enumerate(leads_list):
        # Construct URL with campaign_id to force linkage
        endpoint_with_param = f"leads?campaign_id={campaign_id}"
        
        # Payload already has skip_if_in_workspace=False
        resp = req('POST', endpoint_with_param, json_data=lead)
        
        if resp is not None and resp.status_code == 200:
            success_count += 1
            print(f"[{i+1}/{len(leads_list)}] ✅ Uploaded {lead['email']}")
        else:
            status = resp.status_code if resp else 'NoResp'
            body = resp.text if resp else ''
            print(f"[{i+1}/{len(leads_list)}] ❌ Failed {lead['email']} (Status: {status}) Body: {body}")

    print(f"\nUpload Complete. Success: {success_count}/{len(leads_list)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload leads to Instantly Campaign")
    parser.add_argument("--csv", required=True, help="Path to CSV file")
    parser.add_argument("--campaign", required=True, help="Campaign ID")
    args = parser.parse_args()

    upload_leads(args.csv, args.campaign)
