import sys
import os
import logging
import json
from datetime import datetime

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.utils import load_config, setup_logging
from execution.generate_client_report import generate_client_report
from execution.send_email_report import send_email_report
from execution.update_google_sheet import update_google_sheet
from execution.send_slack_notification import send_slack_notification

def main():
    setup_logging()
    logging.info("Starting InboxBench Automation Workflow (V2+Resend)...")

    config = load_config()
    if not config:
        sys.exit(1)

    api_key = config.get("instantly_api_key")
    client_tags = config.get("client_tags", [])
    
    full_report = {
        "date": datetime.now().isoformat(),
        "client_reports": []
    }
    
    logging.info(f"Processing {len(client_tags)} clients...")
    for client_profile in client_tags:
        try:
            client_report = generate_client_report(api_key, client_profile, None)
            full_report["client_reports"].append(client_report)
        except Exception as e:
            logging.error(f"Error generating report for {client_profile.get('client_name')}: {e}")

    # Generate Outputs
    if config.get("reporting_email"):
        logging.info("Sending Email Report...")
        # Updated to pass resend_api_key
        send_email_report(
            config.get("resend_api_key"),
            config.get("reporting_email"),
            config.get("agency_name"),
            full_report
        )
        
    if config.get("google_sheet_id") and config.get("google_sheet_id") != "YOUR_GOOGLE_SHEET_ID":
        logging.info("Updating Google Sheet...")
        update_google_sheet(
            config.get("google_sheet_id"),
            full_report
        )
        
    if config.get("slack_webhook_url") and config.get("slack_webhook_url") != "YOUR_SLACK_WEBHOOK_URL":
        logging.info("Sending Slack Notification...")
        send_slack_notification(
            config.get("slack_webhook_url"),
            full_report
        )

    logging.info("Workflow completed.")

if __name__ == "__main__":
    main()
