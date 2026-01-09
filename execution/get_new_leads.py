import csv
import os
import re
import sys

# Ensure we can import backend.instrumentation
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.instrumentation import step, init
except ImportError:
    # Dummy fallbacks for local testing without backend
    def step(name):
        def decorator(func):
            return func
        return decorator
    def init(name):
        return None

FIRST_FIVE_TRACKING = "marketing/first_five_tracking.csv"
INPUT_FILES = [
    "marketing/agency_owners_raw.csv"
]
OUTPUT_FILE = "marketing/new_leads_batch.csv"

@step("Normalize URL")
def normalize_url(url):
    if not url:
        return ""
    return url.strip().rstrip("/").replace("https://", "").replace("http://", "").replace("www.", "")

@step("Load Suppression List")
def load_suppression_list():
    existing_identifiers = set()
    
    if os.path.exists(FIRST_FIVE_TRACKING):
        print(f"Reading {FIRST_FIVE_TRACKING}...")
        with open(FIRST_FIVE_TRACKING, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Email"):
                    existing_identifiers.add(row["Email"].strip().lower())
                if row.get("LinkedIn"):
                    existing_identifiers.add(normalize_url(row["LinkedIn"]))
    
    print(f"Loaded {len(existing_identifiers)} existing identifiers to suppress.")
    return existing_identifiers

@step("Check Role Eligibility")
def check_role_eligibility(role, industry):
    # 1. Prepare data
    role_lower = role.lower()
    industry_lower = industry.lower()

    # 2. Role Check (Must be Owner/Exec)
    target_roles = ["owner", "president", "ceo", "founder", "partner", "principal", "chief executive"]
    if not any(r in role_lower for r in target_roles):
        return False
    
    # 3. Negative Role Check (Must NOT be Product Owner etc)
    bad_roles = ["product owner", "project owner", "process owner", "business owner analyst", "franchise owner", "sales development"]
    if any(br in role_lower for br in bad_roles):
        return False

    return True

@step("Process Input Files")
def process_input_files(existing_identifiers, target_count=20):
    new_leads = []
    
    for input_file in INPUT_FILES:
        if len(new_leads) >= target_count:
            break
            
        if not os.path.exists(input_file):
            print(f"Skipping missing file: {input_file}")
            continue

        print(f"Reading {input_file}...")
        with open(input_file, 'r', encoding='utf-8-sig') as f: 
            reader = csv.DictReader(f)
            
            for row in reader:
                if len(new_leads) >= target_count:
                    break
                
                email = row.get("email", "").strip()
                linkedin = row.get("linkedin", "").strip()
                
                if not linkedin:
                    continue

                role = row.get("job_title", "").strip()
                if not role:
                    continue
                
                # Check eligibility
                if not check_role_eligibility(role, row.get("industry", "")):
                    continue

                # Duplicate Check
                if email and email.lower() in existing_identifiers:
                    continue
                if linkedin and normalize_url(linkedin) in existing_identifiers:
                    continue
                
                # Add to new leads
                full_name = row.get("full_name") or f"{row.get('first_name', '')} {row.get('last_name', '')}".strip()
                
                lead = {
                    "Name": full_name,
                    "Company": row.get("company_name", ""),
                    "Role": role,
                    "Email": email,
                    "LinkedIn": linkedin
                }
                new_leads.append(lead)
                
                # Add to suppression set
                if email:
                    existing_identifiers.add(email.lower())
                if linkedin:
                    existing_identifiers.add(normalize_url(linkedin))
                    
    return new_leads

@step("Save Results")
def save_results(new_leads):
    print(f"\nFound {len(new_leads)} new unique leads:")
    
    headers = ["Name", "Company", "Role", "Email", "LinkedIn"]
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(new_leads)

    print(f"\nSaved to {OUTPUT_FILE}")
    return len(new_leads)

@step("Run Lead Generation")
def main():
    # Initialize Context
    ctx = init("get_new_leads.py")
    
    try:
        # 1. Load suppression
        existing_identifiers = load_suppression_list()

        # 2. Extract new leads
        new_leads = process_input_files(existing_identifiers)

        # 3. Output results
        save_results(new_leads)
        
        if ctx:
            ctx.finish_run("completed")
            
    except Exception as e:
        print(f"Workflow failed: {e}")
        if ctx:
            ctx.finish_run("failed")
        raise e

if __name__ == "__main__":
    main()
