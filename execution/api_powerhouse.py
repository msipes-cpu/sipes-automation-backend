#!/usr/bin/env python3
"""
API Powerhouse - Master Orchestrator
------------------------------------
1. Search Apollo for Leads
2. (Optional) Enrich Leads (Reveal Emails) if missing
3. Verify Emails (Tiered: MillionVerifier -> BounceBan/Reoon)
4. Export to CSV/Google Sheets
"""
import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def run_command(cmd, description, input_json=None):
    """Run a shell command and return the output."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    # Hide full JSON input from print logs if it's too long
    display_cmd = cmd.copy()
    if input_json:
         print(f"Running: {' '.join(cmd)} (with input payload)")
    else:
         print(f"Running: {' '.join(cmd)}\n")
    
    try:
        if input_json:
            result = subprocess.run(cmd, input=input_json, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
        if result.returncode != 0:
            print(f"ERROR: {description} failed")
            print(f"STDERR: {result.stderr}")
            return None
        
        return result.stdout
        
    except Exception as e:
        print(f"Execution Error: {e}")
        return None

def parse_json_output(output, source_name):
    """Robustly parse JSON output from a command."""
    try:
        # Try finding the first '[' or '{'
        lines = output.strip().split('\n')
        json_start = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('[') or line.strip().startswith('{'):
                json_start = i
                break
        
        if json_start != -1:
            json_str = '\n'.join(lines[json_start:])
            return json.loads(json_str)
        else:
            # Maybe it's just pure JSON
            return json.loads(output)
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {source_name}: {e}")
        print(f"Raw Output start: {output[:200]}...")
        return None

def main():
    parser = argparse.ArgumentParser(description="API Powerhouse Lead Gen Workflow")
    parser.add_argument("--job_titles", nargs="+", help="Job titles", required=True)
    parser.add_argument("--locations", nargs="+", help="Locations", default=[])
    parser.add_argument("--keywords", nargs="+", help="Keywords (Industry terms for companies)", default=[])
    parser.add_argument("--limit", type=int, help="Max leads", default=10)
    parser.add_argument("--enrich", action="store_true", help="Enable enrichment (Apollo Reveal)")
    parser.add_argument("--spreadsheet_id", help="Google Sheet ID for export")
    
    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(".tmp", exist_ok=True)
    
    # Files
    raw_file = f".tmp/powerhouse_raw_{timestamp}.json"
    enriched_file = f".tmp/powerhouse_enriched_{timestamp}.json"
    verified_file = f".tmp/powerhouse_verified_{timestamp}.json"
    
    # 1. Search
    search_cmd = ["python3", "execution/apollo_search.py", "--limit", str(args.limit)]
    if args.job_titles: search_cmd.extend(["--job_titles"] + args.job_titles)
    if args.locations: search_cmd.extend(["--locations"] + args.locations)
    if args.keywords: search_cmd.extend(["--keywords"] + args.keywords)
    
    search_out = run_command(search_cmd, "Searching Apollo")
    if not search_out: return 1
    
    leads = parse_json_output(search_out, "Apollo Search")
    if not leads: return 1
    
    with open(raw_file, 'w') as f: json.dump(leads, f, indent=2)
    print(f"✓ Found {len(leads)} leads")

    # 2. Enrich (Conditional)
    current_leads = leads
    if args.enrich:
        # Check which leads need enrichment (missing email or 'email_not_unlocked')
        leads_to_enrich = []
        for l in current_leads:
             email = l.get('email', '')
             if not email or 'email_not_unlocked' in email:
                 leads_to_enrich.append(l)
        
        if leads_to_enrich:
            print(f"Enriching {len(leads_to_enrich)} leads with missing emails...")
            # We will just pass ALL leads to enrich script, let it handle skipping?
            # Or better, just pass the full list and let it smart-process.
            # My apollo_enrich.py iterates all. Let's rely on that.
            
            enrich_cmd = ["python3", "execution/apollo_enrich.py", "--input_file", raw_file]
            enrich_out = run_command(enrich_cmd, "Enriching via Apollo Reveal")
            
            if enrich_out:
                enriched_data = parse_json_output(enrich_out, "Enrichment")
                if enriched_data:
                    current_leads = enriched_data
                    with open(enriched_file, 'w') as f: json.dump(current_leads, f, indent=2)
                    print(f"✓ Enrichment complete")
        else:
            print("No leads needed enrichment (all had emails).")
    
    # 3. Verify
    # We pass the current_leads (either raw or enriched)
    # Save current leads to a temp file for verification input if it changed
    verification_input = raw_file
    if args.enrich and os.path.exists(enriched_file):
        verification_input = enriched_file
        
    verify_cmd = ["python3", "execution/verify_leads.py", "--input_file", verification_input]
    verify_out = run_command(verify_cmd, "Verifying Emails")
    
    if verify_out:
        verified_data = parse_json_output(verify_out, "Verification")
        if verified_data:
            current_leads = verified_data
            with open(verified_file, 'w') as f: json.dump(current_leads, f, indent=2)
            print(f"✓ Verification complete")
            
    # 4. Export
    final_input = verified_file if os.path.exists(verified_file) else verification_input
    export_cmd = ["python3", "execution/export_leads.py", "--input_file", final_input]
    if args.spreadsheet_id:
        export_cmd.extend(["--spreadsheet_id", args.spreadsheet_id])
        
    export_out = run_command(export_cmd, "Exporting Leads")
    if export_out:
        print("\n✓ Export Output:")
        print(export_out)

    print(f"\nWorkflow Completed. Final data in {final_input}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
