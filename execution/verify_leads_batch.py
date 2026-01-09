
import csv
import argparse
import json
import sys
# Add current directory to path to allow import
sys.path.append(".")
from execution.verify_leads import process_leads

def main():
    parser = argparse.ArgumentParser(description="Verify leads in CSV batch")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    print(f"Reading {args.input}...")
    with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        leads = list(reader)
    
    print(f"Verifying {len(leads)} leads...")
    # process_leads expects list of dicts.
    # It modifies them in place or returns new list.
    verified_leads = process_leads(leads)
    
    # Determined fieldnames.
    # verification_status and verification_details (as str) should be added.
    if verified_leads:
        fieldnames = list(verified_leads[0].keys())
        # Ensure new fields are in header
        for f in ["verification_status", "verification_details"]:
            if f not in fieldnames:
                fieldnames.append(f)
    else:
        fieldnames = []

    print(f"Writing {len(verified_leads)} results to {args.output}...")
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for lead in verified_leads:
            # Flatten details to string for CSV if needed, or just let DictWriter handle it (might be ugly)
            # Better to dump details to JSON string
            if "verification_details" in lead and isinstance(lead["verification_details"], dict):
                lead["verification_details"] = json.dumps(lead["verification_details"])
            writer.writerow(lead)

if __name__ == "__main__":
    main()
