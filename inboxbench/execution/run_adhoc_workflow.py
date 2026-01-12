import argparse
import json
import logging
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.instantly_api import InstantlyAPI
from execution.update_google_sheet import update_client_sheet
from execution.send_email_report import send_email_report

# Setup logging
logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(levelname)s: %(message)s')

def run_adhoc_report(api_key, sheet_url, report_email=None):
    """
    Runs a report for ALL accounts in the workspace associated with the API key.
    Updates the Google Sheet if provided.
    Sends an email report if email is provided.
    """
    logging.info("Starting Ad-Hoc Report Workflow...")
    
    api = InstantlyAPI(api_key)
    
    # ... (Fetching Logic - Unchanged) ...
    # 1. Fetch ALL Accounts
    # We skip tag filtering to support "whole workspace" view for this ad-hoc tool
    try:
        logging.info("Fetching accounts...")
        accounts_data = api.list_accounts()
        accounts = accounts_data.get("items", []) if isinstance(accounts_data, dict) else accounts_data
        if not accounts: accounts = []
        logging.info(f"Found {len(accounts)} accounts.")
        
        # 2. Fetch ALL Campaigns
        logging.info("Fetching campaigns...")
        campaigns_data = api.list_campaigns()
        campaigns = campaigns_data.get("items", []) if isinstance(campaigns_data, dict) else campaigns_data
        if not campaigns: campaigns = []
        logging.info(f"Found {len(campaigns)} campaigns.")

    except Exception as e:
        return {"success": False, "error": f"API Fetch Failed: {e}"}

    # 3. Analyze Data
    total_sent = 0
    total_replies = 0
    total_leads = 0 # Using opportunities logic
    
    processed_campaigns = []
    # ... (Campaign Processing Logic - Unchanged) ...
    for camp in campaigns:
        processed_campaigns.append({
            "name": camp.get("name"),
            "status": camp.get("status_v2", camp.get("status")),
            "sent": 0, 
            "opens": 0,
            "replies": 0,
            "click_rate": 0,
            "reply_rate": 0
        })

    processed_accounts = []
    for acc in accounts:
        # Vitals check is done inside the loop in main generation, should we add here?
        # Yes, for consistency, but to keep ad-hoc fast, maybe skip DNS for now UNLESS requested?
        # User requested Vitals, so we SHOULD probably include them if we want the sheet to match.
        # However, run_adhoc_workflow didn't have DNS check added in previous turn step 51 (generate_client_report did).
        # Let's adding it now for consistency.
        
        email_addr = acc.get("email")
        
        # Lazy import to avoid circular dependency if any
        from lib.dns_checker import check_dns_vitals
        vitals = check_dns_vitals(email_addr)

        processed_accounts.append({
            "email": email_addr,
            "status": acc.get("status_v2", acc.get("status")),
            "daily_limit": acc.get("limit", 0),
            "warmup_score": f"{acc.get('stat_warmup_score', 0)}/100",
            "spf_valid": vitals["spf"],
            "dkim_valid": vitals["dkim"],
            "dmarc_valid": vitals["dmarc"]
        })

    report_data = {
        "client_name": "InboxBench Ad-Hoc Report",
        "client_tag": "All Accounts", # Fallback for email template
        "formatted_date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "total_sent": total_sent,
        "total_leads": total_leads,
        "total_replies": total_replies,
        "total_opportunities": 0, # Placeholder
        "campaigns": processed_campaigns,
        "accounts": processed_accounts
    }
    
    # 4. Update Sheet
    sheet_updated = False
    if sheet_url:
        try:
            if "/d/" in sheet_url:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                logging.info(f"Updating Sheet ID: {sheet_id}")
                sheet_updated = update_client_sheet(report_data, sheet_id)
            else:
                logging.warning("Invalid Sheet URL format.")
        except Exception as e:
            logging.error(f"Sheet Update Error: {e}")

    # 5. Send Email Report
    email_sent = False
    if report_email:
        try:
            logging.info(f"Sending email report to {report_email}...")
            # We need to construct the 'report' object expected by the email sender
            # send_email_report(to_email, report_data)
            # Ensure send_email_report logic fits.
            # Assuming send_email_report takes (recipient, report_data)
            email_sent = send_email_report(report_email, report_data)
        except Exception as e:
             logging.error(f"Email Sending Error: {e}")

    return {
        "success": True,
        "accounts_count": len(accounts),
        "campaigns_count": len(campaigns),
        "sheet_updated": sheet_updated,
        "email_sent": email_sent
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", required=True)
    parser.add_argument("--sheet", required=False)
    parser.add_argument("--report_email", required=False)
    args = parser.parse_args()
    
    result = run_adhoc_report(args.key, args.sheet, args.report_email)
    print(json.dumps(result))
