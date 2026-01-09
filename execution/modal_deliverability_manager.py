
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
).add_local_file(
    "/Users/michaelsipes/Coding/SA Workspace/execution/universal_campaign_manager.py", remote_path="/root/universal_campaign_manager.py"
)

app = modal.App("sa-sl-ec8aea49")

# Persistent storage for the latest report
report_storage = modal.Dict.from_name("udm-reports", create_if_missing=True)

@app.function(
    image=image,
    secrets=[
        modal.Secret.from_name("smartguard-secrets"), # Expects SMARTLEAD_API_KEY, SENDER_EMAIL, SENDER_PASSWORD
        modal.Secret.from_name("sa-sm1-secret"),      # Specific override: SA_SM1_API_KEY
        modal.Secret.from_name("supabase-secrets"),     # Supabase DB Access
        modal.Secret.from_name("campaign-secrets"),     # Target Campaign IDs
        modal.Secret.from_name("slack-secrets"),        # Slack Webhook URL
    ],
    schedule=modal.Cron("0 14 * * *") # Daily at 2 PM UTC (9 AM EST)
)
def run_job():
    sys.path.append("/root")
    from universal_deliverability_manager import UniversalDeliverabilityManager, SmartleadProvider
    
    print("🚀 Starting Scheduled Deliverability Manager...")
    
    # 1. Setup
    # Prioritize SA_SM1_API_KEY if available (Instance specific override)
    api_key = os.getenv("SA_SM1_API_KEY") or os.getenv("SMARTLEAD_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")
    # sick_threshold = int(os.getenv("SICK_THRESHOLD", 97))
    
    if not api_key:
        print("❌ Missing SMARTLEAD_API_KEY env var.")
        return

    provider = SmartleadProvider(api_key)
    manager = UniversalDeliverabilityManager(
        provider, 
        sick_threshold=97, 
        healthy_tag='Running',
        instance_name="Smartlead",
        dashboard_url="https://app.smartlead.ai/app/email-accounts/list"
    )
    
    # 2. Analyze & Execute
    manager.analyze()
    if manager.proposed_actions:
        manager.execute() # Auto-run on schedule
    
    # 3. Generate & Store Report
    # Use Production URL to ensure the link works even if triggered from an ephemeral run
    web_url = "https://msipes--sa-sl-ec8aea49-get-report.modal.run"
    
    html_report = manager.generate_html(web_link=web_url)
    report_storage["latest"] = html_report
    
    # 4. Phase 2 Orchestration: Advanced Stats & Sync
    
    # A. Fetch Previous Volume (Before Sync overwrites DB)
    sb_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    sb_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    vol_prev = 0
    if sb_url and sb_key:
        vol_prev = manager.fetch_previous_volume(sb_url, sb_key)
        
    # B. Execute Deliverability Manager (Updates internal state)
    manager.execute() 
    
    # C. Calculate Current Volume (After updates)
    vol_curr = manager.get_sending_volume()
    
    # D. Execute Campaign Manager (Returns stats)
    print("\n🚀 Starting Campaign Manager...")
    campaign_stats = None
    try:
        from universal_campaign_manager import UniversalCampaignManager
        c_ids = os.getenv("TARGET_CAMPAIGN_IDS") # campaign-secrets
        
        if c_ids and sb_url and sb_key and api_key:
            cm = UniversalCampaignManager(c_ids, sb_url, sb_key, api_key)
            campaign_stats = cm.run()
        else:
            print("⚠️  Skipping Campaign Manager: Missing Env Vars")
    except Exception as e:
        print(f"❌ Campaign Manager Failed: {e}")

    # 5. Send Consolidated Report
    sender_email = os.getenv("SENDER_EMAIL")
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    
    # Use Campaign Volume if available (more accurate to "Campaigns sending"), else fallback to Account Volume
    final_vol = vol_curr
    if campaign_stats and 'volume' in campaign_stats:
        final_vol = campaign_stats['volume']
    
    vol_stats = {'current': final_vol, 'previous': vol_prev}
    
    if sender_email or slack_webhook:
        manager.send_report(
            email_to="msipes@sipesautomation.com", 
            slack_url=slack_webhook, 
            web_link=web_url,
            campaign_stats=campaign_stats,
            volume_stats=vol_stats
        )

    print("✅ Job Complete.")

@app.function(image=image)
@modal.web_endpoint()
def get_report():
    """Serves the latest HTML report."""
    html = report_storage.get("latest", "<h1>No report generated yet.</h1>")
    return html
