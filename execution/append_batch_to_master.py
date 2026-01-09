
import csv
import os

BATCH_FILE = "marketing/prospects_batch_0104.csv"
MASTER_FILE = "marketing/first_five_tracking.csv"

def main():
    if not os.path.exists(BATCH_FILE):
        print("Batch file not found.")
        return

    print(f"Reading batch from {BATCH_FILE}...")
    with open(BATCH_FILE, 'r') as f:
        reader = csv.DictReader(f)
        batch_leads = list(reader)
        
    print(f"Found {len(batch_leads)} new leads.")
    
    # Read master headers
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, 'r') as f:
            reader = csv.DictReader(f)
            master_fieldnames = reader.fieldnames
            # Check if master has leads to avoid duplicates?
            # Ideally verify by email.
            master_emails = set()
            for row in reader:
                if row.get("Email"):
                    master_emails.add(row["Email"])
    else:
        master_fieldnames = list(batch_leads[0].keys())
        master_emails = set()

    # ensure all batch fields are in master
    for field in batch_leads[0].keys():
        if field not in master_fieldnames:
            master_fieldnames.append(field)

    new_leads = []
    for lead in batch_leads:
        email = lead.get("Email")
        if email and email not in master_emails:
            new_leads.append(lead)
        elif not email:
            # Maybe LinkedIn only lead?
            new_leads.append(lead) # Add anyway?
        else:
            print(f"Skipping duplicate: {email}")

    if new_leads:
        print(f"Appending {len(new_leads)} unique leads to master...")
        with open(MASTER_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=master_fieldnames)
            # If file was empty/new, write header? 
            # We opened in 'a'. If it didn't exist, we should 'w'.
            # But assume it exists based on previous tasks.
            # DictWriter doesn't write header automatically in append.
            writer.writerows(new_leads)
        print("Done.")
    else:
        print("No new unique leads to append.")

if __name__ == "__main__":
    main()
