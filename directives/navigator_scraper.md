# Navigator Scraper Directive

## Goal
Scrape leads from LinkedIn Sales Navigator using Apify and prepare them for enrichment (e.g., Clay).

## Inputs
- **Sales Navigator Search URL**: The URL of the search results you want to scrape.
- **Max Profiles**: Number of profiles to scrape (default: 50).
- **Session Cookie (Optional)**: If the actor requires it (some do, some use their own pools). For `curious_programmer/linkedin-sales-navigator-scraper`, it often uses its own accounts or requires cookies. *Note: We will assume we use an actor that handles this or prompts for cookies if needed.*

## Tools
- **Apify Actor**: `curious_programmer/linkedin-sales-navigator-scraper` (or equivalent).
- **Script**: `execution/navigator_scraper.py`

## Process
1.  **Input Search URL**: User provides the Sales Nav URL.
2.  **Execute Scraper**: Run the Apify actor via the Python script.
3.  **Poll for Completion**: Script waits for the run to finish.
4.  **Download Results**: Fetch the dataset items (clean JSON/CSV).
5.  **Save Output**: Save to `.tmp/leads_<timestamp>.csv`.

## Output
- A CSV file in `.tmp/` containing:
    - Profile URL
    - Name
    - Job Title
    - Company Name
    - Location
    - (Other available fields)

## Next Steps
- Import the CSV into Clay or another enrichment tool to find work emails.
