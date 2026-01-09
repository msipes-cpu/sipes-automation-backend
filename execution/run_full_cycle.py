import sys
import json
import argparse
import subprocess
import os
from proposal_manager import get_next_proposal_number

# Scripts
GENERATE_SCRIPT = "execution/generate_proposal.py"
DOCUSEAL_SCRIPT = "execution/docuseal_client.py"
EMAIL_SCRIPT = "execution/email_client.py"
GHL_SCRIPT = "execution/ghl_client.py"
DRIVE_SCRIPT = "execution/drive_client.py"

def run_command(cmd):
    print(f"\nRunning: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        raise e

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to JSON data")
    args = parser.parse_args()

    # 1. Get Proposal Number
    prop_num = get_next_proposal_number()
    print(f"Assigning Proposal Number: {prop_num}")

    # 2. Update Data with Number
    try:
        with open(args.data, 'r') as f:
            data = json.load(f)
        
        data['proposal_number'] = prop_num
        client_email = data.get('client_email', 'mikesipes107@gmail.com') # Fallback for now based on context
        client_name = data.get('client_name', 'Client')
        project_title = data.get('project_title', 'Project')

        # Save temporarily
        temp_data_path = f".tmp/proposal_data_{prop_num}.json"
        with open(temp_data_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Data Error: {e}")
        return

    # 3. Generate PDF
    print(f"--- Generating PDF ({prop_num}) ---")
    run_command(f"python3 {GENERATE_SCRIPT} --data {temp_data_path}")
    
    # Identify PDF Path (Standard naming in generate_proposal.py: Proposal_<SafeClientName>.pdf)
    safe_name = "".join([c for c in client_name if c.isalpha() or c.isdigit()]).rstrip()
    pdf_path = f".tmp/Proposal_{safe_name}.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Critical Error: PDF not found at {pdf_path}")
        return

    # 4. DocuSeal
    print(f"--- Creating Signing Link ---")
    # docuseal_client.py output: "Signing Link: https://..." on last line usually
    ds_out = run_command(f"python3 {DOCUSEAL_SCRIPT} --pdf {pdf_path} --emails {client_email} --no-email")
    
    link = None
    for line in ds_out.split('\n'):
        if "Signing Link:" in line:
            link = line.split("Signing Link:")[1].strip()
            break
            
    if not link:
        print("Error: Could not extract signing link.")
        return
        
    print(f"Got Link: {link}")

    # 5. Google Drive Upload (Best Effort)
    drive_link = "N/A"
    try:
        print(f"--- Uploading to Drive ---")
        drive_out = run_command(f"python3 {DRIVE_SCRIPT} {pdf_path}")
        # Extract link if possible
        for line in drive_out.split('\n'):
            if "Link:" in line:
                drive_link = line.split("Link:")[1].strip()
    except Exception as e:
        print(f"Drive Upload Failed (Non-critical): {e}")

    # 6. GHL Update (Best Effort)
    try:
        print(f"--- Updating GHL CRM ---")
        run_command(f"python3 {GHL_SCRIPT} --email {client_email} --link {link} --number {prop_num}")
    except Exception as e:
        print(f"GHL Update Failed (Non-critical): {e}")

    # 7. Send Email
    print(f"--- Sending Email ---")
    subject = f"Proposal for {client_name} - {project_title} - Sipes Automation"
    body = f"""Hi {client_name.split()[0]},

Great speaking with you earlier. Please find attached the updated proposal ({prop_num}) for the {project_title} project, incorporating the new terms and scope we discussed.

As agreed, we will focus on:
- Automated WhatsApp Order Ingestion
- Notion & Xero Integration
- OCR for Delivery Notes

Payment Terms:
- $400.00 Deposit (Due Now)
- $400.00 Upon Completion

Next Steps:
1. Review the attached proposal.
2. Click the 'Pay Deposit Now' link inside the PDF.
3. Sign the document here: {link}

Timeline:
Targeting Monday, Jan 5th.

Let me know if you have any questions!

Best,
Michael Sipes
Sipes Automation
"""
    # Use proper escaping for body in subprocess? better to pass file or rely on python lib
    # subprocess might break with newlines in body arg.
    # Let's import email_client directly if possible or be careful.
    # actually, passing long multiline strings in shell is risky.
    # writing body to temp file.
    body_file = f".tmp/email_body_{prop_num}.txt"
    with open(body_file, 'w') as f:
        f.write(body)
        
    # use email_client.py but modified to read body from file? NO, it takes string.
    # Let's wrap body in quotes carefully or import.
    # importing is safer.
    
    from email_client import send_email
    sent = send_email(client_email, subject, body, attachment_path=pdf_path)
    
    if sent:
        print("\nSUCCESS: Email Sent.")
    else:
        print("\nFAILURE: Email Failed.")

    print(f"Summary:\nProposal: {prop_num}\nLink: {link}\nDrive: {drive_link}")

if __name__ == "__main__":
    main()
