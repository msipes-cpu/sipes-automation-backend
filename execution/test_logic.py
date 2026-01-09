import re

def normalize_url(url):
    if not url:
        return ""
    return url.strip().rstrip("/").replace("https://", "").replace("http://", "").replace("www.", "")

def main():
    row = {
        'company_name': 'Brand Fuel',
        'first_name': 'Robert',
        'last_name': 'Fiveash',
        'full_name': 'Robert Fiveash',
        'linkedin': 'https://www.linkedin.com/in/robert-fiveash-0288483',
        'email': 'robertf@brandfuel.com',
        'job_title': 'President/co-owner',
        'company_description': 'Brand Fuel is a Free-Spirited Brand Merchandising Agency with a Focus on Sustainability.',
        'industry': 'Marketing & Advertising',
        'keywords': 'shipping, logistics & supply chain, marketing & advertising, environmental services, renewables & environment, crm, enterprise software, enterprises, computer software, information technology & services, b2b, events services'
    }

    print("Testing Brand Fuel logic...")
    
    existing_identifiers = set()
    new_leads = []
    
    # Logic copied from script
    
    # DEBUG TRACE
    debug_mode = True
    print(f"TRACE: Found Brand Fuel! LinkedIn: {row.get('linkedin')}")
    
    email = row.get("email", "").strip()
    linkedin = row.get("linkedin", "").strip()
    
    if not linkedin:
        print("Failed: No LinkedIn")
        return

    # Filter by Role
    role = row.get("job_title", "").strip()
    if not role:
        print("Failed: No Role")
        return
        
    role_lower = role.lower()
    target_roles = ["owner", "president", "ceo", "founder", "partner", "principal", "chief executive"]
    if not any(r in role.lower() for r in target_roles):
        if debug_mode: print(f"TRACE: Failed Role Check: {role}")
        return
    
    # Negative Role Filter
    bad_roles = ["product owner", "project owner", "process owner", "business owner analyst", "franchise owner", "sales development"]
    if any(br in role_lower for br in bad_roles):
        if debug_mode: print(f"TRACE: Rejected Negative Role: {role}")
        return

    # Determine Industry / Agency Relevance First
    company_desc = row.get("company_description", "").lower()
    industry = row.get("industry", "").lower()
    keywords = row.get("keywords", "").lower()
    combined_text = f"{company_desc} {industry} {keywords} {row.get('company_name', '').lower()}"
    
    allowed_industries = ["marketing & advertising", "marketing and advertising", "online media", "graphic design", "public relations and communications"]
    is_explicit_marketing = any(ai in industry for ai in allowed_industries)
    print(f"Is Explicit Marketing: {is_explicit_marketing}")

    # FATAL Negatives (Always exclude)
    fatal_negatives = [
        "insurance", "real estate", "home care", "healthcare", "senior care", 
        "fitness", "gym", "dental", "medical", "construction", "cleaning", 
        "staffing", "recruiting", "mortgage", "bank", "financial", "investment",
        "pest control", "plumbing", "hvac", "roofing", "auto", "car",
        "trucking", "dairy", "food", "restaurant", "therapy", "counseling", 
        "nursing", "pharmacy"
    ]
    
    found_fatal = False
    for ns in fatal_negatives:
        pattern = r'\b' + re.escape(ns) + r'\b'
        if re.search(pattern, combined_text):
            found_fatal = ns
            break
    
    if found_fatal:
        print(f"Rejected {row.get('company_name')} due to fatal signal: {found_fatal}")
        if debug_mode: print(f"TRACE: Fatal signal {found_fatal}")
        return

    # SUSPICIOUS Negatives (Exclude UNLESS explicit marketing)
    suspicious_negatives = ["shipping", "logistics", "manufacturing", "wholesale", "retail", "franchise"]
    
    found_suspicious = False
    if not is_explicit_marketing:
        for ns in suspicious_negatives:
            pattern = r'\b' + re.escape(ns) + r'\b'
            if re.search(pattern, combined_text):
                found_suspicious = ns
                break
    
    if found_suspicious:
        # DEBUG
        # print(f"Rejected {row.get('company_name')} due to suspicious signal: {found_suspicious}")
        return

    # Positive Signals pass
    
    # Check for duplicates
    is_duplicate = False
    if email and email.lower() in existing_identifiers:
        print(f"Duplicate email: {email}")
        is_duplicate = True
    if linkedin and normalize_url(linkedin) in existing_identifiers:
        print(f"Duplicate LinkedIn: {linkedin}")
        is_duplicate = True
    
    if is_duplicate:
        return
    
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
    if debug_mode: print(f"TRACE: Added {full_name} to new_leads. Count: {len(new_leads)}")

if __name__ == "__main__":
    main()
