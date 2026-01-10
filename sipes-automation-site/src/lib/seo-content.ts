export const industries: Record<string, {
    title: string;
    heroTitle: string;
    heroSub: string;
    painPoint: string;
    exampleAutomation: string;
    metaDesc: string;
}> = {
    // --- LEGAL (10) ---
    "personal-injury-lawyer-automation": { title: "PI Law Automation", heroTitle: "Automate Your PI Intake.", heroSub: "Instant case files from intake calls.", painPoint: "manual intake", exampleAutomation: "Intake-to-CaseFile Bot", metaDesc: "PI Firm Automation." },
    "criminal-defense-law-automation": { title: "Criminal Defense Automation", heroTitle: "Speed Up Client Consults.", heroSub: "Auto-schedule jail visits and consults.", painPoint: "scheduling chaos", exampleAutomation: "Consult Scheduler", metaDesc: "Defense Firm Automation." },
    "family-law-automation": { title: "Family Law Automation", heroTitle: "Streamline Divorce Docs.", heroSub: "Auto-generate standard petitions.", painPoint: "drafting docs", exampleAutomation: "Petition Generator", metaDesc: "Family Law Automation." },
    "estate-planning-automation": { title: "Estate Planning Automation", heroTitle: "Streamline Wills & Trusts.", heroSub: "Auto-generate documents from intake forms.", painPoint: "drafting wills", exampleAutomation: "Document Gen Bot", metaDesc: "Estate Planning Automation." },
    "corporate-law-automation": { title: "Corporate Law Automation", heroTitle: "Automate Entity Formation.", heroSub: "One-click LLC setup and filings.", painPoint: "filing paperwork", exampleAutomation: "Entity Setup Flow", metaDesc: "Corporate Law Automation." },
    "immigration-law-automation": { title: "Immigration Law Automation", heroTitle: "Track Visa Deadlines.", heroSub: "Auto-reminders for every client filing date.", painPoint: "missed deadlines", exampleAutomation: "Deadline Watchdog", metaDesc: "Immigration Law Automation." },
    "ip-law-automation": { title: "IP Law Automation", heroTitle: "Automate Trademark Filings.", heroSub: "Streamline the search and file process.", painPoint: "trademark admin", exampleAutomation: "Filing Assistant", metaDesc: "IP Law Automation." },
    "tax-law-automation": { title: "Tax Law Automation", heroTitle: "Organize Audit Defence.", heroSub: "Auto-collect client financial records.", painPoint: "document collection", exampleAutomation: "Audit Doc Collector", metaDesc: "Tax Law Automation." },
    "employment-law-automation": { title: "Employment Law Automation", heroTitle: "Scale Dispute Resolution.", heroSub: "Automate claimant intake and sorting.", painPoint: "claimant screening", exampleAutomation: "Case Screener", metaDesc: "Employment Law Automation." },
    "real-estate-law-automation": { title: "Real Estate Law Automation", heroTitle: "Faster Closing Disclosures.", heroSub: "Auto-generate CDs and settlement statements.", painPoint: "closing docs", exampleAutomation: "Closing Doc Bot", metaDesc: "Real Estate Law Automation." },

    // --- FINANCIAL (10) ---
    "accounting-firm-automation": { title: "Accounting Firm Automation", heroTitle: "Add $50k Capacity.", heroSub: "Automate onboarding and monthly reports.", painPoint: "chasing clients", exampleAutomation: "Tax Return Chaser", metaDesc: "Accounting Automation." },
    "bookkeeping-automation": { title: "Bookkeeping Automation", heroTitle: "Double Client Load.", heroSub: "Auto-reconcile transactions daily.", painPoint: "manual recs", exampleAutomation: "Statement Fetcher", metaDesc: "Bookkeeping Automation." },
    "cfp-automation": { title: "Financial Planner Automation", heroTitle: "Automate Annual Reviews.", heroSub: "Auto-prep portfolio reports.", painPoint: "meeting prep", exampleAutomation: "Portfolio Reporter", metaDesc: "CFP Automation." },
    "wealth-management-automation": { title: "Wealth Manager Automation", heroTitle: "Scale High-Net-Worth Ops.", heroSub: "White-glove onboarding on autopilot.", painPoint: "paperwork friction", exampleAutomation: "VIP Onboarding Flow", metaDesc: "Wealth Management Automation." },
    "mortgage-broker-automation": { title: "Mortgage Broker Automation", heroTitle: "Close Loans Faster.", heroSub: "Auto-chase conditions.", painPoint: "chasing borrowers", exampleAutomation: "Loan Status Bot", metaDesc: "Mortgage Automation." },
    "insurance-broker-automation": { title: "Insurance Broker Automation", heroTitle: "Automate Renewals.", heroSub: "Auto-quote renewal policies 30 days out.", painPoint: "missed renewals", exampleAutomation: "Renewal Engine", metaDesc: "Insurance Automation." },
    "tax-prep-automation": { title: "Tax Prep Automation", heroTitle: "Crush Tax Season.", heroSub: "Auto-organize uploaded documents.", painPoint: "messy uploads", exampleAutomation: "Doc Sorter", metaDesc: "Tax Prep Automation." },
    "ma-advisor-automation": { title: "M&A Advisor Automation", heroTitle: "Streamline Due Diligence.", heroSub: "Auto-populate data rooms.", painPoint: "data room prep", exampleAutomation: "Data Room Builder", metaDesc: "M&A Automation." },
    "pe-firm-automation": { title: "PE Firm Automation", heroTitle: "Automate Deal Sourcing.", heroSub: "Scrape and enrich target companies.", painPoint: "deal sourcing", exampleAutomation: "Deal Scraper", metaDesc: "PE Automation." },
    "vc-firm-automation": { title: "VC Firm Automation", heroTitle: "Track Portfolio Needs.", heroSub: "Auto-collect monthly portfolio updates.", painPoint: "chasing founders", exampleAutomation: "Update Collector", metaDesc: "VC Automation." },

    // --- REAL ESTATE (10) ---
    "real-estate-wholesaler-automation": { title: "Wholesaler Automation", heroTitle: "Double Deal Flow.", heroSub: "Speed-to-lead SMS bots.", painPoint: "leads cooling", exampleAutomation: "SMS Responder", metaDesc: "Wholesaler Automation." },
    "house-flipper-automation": { title: "Flipper Automation", heroTitle: "Manage Project Costs.", heroSub: "Auto-track contractor invoices.", painPoint: "budget tracking", exampleAutomation: "Cost Tracker", metaDesc: "Flipper Automation." },
    "real-estate-agent-automation": { title: "Real Estate Agent Automation", heroTitle: "Automate Open House Follow-up.", heroSub: "Instant text to visitors.", painPoint: "follow-up lag", exampleAutomation: "Open House Bot", metaDesc: "Realtor Automation." },
    "property-manager-automation": { title: "Property Manager Automation", heroTitle: "Manage 50 More Doors.", heroSub: "Automate maintenance triage.", painPoint: "maintenance calls", exampleAutomation: "Maintenance Bot", metaDesc: "Property Ops Automation." },
    "commercial-broker-automation": { title: "Commercial Broker Automation", heroTitle: "Track Lease Expirations.", heroSub: "Auto-notify tenants 6 months out.", painPoint: "lease tracking", exampleAutomation: "Lease Watchdog", metaDesc: "Commercial RE Automation." },
    "airbnb-host-automation": { title: "Airbnb Host Automation", heroTitle: "Automate Guest Messaging.", heroSub: "Check-in instructions on autopilot.", painPoint: "messaging guests", exampleAutomation: "Message Sequencer", metaDesc: "Airbnb Automation." },
    "real-estate-developer-automation": { title: "Developer Automation", heroTitle: "Track Permitting Status.", heroSub: "Auto-check city portals for updates.", painPoint: "permit delays", exampleAutomation: "Permit Checker", metaDesc: "Developer Automation." },
    "hoa-management-automation": { title: "HOA Automation", heroTitle: "Automate Violation Letters.", heroSub: "Easy violation tracking and mailing.", painPoint: "violation admin", exampleAutomation: "HOA Letter Bot", metaDesc: "HOA Automation." },
    "title-company-automation": { title: "Title Company Automation", heroTitle: "Faster Title Searches.", heroSub: "Integrate order entry with search vendors.", painPoint: "re-keying orders", exampleAutomation: "Order Sync", metaDesc: "Title Automation." },
    "home-inspector-automation": { title: "Home Inspector Automation", heroTitle: "Automate Report Delivery.", heroSub: "Send reports and collect payment instantly.", painPoint: "admin after inspection", exampleAutomation: "Report Deliverer", metaDesc: "Inspector Automation." },

    // --- HEALTH & WELLNESS (10) ---
    "dentist-automation": { title: "Dentist Automation", heroTitle: "Fill Your Hygiene Chairs.", heroSub: "Recall automation for 6-month checkups.", painPoint: "empty chairs", exampleAutomation: "Recall Bot", metaDesc: "Dental Automation." },
    "chiropractor-automation": { title: "Chiropractor Automation", heroTitle: "Reduce No-Shows.", heroSub: "SMS reminders and confirmations.", painPoint: "no-shows", exampleAutomation: "Appointment Reminder", metaDesc: "Chiro Automation." },
    "med-spa-automation": { title: "Med Spa Automation", heroTitle: "Automate Membership Billing.", heroSub: "Manage subscriptions seamlessly.", painPoint: "billing issues", exampleAutomation: "Membership Manager", metaDesc: "Med Spa Automation." },
    "plastic-surgeon-automation": { title: "Plastic Surgeon Automation", heroTitle: "Nurture Consult Leads.", heroSub: "Long-term drip for expensive procedures.", painPoint: "cold consults", exampleAutomation: "Nurture Drip", metaDesc: "Surgeon Automation." },
    "psychologist-automation": { title: "Psychologist Automation", heroTitle: "Automate Intake Forms.", heroSub: "Secure forms sent before first session.", painPoint: "intake paperwork", exampleAutomation: "Secure Intake Flow", metaDesc: "Psychology Automation." },
    "pt-clinic-automation": { title: "PT Clinic Automation", heroTitle: "Track Care Plans.", heroSub: "Auto-reminders for home exercises.", painPoint: "patient adherence", exampleAutomation: "Care Plan Bot", metaDesc: "PT Automation." },
    "gym-owner-automation": { title: "Gym Automation", heroTitle: "Automate Member Onboarding.", heroSub: "Access codes and welcome emails instantly.", painPoint: "front desk admin", exampleAutomation: "New Member Flow", metaDesc: "Gym Automation." },
    "nutritionist-automation": { title: "Nutritionist Automation", heroTitle: "Automate Meal Plans.", heroSub: "Generate standard plans from preferences.", painPoint: "custom planning time", exampleAutomation: "Plan Generator", metaDesc: "Nutrition Automation." },
    "urgent-care-automation": { title: "Urgent Care Automation", heroTitle: "Manage Wait Times.", heroSub: "SMS updates for waiting patients.", painPoint: "angry patients", exampleAutomation: "Wait Time Notifier", metaDesc: "Urgent Care Automation." },
    "senior-care-automation": { title: "Senior Care Automation", heroTitle: "Update Families Automatically.", heroSub: "Daily activity logs sent to family.", painPoint: "family communication", exampleAutomation: "Family Update Bot", metaDesc: "Senior Care Automation." },

    // --- HOME SERVICES (10) ---
    "hvac-company-automation": { title: "HVAC Automation", heroTitle: "Automate Dispatch.", heroSub: "Route techs efficiently.", painPoint: "dispatch chaos", exampleAutomation: "Route Optimizer", metaDesc: "HVAC Automation." },
    "plumbing-business-automation": { title: "Plumber Automation", heroTitle: "Capture Emergency Calls.", heroSub: "AI voice answers 24/7.", painPoint: "missed calls", exampleAutomation: "AI Receptionist", metaDesc: "Plumbing Automation." },
    "roofing-company-automation": { title: "Roofer Automation", heroTitle: "Follow Up Estimates.", heroSub: "Don't let bids go cold.", painPoint: "lost bids", exampleAutomation: "Bid Chaser", metaDesc: "Roofing Automation." },
    "solar-company-automation": { title: "Solar Automation", heroTitle: "Push Project Stages.", heroSub: "Auto-move projects through permitting.", painPoint: "stalled projects", exampleAutomation: "Stage Mover", metaDesc: "Solar Automation." },
    "landscaping-business-automation": { title: "Landscaper Automation", heroTitle: "Automate Seasonal Upsells.", heroSub: "Pitch aeration/cleanups automatically.", painPoint: "manual sales", exampleAutomation: "Seasonal Upseller", metaDesc: "Landscaping Automation." },
    "pest-control-automation": { title: "Pest Control Automation", heroTitle: "Schedule Regular Service.", heroSub: "Auto-book quarterly sprays.", painPoint: "scheduling recurring", exampleAutomation: "Quarterly Scheduler", metaDesc: "Pest Automation." },
    "cleaning-business-automation": { title: "Cleaning Business Automation", heroTitle: "Manage Crews & supplies.", heroSub: "Auto-restock and schedule.", painPoint: "inventory/scheduling", exampleAutomation: "Ops Dashboard", metaDesc: "Cleaning Automation." },
    "moving-company-automation": { title: "Moving Company Automation", heroTitle: "Automate Quote Follow-up.", heroSub: "Convert more quote requests.", painPoint: "shoppers ghosting", exampleAutomation: "Quote Converter", metaDesc: "Moving Automation." },
    "general-contractor-automation": { title: "GC Automation", heroTitle: "Collect Subcontractor Bids.", heroSub: "Auto-request bids from subs.", painPoint: "chasing subs", exampleAutomation: "Bid Collector", metaDesc: "GC Automation." },
    "electrician-automation": { title: "Electrician Automation", heroTitle: "Automate Invoicing.", heroSub: "Bill immediately upon job completion.", painPoint: "slow billing", exampleAutomation: "Instant Invoicer", metaDesc: "Electrician Automation." }
};

export const integrations: Record<string, {
    toolName: string;
    heroTitle: string;
    heroSub: string;
    painPoint: string;
    exampleAutomation: string;
    metaDesc: string;
}> = {
    // CRM
    "hubspot-automation-expert": { toolName: "HubSpot", heroTitle: "Revive Dead Leads.", heroSub: "Advanced HubSpot workflows.", painPoint: "dead leads", exampleAutomation: "Lead Reviver", metaDesc: "HubSpot Experts." },
    "salesforce-consultant-alternative": { toolName: "Salesforce", heroTitle: "Fix Broken Data.", heroSub: "Clean up your Salesforce instance.", painPoint: "dirty data", exampleAutomation: "Data Cleaner", metaDesc: "Salesforce Cleanup." },
    "pipedrive-automation-expert": { toolName: "Pipedrive", heroTitle: "Drive More Sales.", heroSub: "Automate activity logging.", painPoint: "manual logging", exampleAutomation: "Activity Sync", metaDesc: "Pipedrive Automation." },
    "zoho-crm-automation": { toolName: "Zoho CRM", heroTitle: "Untangle Zoho.", heroSub: "Streamline Zoho One apps.", painPoint: "app confusion", exampleAutomation: "Zoho Unifier", metaDesc: "Zoho Experts." },
    "gohighlevel-snapshot-expert": { toolName: "GoHighLevel", heroTitle: "Scale Agencies.", heroSub: "Deploy snapshots instantly.", painPoint: "setup time", exampleAutomation: "Snapshot Deployer", metaDesc: "GHL Experts." },
    "activecampaign-automation": { toolName: "ActiveCampaign", heroTitle: "Better Email Logic.", heroSub: "Complex segmentation made easy.", painPoint: "bad segments", exampleAutomation: "Segmentor Bot", metaDesc: "ActiveCampaign Experts." },
    "keap-automation": { toolName: "Keap", heroTitle: "Automate Infusionsoft.", heroSub: "Legacy campaigns modernized.", painPoint: "clunky campaigns", exampleAutomation: "Campaign Refresher", metaDesc: "Keap Experts." },
    "close-crm-automation": { toolName: "Close", heroTitle: "Close More Deals.", heroSub: "Power dialer automations.", painPoint: "slow dialing", exampleAutomation: "Dialer Sync", metaDesc: "Close CRM Experts." },

    // PM
    "clickup-automation-expert": { toolName: "ClickUp", heroTitle: "Agency OS in ClickUp.", heroSub: "Standardize every project.", painPoint: "messy tasks", exampleAutomation: "Template Enforcer", metaDesc: "ClickUp Experts." },
    "monday-com-automation": { toolName: "Monday.com", heroTitle: "Automate Boards.", heroSub: "Connect boards to email.", painPoint: "manual updates", exampleAutomation: "Board Syncer", metaDesc: "Monday.com Experts." },
    "asana-automation-specialist": { toolName: "Asana", heroTitle: "Streamline Asana.", heroSub: "Auto-create projects from sales.", painPoint: "handover lag", exampleAutomation: "Sales-to-PM Flow", metaDesc: "Asana Experts." },
    "notion-automation-expert": { toolName: "Notion", heroTitle: "Notion Business OS.", heroSub: "Connect Notion to tools.", painPoint: "siloed info", exampleAutomation: "Notion Syncer", metaDesc: "Notion Experts." },
    "airtable-automation-consultant": { toolName: "Airtable", heroTitle: "Airtable Backends.", heroSub: "Scripting and interfaces.", painPoint: "spreadsheet limits", exampleAutomation: "Interface Builder", metaDesc: "Airtable Experts." },
    "trello-automation": { toolName: "Trello", heroTitle: "Butler Automation.", heroSub: "Max out Trello power-ups.", painPoint: "card chaos", exampleAutomation: "Card Butler", metaDesc: "Trello Experts." },
    "jira-automation": { toolName: "Jira", heroTitle: "Dev Ops Automation.", heroSub: "Sync Jira with support.", painPoint: "dev disconnect", exampleAutomation: "Support-Dev Sync", metaDesc: "Jira Experts." },
    "basecamp-automation": { toolName: "Basecamp", heroTitle: "Organize Basecamp.", heroSub: "Auto-archive old projects.", painPoint: "clutter", exampleAutomation: "Project Archiver", metaDesc: "Basecamp Experts." },

    // OPS
    "zapier-expert-consultant": { toolName: "Zapier", heroTitle: "Fix Broken Zaps.", heroSub: "Optimize and reduce costs.", painPoint: "zap errors", exampleAutomation: "Error Handler", metaDesc: "Zapier Experts." },
    "make-com-specialist": { toolName: "Make.com", heroTitle: "Complex Scenarios.", heroSub: "Multi-branch logic.", painPoint: "simple zap limits", exampleAutomation: "Logic Master", metaDesc: "Make.com Experts." },
    "n8n-workflow-developer": { toolName: "n8n", heroTitle: "Self-Hosted Flows.", heroSub: "Private data automation.", painPoint: "privacy concerns", exampleAutomation: "Private Flow", metaDesc: "n8n Experts." },
    "slack-automation-bot": { toolName: "Slack", heroTitle: "Custom Slack Bots.", heroSub: "Interactive internal tools.", painPoint: "context switching", exampleAutomation: "Internal Tool Bot", metaDesc: "Slack Experts." },
    "quickbooks-online-automation": { toolName: "QuickBooks", heroTitle: "Auto-Invoicing.", heroSub: "Stripe to QBO sync.", painPoint: "manual data entry", exampleAutomation: "Payment Syncer", metaDesc: "QBO Experts." },
    "xero-automation-expert": { toolName: "Xero", heroTitle: "Xero Reconciliation.", heroSub: "Bank feed automation.", painPoint: "reconciliation", exampleAutomation: "Bank Feed Fix", metaDesc: "Xero Experts." },
    "stripe-automation": { toolName: "Stripe", heroTitle: "Payment Ops.", heroSub: "Failed payment recovery.", painPoint: "churn", exampleAutomation: "Dunning Bot", metaDesc: "Stripe Experts." },
    "shopify-automation": { toolName: "Shopify", heroTitle: "E-com Flows.", heroSub: "Order tagging and routing.", painPoint: "fulfillment lag", exampleAutomation: "Tagging Bot", metaDesc: "Shopify Experts." }
};
