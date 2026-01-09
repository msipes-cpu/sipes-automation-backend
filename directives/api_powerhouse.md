# API Powerhouse Workflow

> [!NOTE]
> **Goal**: High-velocity, orchestrated lead generation, enrichment, and verification.

This directive outlines the process for the "API Powerhouse" workflow, which combines Apollo Search, Apollo Reveal (Enrichment), and Tiered Verification (MillionVerifier + BounceBan/Reoon).

## Inputs
- **Search Criteria**: Job Titles, Locations, Employee Count, Keywords.
- **Enrichment**: Boolean flag (True/False) to enable "Reveal" for missing emails.
- **Export Target**: Google Sheet ID (optional).

## Tools
- `execution/api_powerhouse.py`: **Master Orchestrator**. Use this tool.
- `execution/apollo_search.py`: Component for search.
- `execution/apollo_enrich.py`: Component for "reveal".
- `execution/verify_leads.py`: Component for tiered verification.
- `execution/export_leads.py`: Component for export.

## Workflow Steps

1.  **Clarify Requirements**
    - Ask for Target Persona (Title, Location).
    - Ask if "Enrichment" (Reveal) is needed (costs credits).
    - Ask for Export Destination (Google Sheet or CSV).

2.  **Execute Workflow**
    - Run the orchestrator script:
      ```bash
      python3 execution/api_powerhouse.py \
          --job_titles "CEO" "Founder" \
          --locations "US" "UK" \
          --limit 100 \
          --enrich \
          --spreadsheet_id "YOUR_SHEET_ID"
      ```

3.  **Review Output**
    - The script will output raw, enriched, and verified files in `.tmp/`.
    - It will also export to the specified Google Sheet if provided.

4.  **Handle Catch-Alls**
    - The script automatically attempts to verify catch-all emails using BounceBan or Reoon if keys are present.

## Configuration (.env)
Ensure these keys are present:
- `APOLLO_API_KEY`
- `MILLION_VERIFIER_API_KEY`
- `BOUNCEBAN_API_KEY` (Optional, for catch-alls)
- `REOON_API_KEY` (Optional, for catch-alls)
- `GOOGLE_SERVICE_ACCOUNT_FILE` (For Sheets export)
