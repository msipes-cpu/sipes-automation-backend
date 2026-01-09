
import csv
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        leads = list(reader)

    normalized_leads = []
    for lead in leads:
        # Map fields
        new_lead = {}
        
        # Name
        full_name = lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
        new_lead["Name"] = full_name
        
        # Company
        new_lead["Company"] = lead.get("company_name", "")
        
        # Role
        new_lead["Role"] = lead.get("job_title", "")
        
        # Email
        new_lead["Email"] = lead.get("email") or lead.get("Email", "")
        
        # Website
        new_lead["Website"] = lead.get("company_website", "")
        
        # LinkedIn
        new_lead["LinkedIn"] = lead.get("linkedin", "")
        
        # Verification Status (if present)
        new_lead["Verification_Status"] = lead.get("verification_status", "unknown")
        
        # Add default context if missing?
        # outreach_manager expects 'Personalized_Line_Context'
        company_desc = lead.get("company_description", "")
        if company_desc:
            # Maybe truncate?
            pass
        new_lead["Personalized_Line_Context"] = "I checked out your site and noticed you're doing interesting work."

        # Keep other fields?
        # Instantly might want them as variables.
        for k, v in lead.items():
            if k not in ["first_name", "last_name", "full_name", "company_name", "job_title", "email", "company_website", "linkedin"]:
                new_lead[k] = v
        
        normalized_leads.append(new_lead)

    if not normalized_leads:
        print("No leads to normalize.")
        return

    fieldnames = list(normalized_leads[0].keys())
    
    # Ensure our required keys are there
    for k in ["Name", "Company", "Role", "Email", "Personalized_Line_Context"]:
        if k not in fieldnames:
            fieldnames.append(k)

    print(f"Writing {len(normalized_leads)} normalized leads to {args.output}")
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(normalized_leads)

if __name__ == "__main__":
    main()
