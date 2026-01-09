
import modal
import os
import sys

# Define Image
image = modal.Image.debian_slim().pip_install(
    "requests",
    "python-dotenv",
    "fastapi"
).add_local_file(
    "/Users/michaelsipes/Coding/SA Workspace/execution/universal_deliverability_manager.py", remote_path="/root/universal_deliverability_manager.py"
)

app = modal.App("sa-instantly-manager")

# Persistent storage for the latest report
report_storage = modal.Dict.from_name("udm-instantly-reports", create_if_missing=True)

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("instantly-api-keys"), # Expects INSTANTLY_API_KEY
        modal.Secret.from_name("supabase-secrets"),     # Supabase DB Access
        modal.Secret.from_name("slack-secrets"),        # Slack Webhook URL
        modal.Secret.from_name("smartguard-secrets"),   # SENDER_EMAIL, SENDER_PASSWORD
    ],
    schedule=modal.Cron("0 14 * * *") # Daily at 2 PM UTC (9 AM EST)
)
def run_job():
    sys.path.append("/root")
    from universal_deliverability_manager import UniversalDeliverabilityManager, InstantlyProvider
    
    print("🚀 Starting Scheduled Instantly Deliverability Manager...")
    
    # 1. Setup
    api_key = os.getenv("INSTANTLY_API_KEY")
    if not api_key:
        pass

    if not api_key:
        print("❌ Missing INSTANTLY_API_KEY env var.")
        return

    provider = InstantlyProvider(api_key)
    # Instantly specific threshold? Keeping default 98%
    manager = UniversalDeliverabilityManager(
        provider, 
        sick_threshold=98, 
        healthy_tag='Running',
        instance_name="Instantly",
        dashboard_url="https://app.instantly.ai/app/accounts"
    )
    
    # 2. Analyze & Execute
    manager.analyze()
    if manager.proposed_actions:
        manager.execute() # Auto-run on schedule
    
    # 3. Generate & Store Report
    web_url = "https://msipes--sa-instantly-manager-get-report.modal.run"
    
    html_report = manager.generate_html(web_link=web_url)
    report_storage["latest"] = html_report
    
    # 4. Sync State to DB
    # (Happens inside execute() usually, but strictly we call it explicitly too to be safe/update timestamps)
    manager.sync_to_supabase()
    
    # 5. Send Report
    sender_email = os.getenv("SENDER_EMAIL")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    if sender_email or slack_webhook:
        manager.send_report(
            email_to="msipes@sipesautomation.com", 
            slack_url=slack_webhook, 
            web_link=web_url
        )

    print("✅ Job Complete.")

@app.function(image=image)
@modal.fastapi_endpoint()
def get_report():
    """Serves the latest HTML report."""
    html = report_storage.get("latest", "<h1>No report generated yet.</h1>")
    return html
