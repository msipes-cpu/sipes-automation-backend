# Generate Leads Workflow

This directive outlines the process for generating leads using Apollo, verifying them with Million Verifier, and exporting the valid results to a Google Sheet.

## Inputs
- **Search Criteria**: JSON object or arguments specifying target leads (e.g., job titles, location, industry).
- **Target Spreadsheet**: Name or ID of the Google Sheet to export to.

## Tools
- `execution/apollo_search.py`: Fetches leads from Apollo API.
- `execution/verify_leads.py`: Verifies email addresses using Million Verifier.
- `execution/export_leads.py`: appends data to Google Sheets.

## Workflow Steps

0.  **Clarify Intent (Interactive)**
    - **Step 0a**: User provides a prompt (e.g., "Dentists in NYC").
    - **Step 0b**: Agent asks: "Quick search or In-Depth search?"
    - **Step 0c - Quick**: Agent maps the prompt to best-guess parameters (Title="Dentist", Location="New York") and proceeds.
    - **Step 0d - In-Depth**: Agent asks clarifying questions (Employee count, Revenue, Specific keywords, etc.) before proceeding.

1.  **Search Apollo**
    - Run `execution/apollo_search.py` with the determined criteria.
    - Output: A JSON list of lead objects (or a path to a temp file containing them).

2.  **Verify Emails**
    - Take the list of leads from Step 1.
    - Run `execution/verify_leads.py`.
    - Note: This step may be asynchronous or take time depending on list size.
    - Output: A list of leads enriched with verification status (Safe, Risky, Invalid).

3.  **Filter & Export**
    - Filter the verified list to include only "Safe" (and optionally "Risky" if requested) emails.
    - Run `execution/export_leads.py` to export to CSV (or Google Sheet if credentials exist).

4.  **Upload to Google Drive**
    - Run `execution/gdrive_manager.py` to upload the CSV to "Leads from Apollo API" folder.
    - Return the shareable link to the user.

## Quick Run
Use the master workflow script:
```bash
python3 execution/run_lead_workflow.py --job_titles "CEO" "Founder" --locations "United States" --limit 10
```

## Setup Requirements
- `.env` must contain:
    - `APOLLO_API_KEY`
    - `MILLION_VERIFIER_API_KEY`
    - `GOOGLE_SERVICE_ACCOUNT_FILE` (Path to json key) or standard Google auth env vars.
