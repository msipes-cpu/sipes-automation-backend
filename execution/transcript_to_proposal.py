#!/usr/bin/env python3
"""
Transcript to Proposal Engine
-----------------------------
Reads a meeting transcript, uses Anthropic Claude to extract structure,
and calls generate_proposal.py to create the PDF.
Then Uploads to Drive, Updates GHL, and Emails User.

Usage:
    python3 execution/transcript_to_proposal.py --transcript <path> [--client_name <name>] [--email <client_email>]
"""
import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Helpers
try:
    from execution.gdrive_manager import get_drive_service, find_or_create_folder, upload_file
    from execution.ghl_client import update_ghl_contact
    from execution.email_client import send_email
except ImportError:
    sys.path.append(os.getcwd())
    from execution.gdrive_manager import get_drive_service, find_or_create_folder, upload_file
    from execution.ghl_client import update_ghl_contact
    from execution.email_client import send_email

try:
    import anthropic
except ImportError:
    print("Error: Anthropic module not found. Please install: pip install anthropic")
    sys.exit(1)

load_dotenv()

SYSTEM_PROMPT = """
You are a senior proposal writer for Sipes Automation. 
Your goal is to extract key information from a sales meeting transcript and structure it into a JSON format for a proposal.

Our Services:
- Speed-to-Lead Installation (AI Voice/SMS, CRM Sync)
- Workflow Automation (n8n, Make.com)
- Database/CRM Setup (Airtable, Smartlead, HubSpot)

Your Output MUST be strictly valid JSON with this structure:
{
  "client_name": "Extracted Name",
  "client_company": "Extracted Company",
  "project_title": "Short Descriptive Title (e.g. 'Speed-to-Lead Implementation')",
  "problem_statement": "Concise paragraph describing the current inefficiency or pain point.",
  "proposed_solution": "Concise paragraph describing the automated solution.",
  "scope_of_work": [
    {"title": "Deliverable 1", "description": "Details..."},
    {"title": "Deliverable 2", "description": "Details..."}
  ],
  "investment": [
    {"item": "Implementation Fee", "cost": 2500},
    {"item": "Software Setup", "cost": 500}
  ],
  "timeline": "e.g. 2 weeks",
  "access_requirements": ["List of systems needed e.g. CRM access"],
  "exclusions": ["List of things NOT included"],
  "relevant_projects": [
      {"title": "Similar Project 1", "description": "Brief description of similar work done."}
  ]
}

If specific costs aren't mentioned, use reasonable estimates for our services:
- Speed-to-Lead: $2,500
- Custom Automation: $1,500 - $5,000 depending on complexity.

Be persuasive but professional.
"""

def extract_proposal_data(transcript_path, client_name_override=None):
    if client_name_override == "MOCK_MODE":
        return {
            "client_name": "Mock Client",
            "client_company": "Mock Corp",
            "project_title": "Mock Proposal",
            "problem_statement": "Mock Problem",
            "proposed_solution": "Mock Solution",
            "scope_of_work": [{"title": "Item 1", "description": "Desc"}],
            "investment": [{"item": "Service", "cost": 100}],
            "timeline": "1 Week"
        }

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    with open(transcript_path, 'r') as f:
        transcript_text = f.read()

    user_prompt = f"Transcript:\n{transcript_text[:15000]}"
    if client_name_override:
        user_prompt += f"\n\nAdditional Context: The client name is {client_name_override}."

    print("⏳ Extracting proposal structure with Claude...")
    
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    content = message.content[0].text
    try:
        # Robust JSON extraction
        json_start = content.find('{')
        json_end = content.rfind('}')
        
        if json_start != -1 and json_end != -1:
            json_str = content[json_start:json_end+1]
        else:
            json_str = content
            
        data = json.loads(json_str)
        data['j_number'] = "J" + datetime.now().strftime("%y%m%d")
        data['revision'] = 1
        return data
    except json.JSONDecodeError:
        print("Error: Failed to parse Claude response as JSON")
        print(content)
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate Proposal from Transcript")
    parser.add_argument("--transcript", required=True, help="Path to transcript file")
    parser.add_argument("--client_name", help="Override Client Name")
    parser.add_argument("--email", help="Client Email (for GHL lookup)")
    parser.add_argument("--dry_run", action="store_true", help="Skip GHL/Email steps")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.transcript):
        print(f"Error: File not found {args.transcript}")
        sys.exit(1)
        
    # 1. Extract Data
    data = extract_proposal_data(args.transcript, args.client_name)
    if not data: sys.exit(1)
        
    temp_json = f".tmp/proposal_data_{datetime.now().strftime('%H%M%S')}.json"
    with open(temp_json, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Data extracted to {temp_json}")

    # 2. Generate PDF
    print("🚀 Generating PDF...")
    cmd = ["python3", "execution/generate_proposal.py", "--data", temp_json]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ PDF Generation Error: {result.stderr}")
        sys.exit(1)
        
    print(result.stdout)
    
    # 3. Find Generated PDF Path
    # generate_proposal prints: "Proposal generated: .tmp/filename.pdf"
    pdf_path = None
    for line in result.stdout.split('\n'):
        if "Proposal generated:" in line:
            pdf_path = line.split("Proposal generated:")[1].strip()
            break
            
    if not pdf_path or not os.path.exists(pdf_path):
        print("❌ Could not locate generated PDF.")
        sys.exit(1)

    if args.dry_run:
        print("[DRY RUN] PDF generated. Skipping Upload/GHL/Email.")
        return

    # 4. Upload to Drive
    print("\n☁️  Uploading to Google Drive...")
    try:
        service = get_drive_service()
        folder_id, _ = find_or_create_folder(service, "Proposals Generated")
        _, web_link = upload_file(service, pdf_path, folder_id)
        print(f"✓ Uploaded: {web_link}")
    except Exception as e:
        print(f"⚠️ Drive Upload Failed: {e}")
        web_link = "Upload Failed"

    # 5. Update GHL
    client_email = args.email
    if not client_email:
        print("⚠️  No --email provided. Skipping GHL contact update.")
    else:
        print("\n🟢 Updating GHL Opportunity...")
        # Note: update_ghl_contact adds a NOTE. 
        # Ideally we'd Find/Create Opportunity then add Note/File.
        # Current helper just adds a note to the contact.
        success = update_ghl_contact(client_email, web_link, data['j_number'])
        if success: print("✓ GHL Updated")
        else: print("⚠️  GHL Update Failed")

    # 6. Email User (You)
    me_email = os.getenv("REPORT_RECIPIENT_EMAIL") or os.getenv("SMTP_EMAIL")
    if me_email:
        print(f"\n📧 Emailing Proposal to {me_email}...")
        subject = f"Proposal Generated: {data['client_company']}"
        body = (
            f"Proposal for {data['client_name']} ({data['client_company']}) is ready.\n\n"
            f"Drive Link: {web_link}\n"
            f"Total Investment: ${sum(i['cost'] for i in data.get('investment', [])):,.2f}"
        )
        send_email(me_email, subject, body, attachment_path=pdf_path)
    else:
        print("⚠️  No recipient email found for notification.")

    print("\n✨ Workflow Complete!")

if __name__ == "__main__":
    main()
