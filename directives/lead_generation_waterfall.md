# Lead Generation Waterfall Workflow (Strict Mode)

> **Protocol Update (Jan 2026)**: We have moved to a custom **Apollo Universal Scraper** with a **Strict Smart Waterfall** strategy to maximize yield and eliminate bounces.

## Core Component`execution/apollo_universal_scraper.py`

This script parses *any* Apollo Search URL and executes the following high-yield pipeline.

## The Strict Smart Waterfall Flow

1.  **Apollo Lead Capture**:
    - Fetches contacts from the provided Apollo Search URL.
    - Handles pagination and complex filters (Funding, Tech Stack, etc.).

2.  **Primary Enrichment (Blitz)**:
    - Uses the LinkedIn URL to find the email via **Blitz API**.

3.  **Strict Verification (Round 1)**:
    - Verifies the Blitz email using **MillionVerifier**.
    - **SAFE (`ok`)**: Kept. Lead secured.
    - **INVALID**: **Discarded**. Triggers Fallback (Step 4).
    - **CATCH-ALL/UNKNOWN**: **Discarded**. (Strict Mode rejects risk).

4.  **Fallback Enrichment (AnyMail Finder)**:
    - *Triggered ONLY if Blitz returned an INVALID email.*
    - Searches for the email using `First Name` + `Last Name` + `Domain`.

5.  **Strict Verification (Round 2)**:
    - Verifies the AnyMail Finder email using **MillionVerifier**.
    - **SAFE (`ok`)**: Kept.
    - **Anything else**: Discarded.

## Usage

### Standard High-Yield Run
```bash
python3 execution/apollo_universal_scraper.py \
  --url "https://app.apollo.io/#/people?..." \
  --niche "SaaS_CEOs" \
  --target 5000 \
  --threads 20 \
  --fetch-workers 10
```

### Delta Recovery Run (Resume/Retry)
Use this to recover "missed" leads without paying for duplicates.
```bash
python3 execution/apollo_universal_scraper.py \
  --url "..." \
  --niche "SaaS_Rescued" \
  --target 5000 \
  --exclude-file "PREVIOUS_RUN.csv"
```

## Key Configuration
- **Strict Mode**: Enabled by default in `verify_leads.py`. Only allows `safe` emails.
- **Smart Waterfall**: Enabled by default in `apollo_universal_scraper.py`.
