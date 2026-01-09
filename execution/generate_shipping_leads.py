
import os
import sys
import time
import requests
import json
import argparse
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
APIFY_ACTOR_ID = "T1XDXWc1L92AfIJtd"  # Leads Scraper
APIFY_API_BASE = "https://api.apify.com/v2"
ANYMAILFINDER_URL = "https://api.anymailfinder.com/v5.1/verify-email"

def get_api_token(var_name):
    token = os.getenv(var_name)
    if not token:
        print(f"❌ Error: {var_name} is not set in .env")
        sys.exit(1)
    return token

def run_apify_actor(token, inputs):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = f"{APIFY_API_BASE}/acts/{APIFY_ACTOR_ID}/runs"
    
    print(f"🚀 Starting Apify execution for Actor: {APIFY_ACTOR_ID}")
    try:
        response = requests.post(url, headers=headers, json=inputs)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"❌ Failed to start actor: {e}")
        print(f"Response: {response.text}")
        try:
             print(f"JSON: {response.json()}")
        except:
             pass
        sys.exit(1)
        
    run_data = response.json().get("data", {})
    run_id = run_data.get("id")
    print(f"✅ Run started! ID: {run_id}")
    print(f"🔗 Monitor manually: https://console.apify.com/view/runs/{run_id}")
    return run_id

def wait_for_apify_run(token, run_id):
    print("⏳ Waiting for Apify run to complete...")
    url = f"{APIFY_API_BASE}/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Error checking status: {response.text}")
            time.sleep(10)
            continue
            
        data = response.json().get("data", {})
        status = data.get("status")
        
        if status == "SUCCEEDED":
            print("✅ Run succeeded!")
            return data.get("defaultDatasetId")
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"❌ Run failed with status: {status}")
            sys.exit(1)
        else:
            print(f"Apify Status: {status}...", end="\r")
            time.sleep(15)

def fetch_apify_dataset(token, dataset_id):
    print(f"📥 Fetching results from dataset {dataset_id}...")
    url = f"{APIFY_API_BASE}/datasets/{dataset_id}/items?format=json&clean=true"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to download dataset: {response.text}")
        sys.exit(1)

def verify_email_anymailfinder(email, api_key):
    """Verifies email using Anymail Finder."""
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    payload = {"email": email}

    try:
        # Rate limiting handling could be added here if needed
        response = requests.post(ANYMAILFINDER_URL, headers=headers, json=payload)
        if response.status_code != 200:
             return {"result": "error", "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {"result": "error", "error": str(e)}

def categorize_industry(industry_string):
    """Simple keyword matching to categorize industry."""
    if not industry_string:
        return "Other"
    
    industry_lower = str(industry_string).lower()
    
    if "shipping" in industry_lower:
        return "Shipping"
    elif "logistics" in industry_lower or "transport" in industry_lower or "supply chain" in industry_lower:
        return "Logistics"
    elif "manufacturing" in industry_lower or "industrial" in industry_lower:
        return "Manufacturing"
    else:
        return "Other"

def main():
    parser = argparse.ArgumentParser(description="Generate Shipping/Logistics/Mfg Leads")
    parser.add_argument("--limit", type=int, default=100, help="Number of leads to scrape")
    parser.add_argument("--test_mode", action="store_true", help="Run in test mode (small batch)")
    parser.add_argument("--fetch_run_id", help="Fetch results for an existing Apify run ID", default=None)
    parser.add_argument("--mode", choices=["shipping", "logistics", "manufacturing"], help="Target industry mode", required=True)
    
    args = parser.parse_args()
    
    apify_token = get_api_token("APIFY_API_TOKEN")
    anymail_key = get_api_token("ANYMAILFINDER_API_KEY")

    # Define keyword sets
    keywords_map = {
        "shipping": ["Shipping", "Maritime", "Freight", "Trucking", "Transport", "Fleet", "Cargo", "Carrier"],
        "logistics": ["Logistics", "Supply Chain", "Warehousing", "Distribution", "Fulfillment", "3PL", "Inventory"],
        "manufacturing": ["Manufacturing", "Industrial", "Production", "Assembly", "Fabrication"]
    }

    if args.test_mode:
        print("🧪 Running in TEST MODE (Mocking Scrape)")
        leads_data = [
            {
                "fullName": "Michael Sipes",
                "email": "msipes@sipesautomation.com", # Valid (hopefully)
                "companyName": "Sipes Automation",
                "title": "CEO",
                "industry": "Marketing",
                "employeesCount": "1-10",
                "firstName": "Michael",
                "lastName": "Sipes"
            },
           {
                "fullName": "Test Shipping Exec",
                "email": "msipes@sipesautomation.com", # Use valid email to test splitting
                "companyName": "Test Shipping Co",
                "title": "CEO",
                "industry": "Shipping",
                "employeesCount": "500-1000",
                "firstName": "Test",
                "lastName": "User"
            },
            {
                "fullName": "John Doe",
                "email": "johndoe_fake_12345@google.com", # Invalid
                "companyName": "Fake Logistics Inc",
                "title": "Owner",
                "industry": "Logistics",
                "employeesCount": "500-1000",
                "firstName": "John",
                "lastName": "Doe"
            }
        ]
        
    # Step 1: Scrape (Only if not testing or explicit fetch)
    elif args.fetch_run_id:
        print(f"🔄 Resuming from run {args.fetch_run_id}")
        dataset_id = wait_for_apify_run(apify_token, args.fetch_run_id)
        leads_data = fetch_apify_dataset(apify_token, dataset_id)
    else:
        print(f"🔍 Starting new scrape for mode: {args.mode.upper()}...")
        # Defined Filters
        actor_inputs = {
            "totalResults": args.limit, # Use arg limit directly!
            "includeEmails": True,
            "personTitle": ["CEO", "COO", "President", "Owner", "Co-Founder", "Founder"],
            "personCountry": ["United States"],
            "companyEmployeeSize": ["501 - 1000", "1001 - 5000", "5001 - 10000", "10000+"],
            "industryKeywords": keywords_map[args.mode]
        }
        
        run_id = run_apify_actor(apify_token, actor_inputs)
        dataset_id = wait_for_apify_run(apify_token, run_id)
        leads_data = fetch_apify_dataset(apify_token, dataset_id)

    print(f"✅ Scraped {len(leads_data)} raw leads. Starting verification (Parallel)...")

    # Step 2: Verify & Process (Parallel)
    verified_leads = []
    
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_single_lead(lead):
        email = lead.get("email") or lead.get("workEmail")
        if not email and lead.get("emails") and len(lead.get("emails")) > 0:
            email = lead.get("emails")[0]
        
        if not email:
            return None

        # Verify
        result = verify_email_anymailfinder(email, anymail_key)
        status = result.get("email_status")
        
        if status == "valid":
             industry_raw = lead.get("industry") or lead.get("companyIndustry") or lead.get("organizationIndustry") or ""
             category = categorize_industry(industry_raw)
             
             return {
                 "Name": lead.get("fullName") or f"{lead.get('firstName', '')} {lead.get('lastName', '')}",
                 "First Name": lead.get("firstName", ""),
                 "Last Name": lead.get("lastName", ""),
                 "Title": lead.get("title") or lead.get("jobTitle"),
                 "Company": lead.get("companyName") or lead.get("company"),
                 "Email": email,
                 "LinkedIn": lead.get("linkedinUrl") or lead.get("linkedin"),
                 "Location": lead.get("location") or lead.get("country"),
                 "Industry": industry_raw,
                 "Category": category,
                 "Employee Size": lead.get("employeesCount") or lead.get("companyEmployeeSize"),
                 "Website": lead.get("website") or lead.get("companyWebsite")
             }
        return None

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(process_single_lead, lead): lead for lead in leads_data}
        
        total = len(futures)
        completed = 0
        
        for future in as_completed(futures):
            completed += 1
            if completed % 50 == 0:
                print(f"[{completed}/{total}] Processing... ({len(verified_leads)} valid so far)", end="\r")
            
            try:
                result = future.result()
                if result:
                    verified_leads.append(result)
            except Exception as e:
                # print(f"Error processing lead: {e}")
                pass
        
    print(f"\n✨ Verification Complete. {len(verified_leads)} valid leads found.")

    # Step 3: Split and Save
    df = pd.DataFrame(verified_leads)
    
    if df.empty:
        print("⚠️ No valid leads found.")
        return

    os.makedirs("marketing/leads_output", exist_ok=True)
    
    # Save Generic Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"marketing/leads_output/all_verified_leads_{timestamp}.csv", index=False)

    # Split
    shipping_df = df[df["Category"] == "Shipping"]
    logistics_df = df[df["Category"] == "Logistics"]
    manufacturing_df = df[df["Category"] == "Manufacturing"]
    
    shipping_path = f"marketing/leads_output/Shipping_Leads_{timestamp}.csv"
    logistics_path = f"marketing/leads_output/Logistics_Leads_{timestamp}.csv"
    manufacturing_path = f"marketing/leads_output/Manufacturing_Leads_{timestamp}.csv"
    
    shipping_df.to_csv(shipping_path, index=False)
    logistics_df.to_csv(logistics_path, index=False)
    manufacturing_df.to_csv(manufacturing_path, index=False)
    
    print(f"📂 Saved Shipping Leads ({len(shipping_df)}): {shipping_path}")
    print(f"📂 Saved Logistics Leads ({len(logistics_df)}): {logistics_path}")
    print(f"📂 Saved Manufacturing Leads ({len(manufacturing_df)}): {manufacturing_path}")

if __name__ == "__main__":
    main()
