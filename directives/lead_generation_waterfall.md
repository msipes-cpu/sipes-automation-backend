# Lead Generation Waterfall Workflow

> This directive outlines the process for sourcing leads via Apify and enriching them using a multi-provider waterfall methodology.

## Inputs
- **Sourcing Criteria**: Job Titles, Locations, Industries, etc.
- **API Keys**: Apify, MillionVerifier, Datagma, Hunter, etc.

## Tools
- `execution/apify_lead_scraper.py`: Fetches leads from LinkedIn/SalesNav via Apify Actor `T1XDXWc1L92AfIJtd`.
- `execution/waterfall_enrichment.py`: Enriches leads using Prospeo -> Datagma -> Hunter -> MillionVerifier.

## Workflow Steps

0.  **Clarify Limit (Critical Protocol)**
    - **Step 0a**: If the user did not specify a lead limit (e.g., "Get me 500 leads"), **YOU MUST ASK** before proceeding.
    - **Reason**: Sourcing costs credits/money. Always confirm the volume.

1.  **Sourcing (Apify)**
    - Run `execution/apify_lead_scraper.py` with your criteria.
    - Example:
      ```bash
      python3 execution/apify_lead_scraper.py --job_titles "CEO" "Founder" --locations "United States" --limit 100 --output leads_raw.csv
      ```
    - **Output**: A raw CSV file containing LinkedIn profiles and potentially some emails.

2.  **Enrichment (Waterfall)**
    - Run `execution/waterfall_enrichment.py` on the raw output.
    - Example:
      ```bash
      python3 execution/waterfall_enrichment.py --input leads_raw.csv --output leads_enriched.csv
      ```
    - **Logic**:
        - Checks if email exists & validates it.
        - If invalid/missing, tries Datagma (with LinkedIn URL).
        - If still missing, tries Hunter (with Domain).
        - Validates all found emails with MillionVerifier.
    - **Output**: Final CSV with `final_email`, `enrichment_source`, and `verification_status`.

3.  **Review**
    - Open `leads_enriched.csv` to review the results.
    - Filter for `verification_status` = "safe" for high-deliverability campaigns.

## Troubleshooting
- **Missing API Keys**: Ensure `.env` has all required keys (`APIFY_API_TOKEN`, `DATAGMA_API_KEY`, etc.). The scripts will skip providers if keys are missing.
- **Apify Limits**: Check your Apify console for run limits or credit usage if the sourcing step fails.
