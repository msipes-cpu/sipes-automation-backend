# Apollo -> Blitz -> Verification Lead Gen

> This directive outlines the process for sourcing leads from Apollo (People Search only), enriching them with Blitz API, validating emails, and uploading to Google Drive.

## Inputs
- **Apollo Search URL/Parameters**: Defines the target audience (Titles, Locations, Industries, Exclusions).
- **Limit**: Number of leads to fetch (e.g., 1000).

## Tools
- `execution/apollo_blitz_lead_gen.py`: The main orchestrator script.
    - Uses `execution/apollo_search.py` logic for fetching.
    - Uses `execution/enrich_with_blitz.py` logic for enrichment.
    - Uses `execution/verify_leads.py` for verification.
    - Uses `execution/gdrive_manager.py` for upload.
- **API Keys Required**:
    - `APOLLO_API_KEY`
    - `BLITZ_API_KEY`
    - `MILLION_VERIFIER_API_KEY` or other verification keys.
    - `GOOGLE_SERVICE_ACCOUNT_FILE`

## Workflow Steps

1.  **Configure Search**
    - The script `execution/apollo_blitz_lead_gen.py` contains the specific payload derived from the Apollo URL.
    - Update the script parameters if the target audience changes.

2.  **Run Execution**
    ```bash
    python3 execution/apollo_blitz_lead_gen.py --limit 1000
    ```
    - The script will:
        1.  Fetch 1000 leads from Apollo (pages 1-10+).
        2.  Save raw leads to `.tmp/apollo_raw_<timestamp>.csv`.
        3.  Enrich each lead with Blitz API using the LinkedIn URL.
        4.  Verify findings with MillionVerifier (and tiered backups).
        5.  Filter out leads with no valid email.
        6.  Save final enriched list to `.tmp/apollo_enriched_<timestamp>.csv`.
        7.  Upload to Google Drive folder "Leads from Apollo API".

3.  **Review**
    - Click the Google Drive link output by the script.
    - Verify data quality.

## Updates
- Created 2026-01-11 for Manufacturing/Robotics lead list request.
