import csv
import os
import argparse
from gmail_agent import get_gmail_service, create_message, create_draft, IMPERSONATED_USER

CSV_FILE = "marketing/first_five_tracking.csv"

def read_leads(csv_path):
    """Read leads from CSV."""
    leads = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append(row)
    return leads

def update_csv(csv_path, leads, fieldnames):
    """Update CSV with modified leads."""
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

def generate_drafts(dry_run=False, limit=0, output_file=None, csv_only=False, input_csv=None):
    """Generate drafts for leads."""
    csv_file_path = input_csv if input_csv else CSV_FILE

    service = None
    if not output_file and not dry_run and not csv_only:
        service = get_gmail_service()
        if not service:
            print("Failed to authenticate with Gmail.")
            return

    leads = read_leads(csv_file_path)
    if not leads:
        print(f"No leads found in {csv_file_path}.")
        return

    # Get fieldnames from the first read to preserve structure
    with open(csv_file_path, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
    
    # Add new columns if not present
    if 'Generated_Draft_Variant' not in fieldnames: fieldnames.append('Generated_Draft_Variant')
    if 'Generated_Draft_Subject' not in fieldnames: fieldnames.append('Generated_Draft_Subject')
    if 'Generated_Draft_Body' not in fieldnames: fieldnames.append('Generated_Draft_Body')

    drafts_created = 0
    file_content = []

    for lead in leads:
        if limit > 0 and drafts_created >= limit:
            break

        # Check for 'Contacted?' column being 'No' (or empty) and verify it's a Cold lead
        contacted = lead.get('Contacted?', 'No')
        if not contacted: contacted = 'No'
        
        # We process if not contacted OR if we are forcing csv_only generation for upload
        # If csv_only is True, we generate for EVERYONE who is Cold, regardless of status, 
        # unless they already have a drafted subject/body we want to preserve? 
        # actually, user said "write the emails... and add... to Instantly". 
        # Safer to regenerate to ensure consistency or check if empty.
        # Let's regenerate if it's a Cold lead.
        
        should_process = (contacted == 'No') or csv_only
        
        if should_process and lead.get('Warm/Cold', 'Cold') == 'Cold':
            # Personalize
            name = lead.get('Name', '').split()[0] # First name
            company = lead.get('Company', '')
            role = lead.get('Role', '')
            email = lead.get('Email', '')
            context = lead.get('Personalized_Line_Context', '')

            # A/B Testing Logic
            is_variant_a = (drafts_created % 2 == 0)
            variant_name = "A (Tech Install)" if is_variant_a else "B (Loss Aversion)"
            variant_code = "A" if is_variant_a else "B"

            if is_variant_a:
                # Variant A: Tech Install
                subject = f"Quick question about {company} / Automation"
                body = f"""Hey {name},

{context}

I run an automation shop. I know you guys do lead gen/PPC, wanted to run this by you.

To make a long story short: we built a "Speed-to-Lead" system that grabs inbound leads and fires a personalized SMS + calls your sales team in under 5 seconds. It has been crushing—literally doubling conversion rates for agencies because leads never get cold.

I am trying to install this in a few other agencies because I think it has legs. Am extremely confident it'd work for you, so much so that I'd do it 100% free just to prove it.

Idk what your current response time is, but this ensures it's near-instant 24/7. Would take very little time on your end, I'll do everything else within 72hrs.

If you're open to it just let me know. Can give you a quick ring in the next day or two.

Thanks,
- Michael"""

            else:
                # Variant B: Loss Aversion / Value Gap
                subject = f"You are losing leads (technically)"
                body = f"""Hey {name},

{context}

I want to give you some value, because if you're running paid ads, I think I spot a leak.

I used to work in agency ops, and I can say quite confidently that if your team isn't calling leads in <5 minutes, you are likely losing ~50% of your potential deals.

This may be a small sum to you, perhaps not. But I see this all the time and we generally see a 2-4x ROI immediately when we fix it.

Here is my offer: do you want me to fix this for you? I would 100% guarantee I could get your response time to under 10 seconds. It would take next to none of your time, and I'd do it for free as a founding case study.

Just putting this out there. If you're even halfway interested let me know and I can give you a ring.

Best,
- Michael"""

            # Always populate the lead dict with the generated content
            lead['Generated_Draft_Variant'] = variant_code
            lead['Generated_Draft_Subject'] = subject
            lead['Generated_Draft_Body'] = body

            if output_file:
                file_content.append(f"## Draft for {name} ({email}) - Variant {variant_name}\n**Subject:** {subject}\n\n{body}\n\n---\n")
                drafts_created += 1
                
            elif csv_only:
                 # Just increment counter, we update CSV at end
                 drafts_created += 1
                
            elif not dry_run:
                print(f"Preparing draft for {name} ({email})...")
                try:
                    message = create_message(IMPERSONATED_USER, email, subject, body)
                    create_draft(service, 'me', message)
                    lead['Contacted?'] = 'Drafted_Gmail'
                    drafts_created += 1
                    print(f"Draft created for {email}")
                except Exception as e:
                    print(f"Failed to create draft for {email}: {e}")
            else:
                drafts_created += 1
                print(f"[DRY RUN] Would create draft for {email}")
                print(f"[DRY RUN] Subject: {subject}")
                print(f"[DRY RUN] Body preview: {body[:100]}...")

    if output_file:
        with open(output_file, 'w') as f:
            f.write("\n".join(file_content))
        print(f"Saved {drafts_created} drafts to {output_file}")
        
    if not dry_run:
        # Always update CSV with the new columns
        update_csv(csv_file_path, leads, fieldnames)
        print(f"\nSuccess! Updated CSV with {drafts_created} drafts details.")
    else:
        print(f"\n[DRY RUN] Would have created {drafts_created} drafts.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outreach Manager")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without creating drafts")
    parser.add_argument("--limit", type=int, default=0, help="Max number of drafts to create")
    parser.add_argument("--output-file", type=str, help="Save drafts to a local file instead of Gmail")
    parser.add_argument("--csv-only", action="store_true", help="Generate drafts in CSV only, skip Gmail")
    parser.add_argument("--input-csv", type=str, help="Input CSV file path (overrides default)")
    args = parser.parse_args()

    generate_drafts(dry_run=args.dry_run, limit=args.limit, output_file=args.output_file, csv_only=args.csv_only, input_csv=args.input_csv)
