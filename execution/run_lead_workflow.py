#!/usr/bin/env python3
"""
Master workflow script to orchestrate the lead generation process.
"""
import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def run_command(cmd, description):
    """Run a shell command and return the output."""
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR: {description} failed")
        print(f"STDERR: {result.stderr}")
        return None
    
    return result.stdout

def main():
    parser = argparse.ArgumentParser(description="Run complete lead generation workflow")
    parser.add_argument("--job_titles", nargs="+", help="Job titles to search for", required=True)
    parser.add_argument("--locations", nargs="+", help="Locations to search", default=[])
    parser.add_argument("--employees", nargs="+", help="Employee ranges", default=[])
    parser.add_argument("--keywords", nargs="+", help="Keywords/Industry tags", default=[])
    parser.add_argument("--limit", type=int, help="Number of leads to fetch", default=10)
    parser.add_argument("--skip_verification", action="store_true", help="Skip email verification step")
    parser.add_argument("--spreadsheet_id", help="Google Sheet ID to export to (optional)")
    
    args = parser.parse_args()
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Setup temp directory
    os.makedirs(".tmp", exist_ok=True)
    
    # File paths
    raw_leads_file = f".tmp/leads_raw_{timestamp}.json"
    verified_leads_file = f".tmp/leads_verified_{timestamp}.json"
    export_file = f".tmp/leads_export_{timestamp}.csv"
    
    print("\n" + "="*60)
    print("APOLLO LEAD GENERATION WORKFLOW")
    print("="*60)
    print(f"Job Titles: {args.job_titles}")
    print(f"Locations: {args.locations}")
    print(f"Employees: {args.employees}")
    print(f"Limit: {args.limit}")
    print(f"Timestamp: {timestamp}")
    
    # Step 1: Search Apollo
    apollo_cmd = [
        "python3", "execution/apollo_search.py",
        "--limit", str(args.limit)
    ]
    
    if args.job_titles:
        apollo_cmd.extend(["--job_titles"] + args.job_titles)
    if args.locations:
        apollo_cmd.extend(["--locations"] + args.locations)
    if args.employees:
        apollo_cmd.extend(["--employees"] + args.employees)
    if args.keywords:
        apollo_cmd.extend(["--keywords"] + args.keywords)
    
    apollo_output = run_command(apollo_cmd, "Searching Apollo for leads")
    
    if not apollo_output:
        print("Failed to fetch leads from Apollo")
        return 1
    
    # Parse and save raw leads
    try:
        # Extract JSON from output (skip warning lines)
        lines = apollo_output.strip().split('\n')
        json_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('['):
                json_start = i
                break
        
        if json_start is not None:
            json_output = '\n'.join(lines[json_start:])
            raw_leads = json.loads(json_output)
        else:
            raw_leads = json.loads(apollo_output)
            
        with open(raw_leads_file, 'w') as f:
            json.dump(raw_leads, f, indent=2)
        
        print(f"\n✓ Found {len(raw_leads)} leads from Apollo")
        print(f"✓ Saved to {raw_leads_file}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Apollo output: {e}")
        print(f"Output was: {apollo_output[:500]}")
        return 1
    # Step 1.5: Enrich Leads (Reveal Emails)
    print("\n" + "="*60)
    print("STEP: Enriching leads (Revealing Emails)")
    print("="*60)
    
    enrich_cmd = [
        "python3", "execution/apollo_enrich.py",
        "--input_file", raw_leads_file
    ]
    
    enrich_output = run_command(enrich_cmd, "Enriching leads")
    
    enriched_leads_file = f".tmp/leads_enriched_{timestamp}.json"
    leads_for_verification = raw_leads_file
    
    if enrich_output:
        try:
             # apollo_enrich.py now logs to stderr, so stdout is pure JSON
            enriched_leads = json.loads(enrich_output)
            with open(enriched_leads_file, 'w') as f:
                json.dump(enriched_leads, f, indent=2)
                
            print(f"\n✓ Enriched {len(enriched_leads)} leads")
            print(f"✓ Saved to {enriched_leads_file}")
            leads_for_verification = enriched_leads_file
            
        except json.JSONDecodeError as e:
            print(f"Warning: Error parsing enrichment output: {e}")
            print("Continuing with raw leads...")
    else:
        print("Warning: Enrichment failed, continuing with raw leads...")

    # Step 2: Verify emails (optional)
    if not args.skip_verification:
        verify_cmd = [
            "python3", "execution/verify_leads.py",
            "--input_file", leads_for_verification
        ]
        
        verify_output = run_command(verify_cmd, "Verifying emails with Million Verifier")
        
        if verify_output:
            try:
                # Extract JSON from output
                lines = verify_output.strip().split('\n')
                json_start = None
                for i, line in enumerate(lines):
                    if line.strip().startswith('['):
                        json_start = i
                        break
                
                if json_start is not None:
                    json_output = '\n'.join(lines[json_start:])
                    verified_leads = json.loads(json_output)
                else:
                    verified_leads = json.loads(verify_output)
                    
                with open(verified_leads_file, 'w') as f:
                    json.dump(verified_leads, f, indent=2)
                
                print(f"\n✓ Verified {len(verified_leads)} leads")
                print(f"✓ Saved to {verified_leads_file}")
                
                # Use verified leads for export
                leads_to_export = verified_leads_file
                
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing verification output: {e}")
                print("Continuing with unverified leads...")
                leads_to_export = raw_leads_file
        else:
            print("Warning: Verification failed, continuing with unverified leads...")
            leads_to_export = raw_leads_file
    else:
        print("\n⊘ Skipping email verification")
        leads_to_export = raw_leads_file
    
    # Step 3: Export to CSV/Sheets
    export_cmd = [
        "python3", "execution/export_leads.py",
        "--input_file", leads_to_export
    ]
    
    if args.spreadsheet_id:
        export_cmd.extend(["--spreadsheet_id", args.spreadsheet_id])
    
    export_output = run_command(export_cmd, "Exporting leads")
    
    if export_output:
        print(f"\n✓ Export completed")
        print(export_output)

    # Step 3.5: Local CSV Export (Fallback/Default)
    local_csv_file = f"leads_{timestamp}.csv" # Save to root or workspace for user visibility
    csv_cmd = [
        "python3", "execution/convert_leads_to_csv.py",
        leads_to_export,
        local_csv_file
    ]
    
    csv_output = run_command(csv_cmd, "Creating local CSV")
    
    if csv_output:
        print(f"\n✓ Local CSV created: {local_csv_file}")
    
    # Step 4: Upload to Google Drive
    # Find the CSV file that was created
    csv_files = [f for f in os.listdir('.tmp') if f.startswith('leads_export') and f.endswith('.csv')]
    
    if csv_files:
        latest_csv = sorted(csv_files)[-1]
        csv_path = f".tmp/{latest_csv}"
        
        gdrive_cmd = [
            "python3", "execution/gdrive_manager.py",
            "--folder_name", "Leads from Apollo API",
            "--upload_file", csv_path,
            "--file_name", f"leads_{timestamp}.csv"
        ]
        
        gdrive_output = run_command(gdrive_cmd, "Uploading to Google Drive")
        
        if gdrive_output:
            print(f"\n✓ Upload to Google Drive completed")
            print(gdrive_output)
            
            # Extract the folder link from output
            for line in gdrive_output.split('\n'):
                if 'Folder Link:' in line or 'File Link:' in line:
                    print(f"\n🔗 {line}")
    
    print("\n" + "="*60)
    print("WORKFLOW COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
