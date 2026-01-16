import os
import requests
import argparse
import json
import time
import sys
from typing import List, Dict, Any

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
from dotenv import load_dotenv

load_dotenv()

# API Keys and Endpoints
MILLION_VERIFIER_API_KEY = os.getenv("MILLION_VERIFIER_API_KEY")
MILLION_VERIFIER_URL = "https://api.millionverifier.com/api/v3/"

BOUNCEBAN_API_KEY = os.getenv("BOUNCEBAN_API_KEY")
BOUNCEBAN_URL = "https://api.bounceban.com/v1/verify/single"

REOON_API_KEY = os.getenv("REOON_API_KEY")
REOON_URL = "https://emailverifier.reoon.com/api/v1/verify"

ANYMAILFINDER_API_KEY = os.getenv("ANYMAILFINDER_API_KEY")
ANYMAILFINDER_URL = "https://api.anymailfinder.com/v5.1/verify-email"

STRICT_MODE = True # User requested strict Million Verifier only

def verify_million_verifier(email: str, session=None) -> Dict[str, Any]:
    """Verifies email using Million Verifier."""
    if not MILLION_VERIFIER_API_KEY:
        return {"result": "skipped", "error": "MILLION_VERIFIER_API_KEY not set"}

    params = {
        "api": MILLION_VERIFIER_API_KEY,
        "email": email,
        "timeout": 10
    }
    try:
        req = session if session else requests
        response = req.get(MILLION_VERIFIER_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"result": "error", "error": str(e)}

def verify_bounceban(email: str, session=None) -> Dict[str, Any]:
    # ... (unchanged) ...
    """Verifies email using BounceBan (good for catch-alls)."""
    if not BOUNCEBAN_API_KEY:
        return {"result": "skipped", "error": "BOUNCEBAN_API_KEY not set"}

    params = {"email": email}
    headers = {"Authorization": BOUNCEBAN_API_KEY} 
    params["api_key"] = BOUNCEBAN_API_KEY
    
    try:
        req = session if session else requests
        response = req.get(BOUNCEBAN_URL, params=params)
        if response.status_code != 200:
             return {"result": "error", "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {"result": "error", "error": str(e)}

def verify_reoon(email: str, session=None) -> Dict[str, Any]:
    # ... (unchanged) ...
    """Verifies email using Reoon."""
    if not REOON_API_KEY:
        return {"result": "skipped", "error": "REOON_API_KEY not set"}

    params = {
        "email": email,
        "key": REOON_API_KEY,
        "mode": "quick" # or 'power'
    }
    try:
        req = session if session else requests
        response = req.get(REOON_URL, params=params)
        if response.status_code != 200:
             return {"result": "error", "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {"result": "error", "error": str(e)}

def verify_anymailfinder(email: str, session=None) -> Dict[str, Any]:
    # ... (unchanged) ...
    """Verifies email using Anymail Finder."""
    if not ANYMAILFINDER_API_KEY:
        return {"result": "skipped", "error": "ANYMAILFINDER_API_KEY not set"}

    headers = {
        "Authorization": ANYMAILFINDER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"email": email}

    try:
        req = session if session else requests
        response = req.post(ANYMAILFINDER_URL, headers=headers, json=payload)
        if response.status_code != 200:
             return {"result": "error", "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {"result": "error", "error": str(e)}

def verify_email_tiered(email: str, session=None) -> Dict[str, Any]:
    """
    Verifies email using tiered approach:
    1. Million Verifier
    2. If catch_all/unknown -> BounceBan (if avail) or Reoon (if avail)
    """
    # Step 1: Standard (Million Verifier)
    mv_result = verify_million_verifier(email, session=session)
    result_status = mv_result.get("result")
    
    if result_status == 'ok':
        result_status = 'safe'
    
    final_result = {
        "email": email,
        "mv_status": result_status,
        "mv_details": mv_result,
        "final_status": result_status,
        "verification_source": "million_verifier"
    }

    # IMPORTANT: If STRICT_MODE is on, we STOP here. No upgrading catch_alls.
    if STRICT_MODE:
        return final_result

    # If it's safe/invalid, we are done.
    # If catch_all, unknown, skipped, or error, try tier 2 (BounceBan/Reoon)
    if result_status in ["catch_all", "unknown", "skipped", "error"]:
        # Try BounceBan first
        if BOUNCEBAN_API_KEY:
            bb_result = verify_bounceban(email, session=session)
            bb_status = bb_result.get("result") # normalize this field from bb response
            if "status" in bb_result:
                bb_status = bb_result["status"]
            
            final_result["bb_status"] = bb_status
            final_result["bb_details"] = bb_result
            final_result["final_status"] = bb_status # Update final status
            final_result["verification_source"] = "bounceban"
            
            # Update final status if BB gives a decisive answer
            if bb_status == "valid":
                final_result["final_status"] = "safe" # Upgrade to safe
            elif bb_status == "invalid":
                final_result["final_status"] = "invalid"

        elif REOON_API_KEY:
            re_result = verify_reoon(email, session=session)
            re_status = re_result.get("status") # Reoon uses 'status'
            
            final_result["reoon_status"] = re_status
            final_result["reoon_details"] = re_result
            final_result["verification_source"] = "reoon"
            
            if re_status == "safe" or re_status == "valid":
                 final_result["final_status"] = "safe"
            elif re_status == "invalid":
                 final_result["final_status"] = "invalid"

        elif ANYMAILFINDER_API_KEY:
            am_result = verify_anymailfinder(email, session=session)
            # Anymailfinder usually returns 'status' (e.g. 'valid', 'invalid', 'unknown') or 'email_status'
            am_status = am_result.get("status") or am_result.get("email_status")
            
            final_result["am_status"] = am_status
            final_result["am_details"] = am_result
            final_result["verification_source"] = "anymailfinder"
            
            if am_status == "valid":
                 final_result["final_status"] = "safe"
            elif am_status == "invalid":
                 final_result["final_status"] = "invalid"
            # If unknown, final_status remains 'catch_all' or 'unknown' from MV

    return final_result

def process_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Iterates through leads and verifies their emails."""
    verified_leads = []
    log(f"Verifying {len(leads)} leads...")
    
    for lead in leads:
        email = lead.get("email") or lead.get("work_email")
        if not email:
            log(f"Skipping lead {lead.get('name', 'Unknown')} - No email found.")
            lead["verification_status"] = "no_email"
            verified_leads.append(lead)
            continue

        result = verify_email_tiered(email)
        
        # Update lead with verification results
        lead["verification_status"] = result["final_status"]
        lead["verification_details"] = result
        
        log(f"Verified {email}: {result['final_status']} (Source: {result['verification_source']})")
        
        verified_leads.append(lead)
        time.sleep(0.1) 
        
    return verified_leads

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify leads with tiered verification")
    parser.add_argument("--input_file", help="Path to JSON file containing leads")
    parser.add_argument("--input_json", help="JSON string of leads")
    
    args = parser.parse_args()
    
    leads = []
    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                leads = json.load(f)
        except Exception as e:
            log(f"Error reading file: {e}")
            exit(1)
    elif args.input_json:
        try:
            leads = json.loads(args.input_json)
        except Exception as e:
            log(f"Error parsing JSON: {e}")
            exit(1)
    else:
        log("No input provided.")
        exit(1)

    try:
        verified_results = process_leads(leads)
        print(json.dumps(verified_results, indent=2))
    except Exception as e:
        log(f"Unexpected error: {e}")
        exit(1)
