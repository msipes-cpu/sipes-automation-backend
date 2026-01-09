# Smartlead Reports - Quick Reference

## 📊 View Reports

### Console (Instant)
```bash
# Today's stats
python3 execution/smartlead_daily_report.py

# Yesterday's stats  
python3 execution/smartlead_daily_report.py 2025-12-21

# Specific campaigns
python3 execution/smartlead_daily_report.py 2025-12-22 "2789045,2789046"
```

### Email (Manual Send)
```bash
# Send to default recipient
python3 execution/smartlead_email_report.py

# Send to custom recipient
python3 execution/smartlead_email_report.py 2025-12-22 user@example.com
```

## ⚙️ Setup Automation

### First Time Setup
1. Edit `.env` - add email config (see SMARTLEAD_REPORTS_SETUP.md)
2. Get Gmail App Password (not regular password!)
3. Run: `bash execution/setup_daily_email_cron.sh`
4. Choose time (e.g., 08:00)
5. Done! ✅

### Manage Automation
```bash
# View cron job
crontab -l

# View logs
tail -f .tmp/smartlead_email_cron.log

# Change schedule
bash execution/setup_daily_email_cron.sh

# Disable
crontab -e  # delete the smartlead line
```

## 🔑 Environment Variables

Required in `.env`:
```bash
SMARTLEAD_API_KEY=your-key-here
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
REPORT_RECIPIENT_EMAIL=recipient@example.com
```

## 📈 What You Get

- **Overall Stats**: Total sent, opened, replied, bounced
- **Performance Metrics**: Open rate, reply rate
- **Campaign Breakdown**: Individual campaign performance
- **Sorted by Volume**: Most active campaigns first

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Add `SMARTLEAD_API_KEY` to `.env` |
| "Email config missing" | Add email settings to `.env` |
| "Authentication failed" | Use Gmail App Password, not regular password |
| "No data" | Check date has activity, verify API key |
| Cron not running | Check `crontab -l`, test script manually |

## 📁 Files

- `execution/smartlead_daily_report.py` - Console report
- `execution/smartlead_email_report.py` - Email report  
- `execution/setup_daily_email_cron.sh` - Automation setup
- `directives/smartlead_*.md` - Documentation
- `SMARTLEAD_REPORTS_SETUP.md` - Full setup guide
