
import csv
import os
import argparse

MASTER_FILE = "marketing/first_five_tracking.csv"

def main():
    parser = argparse.ArgumentParser(description="Deduplicate leads against master file")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()

    # Load master emails
    master_emails = set()
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("Email", "").strip().lower()
                if email:
                    master_emails.add(email)
    
    print(f"Loaded {len(master_emails)} existing emails from master.")

    # Process input
    unique_leads = []
    skipped_count = 0
    
    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            email = row.get("email") or row.get("Email")
            if email:
                email_norm = email.strip().lower()
                if email_norm in master_emails:
                    skipped_count += 1
                    continue
                unique_leads.append(row)
            else:
                # If no email, keep it? Or skip?
                # User wants email leads. Probably skip if no email, but Apify might return some without.
                # Let's keep distinct rows even if no email for now, assuming we might find it later?
                # Actually, user wants "200 leads... verify email". So we need email.
                # Apify actor claimed "includeEmails": True.
                unique_leads.append(row)

    print(f"Processed {len(unique_leads) + skipped_count} leads.")
    print(f"Skipped {skipped_count} duplicates.")
    print(f"Retained {len(unique_leads)} unique leads.")

    # Write output
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_leads)
    
    print(f"Saved to {args.output}")

if __name__ == "__main__":
    main()
