# Smartlead Daily Report

## Goal
Pull a daily report of cold email sends and replies from Smartlead for a specified date (defaults to today).

## Inputs
- **Date** (optional): Date to pull stats for in YYYY-MM-DD format. Defaults to today.
- **Campaign IDs** (optional): Comma-separated campaign IDs to filter (max 100). If not provided, pulls stats for all campaigns.
- **Client IDs** (optional): Comma-separated client IDs to filter (max 50). If not provided, pulls stats for all clients.

## Tools/Scripts
- `execution/smartlead_daily_report.py` - Fetches daily stats from Smartlead API

## Process
1. Get the date to query (default to today if not specified)
2. Call Smartlead API endpoint: `GET /api/v1/analytics/day-wise-overall-stats`
3. Parse the response and extract key metrics:
   - Total emails sent
   - Total emails opened
   - Total replies received
   - Total bounced
   - Open rate
   - Reply rate
4. Display the report in a clean, readable format

## Outputs
- Console output with daily stats summary
- Metrics include:
  - Date
  - Overall sent count
  - Overall opened count
  - Overall replied count
  - Overall bounced count
  - Overall open rate (%)
  - Overall reply rate (%)
  - **Campaign-by-campaign breakdown** with individual metrics
- Optional: Email report (see `directives/smartlead_automated_email.md`)

## Related Tools
- `execution/smartlead_email_report.py` - Send reports via email
- `execution/setup_daily_email_cron.sh` - Set up automated daily emails
- See `SMARTLEAD_REPORTS_SETUP.md` for complete setup guide
- See `SMARTLEAD_QUICK_REF.md` for quick reference

## Edge Cases
- **No data for date**: If no stats exist for the specified date, inform the user
- **API rate limit**: Smartlead has a rate limit of 10 requests per 2 seconds - script handles this gracefully
- **Invalid date format**: Validate date format before making API call
- **Missing API key**: Check for SMARTLEAD_API_KEY in .env file
- **API errors**: Handle and display meaningful error messages

## Notes
- API key is stored in `.env` as `SMARTLEAD_API_KEY`
- The endpoint returns stats based on when emails were sent
- For reply tracking by received time, use the alternative endpoint `/analytics/day-wise-overall-stats-by-sent-time`
- Stats are aggregated across all campaigns unless specific campaign_ids are provided
