import pandas as pd
import re

import pandas as pd
import re
import os
import csv

INPUT_FILES = [
    "marketing/agency_owners_raw.csv",
    "marketing/agency_owners_batch_2.csv"
]
OUTPUT_FILE = "marketing/new_leads_batch.csv"
TRACKING_FILE = "marketing/first_five_tracking.csv"

def normalize_url(url):
    if not isinstance(url, str):
        return ""
    return url.strip().rstrip("/").replace("https://", "").replace("http://", "").replace("www.", "")

def main():
    print("Loading data with Pandas...")
    dfs = []
    for f in INPUT_FILES:
        if os.path.exists(f):
            print(f"Reading {f}...")
            try:
                # Handle inconsistent columns or BOM
                dfs.append(pd.read_csv(f))
            except Exception as e:
                print(f"Error reading {f}: {e}")
    
    if not dfs:
        print("No input files found!")
        return
        
    df = pd.concat(dfs, ignore_index=True)
    print(f"Total rows loaded: {len(df)}")

    # 1. Normalize Columns
    df['job_title'] = df['job_title'].astype(str).str.lower().fillna('')
    df['industry'] = df['industry'].astype(str).str.lower().fillna('')
    df['company_description'] = df['company_description'].astype(str).str.lower().fillna('')
    df['keywords'] = df['keywords'].astype(str).str.lower().fillna('')
    df['company_name'] = df['company_name'].astype(str).str.lower().fillna('')
    df['email'] = df['email'].astype(str).str.lower().str.strip()
    # Normalize 'nan' to empty string
    df.replace('nan', '', inplace=True)

    # 2. Filter by Role (Owner, President, etc.)
    target_roles = ["owner", "president", "ceo", "founder", "partner", "principal", "chief executive"]
    role_mask = df['job_title'].apply(lambda x: any(r in x for r in target_roles))
    
    # Negative Roles
    bad_roles = ["product owner", "project owner", "process owner", "business owner analyst", "franchise owner", "sales development"]
    bad_role_mask = df['job_title'].apply(lambda x: any(br in x for br in bad_roles))
    
    candidates = df[role_mask & ~bad_role_mask].copy()
    print(f"Candidates after Role Filter: {len(candidates)}")

    # 3. STRICT Positive Filter -> Must be an Agency
    # Condition A: Industry is explicitly Marketing/Advertising
    explicit_industries = [
        "marketing & advertising", 
        "marketing and advertising", 
        "public relations and communications", 
        "online media", 
        "design", 
        "graphic design",
        "media production"
    ]
    
    # Condition B: Company Name indicates Agency
    agency_name_keywords = [
        "agency", "marketing", "advertising", "media", "communications", 
        "creative", "digital", "interactive", "pr", "public relations", 
        "studios", "solutions", "group", "consulting", "partners", "ventures"
    ]
    # "Solutions", "Group", "Consulting", "Partners" are weak on their own. 
    # Let's require stronger overlap if using those.
    # Actually, let's keep it simple: 
    # If Industry is Explicit -> Keep.
    # If Industry is generic (e.g. "Internet"), Company Name MUST have "Agency", "Marketing", "Advertising", "Digital", "Creative".
    
    strong_agency_name_keywords = ["agency", "marketing", "advertising", "branding", "creative", "media"]

    def is_marketing_agency(row):
        ind = row['industry']
        name = row['company_name'].lower()
        
        # 1. Explicit Industry Match
        if any(ei in ind for ei in explicit_industries):
            return True
            
        # 2. Strong Name Match (even if industry is generic like 'Internet')
        if any(k in name for k in strong_agency_name_keywords):
            # Check for false positives in name like "Marketing Manager" (unlikely in company name but possible)
            return True
            
        return False

    marketing_mask = candidates.apply(is_marketing_agency, axis=1)
    
    # 4. Strict Negative Filter (Remove false positives from the above)
    # FATAL: Always exclude (Insurance, Real Estate, etc.)
    fatal_negatives = [
        "insurance", "real estate", "realtor", "home care", "healthcare", "senior care", 
        "fitness", "gym", "dental", "medical", "clinic", "health", "construction", "cleaning", 
        "staffing", "recruiting", "recruiters", "mortgage", "bank", "financial", "investment", "wealth",
        "pest control", "plumbing", "hvac", "roofing", "auto", "car", "transporation",
        "trucking", "dairy", "food", "beverage",
        "restaurant", "therapy", "counseling", "nursing", "pharmacy", "veterinary",
        "legal", "law", "attorney", "school", "education", "university", "college",
        "hotel", "motel", "resort", "inn", "hospitality",
        "church", "ministry", "non-profit", "charity"
    ]
    
    # SUSPICIOUS: Exclude UNLESS generic agency (e.g. merch agencies have shipping)
    # Actually, if we use the 'marketing_mask' (which requires Explicit Industry or Strong Name), 
    # we can be more lenient with these.
    # But we should still block them if they are the *primary* business.
    # Let's keep them as FATAL for now but remove the ones that merch agencies have.
    
    # "shipping", "logistics", "manufacturing" -> Brand Fuel has these.
    # "wholesale", "retail", "store", "shop" -> Merch agencies have these.
    # So we remove them from fatal.
    
    candidates['combined_text'] = candidates['company_description'] + " " + candidates['industry'] + " " + candidates['keywords'] + " " + candidates['company_name'].astype(str).str.lower()

    def check_fatal(text):
        for ns in fatal_negatives:
             # Use word bounds
             if re.search(r'\b' + re.escape(ns) + r'\b', text):
                 return True
        return False

    fatal_mask = candidates['combined_text'].apply(check_fatal)
    
    # 5. Apply Masks
    # Must be Marketing Agency AND NOT Fatal
    # Note: is_marketing_agency function (marketing_mask) already enforces:
    # - Explicit Industry OR
    # - Strong Name Match
    # This automatically filters out generic "IT Services" unless they are called "Foobar Digital Agency".
    
    valid_leads = candidates[marketing_mask & ~fatal_mask].copy()
    print(f"Valid leads after Filters: {len(valid_leads)}")
    
    # 5. Deduplicate
    # Load tracking
    
    existing_emails = set()
    existing_linkedin = set()
    if os.path.exists(TRACKING_FILE):
         with open(TRACKING_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Email"): existing_emails.add(row["Email"].strip().lower())
                if row.get("LinkedIn"): existing_linkedin.add(normalize_url(row["LinkedIn"]))
    
    # Check dupes
    def is_dupe(row):
        email = row.get('email', '')
        linkedin = str(row.get('linkedin', ''))
        if email and email in existing_emails: return True
        if linkedin and normalize_url(linkedin) in existing_linkedin: return True
        return False
    
    valid_leads['is_dupe'] = valid_leads.apply(is_dupe, axis=1)
    final_leads = valid_leads[~valid_leads['is_dupe']].copy()
    
    # Internal Deduplication (in case same lead is in both batches)
    final_leads.drop_duplicates(subset=['linkedin'], inplace=True)
    # Also drop if email is present and duplicated
    # (Handling empty email strings carefully)
    # Actually, drop_duplicates on subset is enough if we prioritize one.
    
    # Manual Exclusion of known false positives
    final_leads = final_leads[~final_leads['company_name'].str.contains("20th century studios", case=False)]
    
    print(f"Final Unique Leads: {len(final_leads)}")
    
    # 6. Save top 20
    final_leads = final_leads.head(20)
    
    columns = ["full_name", "company_name", "job_title", "email", "linkedin"]
    final_leads = final_leads[columns].rename(columns={
        "full_name": "Name",
        "company_name": "Company",
        "job_title": "Role",
        "email": "Email",
        "linkedin": "LinkedIn"
    })
    
    final_leads.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(final_leads)} to {OUTPUT_FILE}")
    print(final_leads.to_string(index=False))

if __name__ == "__main__":
    main()
