
import json
import csv
import os

# Find the latest verified or enriched file
def find_latest_json():
    # Only look at files from today? 
    # Or just list dir and sort
    files = [f for f in os.listdir(".tmp") if f.endswith(".json") and "powerhouse" in f]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(".tmp", x)), reverse=True)
    if files:
        return os.path.join(".tmp", files[0])
    return None

CSV_PATH = "marketing/prospects_batch_0104.csv"

def main():
    json_path = find_latest_json()
    if not json_path:
        print("No JSON file found in .tmp")
        return

    print(f"Converting {json_path} to CSV...")
    with open(json_path, 'r') as f:
        leads = json.load(f)

    if not leads:
        print("No leads in JSON.")
        return

    headers = ["Name", "First Name", "Last Name", "Title", "Company", "Email", "LinkedIn", "Location", "Website", "Status", "Personalized_Line_Context", "Warm/Cold"]
    
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for lead in leads:
            email = lead.get("email", "")
            if not email or "email_not_unlocked" in email:
                email = "" # Clear invalid email

            # For LinkedIn task, we keep them even if email is missing.
            # But for Email task, they are useless.
            # We will save them all.

            row = {
                "Name": lead.get("name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
                "First Name": lead.get("first_name", ""),
                "Last Name": lead.get("last_name", ""),
                "Title": lead.get("title", ""),
                "Company": lead.get("company_name") or lead.get("organization_name", ""),
                "Email": email,
                "LinkedIn": lead.get("linkedin_url", ""),
                "Location": lead.get("location", "") or f"{lead.get('city', '')}, {lead.get('state', '')}, {lead.get('country', '')}".strip(", "),
                "Website": lead.get("website_url", "") or lead.get("company_domain", ""),
                "Status": "Not Contacted",
                "Personalized_Line_Context": "",
                "Warm/Cold": "Cold" # Add this for outreach_manager compatibility
            }
            writer.writerow(row)
            valid_count += 1

    print(f"✅ Saved {valid_count} valid leads to {CSV_PATH}")

if __name__ == "__main__":
    main()
