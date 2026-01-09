import argparse
import subprocess
import time
import sys
import os

def run_command(command):
    """Run a shell command and print output."""
    print(f"Executing: {command}")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Stream output
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
            
    rc = process.poll()
    return rc

def main():
    parser = argparse.ArgumentParser(description="Orchestrate Lead Generation (Source -> Wait -> Enrich)")
    parser.add_argument("--run_id", help="Existing Apify Run ID to resume from")
    parser.add_argument("--output_base", default="leads_orchestrated", help="Base name for output files")
    
    # Arguments for starting a NEW run (passing through to apify_lead_scraper.py)
    parser.add_argument("--job_titles", nargs="+", default=[])
    parser.add_argument("--locations", nargs="+", default=[])
    parser.add_argument("--industries", nargs="+", default=[])
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--spreadsheet_id", help="Google Sheet ID to export to", default=None)
    parser.add_argument("--output_dir", default=".tmp", help="Directory for output files")
    
    args, unknown = parser.parse_known_args()

    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    raw_file = os.path.join(args.output_dir, f"{args.output_base}_raw.csv")
    enriched_file = os.path.join(args.output_dir, f"{args.output_base}_enriched.csv")

    # Step 1: Sourcing / Fetching
    if args.run_id:
        print(f"🔄 Resuming from Run ID: {args.run_id}")
        cmd = f"python3 execution/apify_lead_scraper.py --fetch_run_id {args.run_id} --output {raw_file}"
        if run_command(cmd) != 0:
            print("❌ Failed to fetch results.")
            sys.exit(1)
    else:
        # Construct start command
        # Ensure limit is provided or asked for (but this script assumes args are passed)
        cmd_parts = ["python3 execution/apify_lead_scraper.py"]
        if args.job_titles: cmd_parts.append(f"--job_titles {' '.join([f'\"{x}\"' for x in args.job_titles])}")
        if args.locations: cmd_parts.append(f"--locations {' '.join([f'\"{x}\"' for x in args.locations])}")
        if args.industries: cmd_parts.append(f"--industries {' '.join([f'\"{x}\"' for x in args.industries])}")
        cmd_parts.append(f"--limit {args.limit}")
        cmd_parts.append(f"--output {raw_file}")
        
        # Pass any unknown args
        if unknown: cmd_parts.extend(unknown)
        
        cmd = " ".join(cmd_parts)
        if run_command(cmd) != 0:
            print("❌ Sourcing failed.")
            sys.exit(1)

    # Step 2: Enrichment
    print("\n💧 Starting Enrichment...")
    enrich_cmd = f"python3 execution/waterfall_enrichment.py --input {raw_file} --output {enriched_file}"
    if run_command(enrich_cmd) != 0:
        print("❌ Enrichment failed.")
        sys.exit(1)

    # Step 3: Export to Google Sheets
    print("\n📊 Exporting to Google Sheets...")
    sheet_title = f"Leads Export - {args.output_base}"
    export_cmd = f"python3 execution/export_leads.py --input_file {enriched_file} --title \"{sheet_title}\""
    if args.spreadsheet_id:
        export_cmd += f" --spreadsheet_id {args.spreadsheet_id}"
    
    run_command(export_cmd)
        
    print(f"\n✅ Pipeline Complete! Enriched file: {enriched_file}")

if __name__ == "__main__":
    main()
