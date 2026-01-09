import os
import requests
import json
import base64
import argparse

# Load env vars
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("DOCUSEAL_API_KEY")
API_URL = "https://api.docuseal.com/submissions/pdf"

def send_for_signature(pdf_path, signers, subject=None, message_body=None, send_email=True):
    if not API_KEY:
        print("Error: DOCUSEAL_API_KEY not found in .env")
        return None

    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None
        
    # Check for metadata
    fields = []
    metadata_path = ".tmp/pdf_metadata.json"
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                meta = json.load(f)
                # Meta contains page, sig_y, date_y, col_x, col_width (in mm)
                # DocuSeal areas are usually pixels at 72dpi or similar? No, DocuSeal API docs use distinct units?
                # Actually most e-sign APIs use points (1/72 inch). FPDF uses mm.
                # 1 mm = 2.83465 points.
                MM_TO_PT = 2.83465
                
                page = meta['page']
                w_mm = meta['col_width']
                
                # --- Client Fields ---
                client_sig_y = meta.get('client_sig_y', meta.get('sig_y', 0))
                client_date_y = meta.get('client_date_y', meta.get('date_y', 0))
                client_x = meta.get('client_col_x', meta.get('col_x', 110))

                fields.append({
                    "name": "Client Signature",
                    "type": "signature",
                    "role": "Client", 
                    "required": True,
                    "areas": [{"x": client_x * MM_TO_PT, "y": (client_sig_y - 15) * MM_TO_PT, "w": w_mm * MM_TO_PT, "h": 15 * MM_TO_PT, "page": page}]
                })
                fields.append({
                    "name": "Date",
                    "type": "date",
                    "role": "Client",
                    "required": True,
                    "areas": [{"x": client_x * MM_TO_PT, "y": (client_date_y - 10) * MM_TO_PT, "w": w_mm * MM_TO_PT, "h": 10 * MM_TO_PT, "page": page}]
                })
                
                # --- Sipes Automation Fields ---
                if 'sipes_sig_y' in meta:
                    sipes_sig_y = meta['sipes_sig_y']
                    sipes_date_y = meta['sipes_date_y']
                    sipes_x = meta['sipes_col_x']
                    
                    fields.append({
                        "name": "Sipes Signature",
                        "type": "signature",
                        "role": "Sipes Automation", 
                        "required": True,
                        "areas": [{"x": sipes_x * MM_TO_PT, "y": (sipes_sig_y - 15) * MM_TO_PT, "w": w_mm * MM_TO_PT, "h": 15 * MM_TO_PT, "page": page}]
                    })
                    fields.append({
                        "name": "Sipes Date",
                        "type": "date",
                        "role": "Sipes Automation",
                        "required": True,
                        "areas": [{"x": sipes_x * MM_TO_PT, "y": (sipes_date_y - 10) * MM_TO_PT, "w": w_mm * MM_TO_PT, "h": 10 * MM_TO_PT, "page": page}]
                    })

                print("Added signature fields from metadata.")
        except Exception as e:
            print(f"Failed to load metadata: {e}")

    # Read and Encode PDF
    with open(pdf_path, "rb") as pdf_file:
        encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')

    filename = os.path.basename(pdf_path)

    # Payload
    payload = {
        "documents": [
            {
                "name": filename,
                "file": encoded_pdf,
                "fields": fields 
            }
        ],
        "submitters": signers
    }
    
    # Assign Roles intelligently if fields exist
    # Logic: If email contains "sipesautomation.com", assign 'Sipes Automation', else 'Client'
    if fields:
        for signer in payload["submitters"]:
            if "sipesautomation.com" in signer["email"]:
                signer["role"] = "Sipes Automation"
            else:
                signer["role"] = "Client"

    if not send_email:
        # If send_email is False, we tell API not to send it.
        # However, checking API docs, 'send_email' might be a top-level or submitter-level preference.
        # Based on search, it often goes into 'submitters' -> 'preferences' OR logic.
        # But search said "at submission level... include send_email: false".
        # Let's add it to the 'message' block or top level if applicable, but DocuSeal structure varies.
        # Search said: "preferences: { send_email: false }" in submitter or submission.
        # Let's try adding it to each submitter first to be safe, as we saw "preferences" in the submitter response earlier.
        for signer in payload["submitters"]:
            signer["preferences"] = {"send_email": False}
        # Also try top-level if supported by some endpoints
        # payload["send_email"] = False # Warning: Check API if this is valid. 
        # Search result [1] said "When creating a new submission... include send_email: false in the request body".
        # So we add it to root.
        payload["send_email"] = False

    if subject or message_body:
        payload["message"] = {}
        if subject:
            payload["message"]["subject"] = subject
        if message_body:
            payload["message"]["body"] = message_body

    headers = {
        "X-Auth-Token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        print(f"Uploading {filename} to DocuSeal...")
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Success! Submission ID: {data[0].get('id') if isinstance(data, list) else data.get('id')}")
        
        # Extract and print link if available
        # Structure: list of submitters in response
        if isinstance(data, list) and len(data) > 0 and 'slug' in data[0]:
             link = f"https://docuseal.com/s/{data[0]['slug']}"
             print(f"Signing Link: {link}")
        elif isinstance(data, dict) and 'submitters' in data:
             # Check submitters list
             for s in data['submitters']:
                 if 'slug' in s:
                     print(f"Signing Link: https://docuseal.com/s/{s['slug']}")

        # print(f"Response Dump: {json.dumps(data, indent=2)}")
        return data
    except Exception as e:
        print(f"DocuSeal API Failed: {e}")
        if 'response' in locals():
             print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send PDF to DocuSeal")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--emails", required=True, help="Comma separated list of signer emails")
    
    parser.add_argument("--subject", help="Email subject")
    parser.add_argument("--message", help="Email body message")
    parser.add_argument("--no-email", action="store_true", help="Do not send email via DocuSeal")
    
    args = parser.parse_args()
    
    signer_list = [{"email": email.strip()} for email in args.emails.split(",")]
    
    # Fix newline characters
    message = args.message.replace('\\n', '\n') if args.message else None
    
    send_for_signature(args.pdf, signer_list, args.subject, message, send_email=not args.no_email)
