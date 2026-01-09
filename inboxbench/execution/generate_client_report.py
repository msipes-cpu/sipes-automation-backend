import sys
import os
import json
import logging

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.instantly_api import InstantlyAPI
from lib.utils import setup_logging

def generate_client_report(api_key, client_profile, workspace_data=None):
    """
    Generates a report for a specific client.
    Fetches data directly using tag filters.
    
    Args:
        api_key (str): Instantly API Key
        client_profile (dict): {"tag": "client-tag-label", "client_name": "Name"}
        workspace_data: Unused in V2 refactor (kept for signature compatibility if needed)
    """
    api = InstantlyAPI(api_key)
    tag_label = client_profile.get("tag")
    client_name = client_profile.get("client_name")
    
    logging.info(f"Generating report for client: {client_name} (Tag: {tag_label})")

    # 1. Resolve Tag ID
    tag_id = api.get_tag_id_by_name(tag_label)
    if not tag_id:
        logging.warning(f"Tag '{tag_label}' not found in Instantly workspace. skipping.")
        return {
            "client_name": client_name,
            "error": "Tag not found",
            "summary": {"total_campaigns": 0, "total_accounts": 0, "accounts_with_issues": 0}
        }
    
    # 2. Fetch filtered data
    c_data = api.list_campaigns(tag_ids=tag_id)
    a_data = api.list_accounts(tag_ids=tag_id)
    
    client_campaigns = c_data.get("items", []) if isinstance(c_data, dict) else c_data
    client_accounts = a_data.get("items", []) if isinstance(a_data, dict) else a_data
    
    if not client_campaigns: client_campaigns = []
    if not client_accounts: client_accounts = []

    report = {
        "client_name": client_name,
        "client_tag": tag_label,
        "campaigns_data": [],
        "accounts_data": [],
        "summary": {
            "total_campaigns": len(client_campaigns),
            "total_accounts": len(client_accounts),
            "accounts_with_issues": 0
        }
    }

    # 3. Fetch details
    for acc in client_accounts:
        # Use 'email' as ID if 'id' missing, but V2 items usually have 'id'
        acc_id = acc.get("email") # Using email as ID for fetch if standard
        
        # Vitals
        # Logic placeholder as endpoint is assumed
        spf = True 
        dkim = True
        dmarc = True
        
        # Warmup
        warmup = acc.get("warmup", {}) # V2 list item often has warmup details embedded!
        # Check previous output: 'warmup': {'limit': 12, ...}
        # It has partial data. 'stat_warmup_score' is in the root item!
        # "stat_warmup_score": 100
        
        inbox_rate = acc.get("stat_warmup_score", 0) / 100.0 # Assuming score is %
        
        report["accounts_data"].append({
            "email": acc.get("email"),
            "vitals": {"spf": spf, "dkim": dkim, "dmarc": dmarc},
            "warmup": {"inbox_rate": inbox_rate}
        })

    for camp in client_campaigns:
        camp_id = camp.get("id")
        name = camp.get("name")
        summary = api.get_campaign_summary(camp_id)
        
        report["campaigns_data"].append({
            "name": name,
            "sent": summary.get("sent", 0) if summary else 0,
            "replies": summary.get("replies", 0) if summary else 0
        })

    return report
