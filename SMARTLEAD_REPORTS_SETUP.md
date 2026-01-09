# Smartlead Daily Reports - Setup Guide

## 🎯 Overview

You now have a complete automated reporting system for your Smartlead cold email campaigns with:
- ✅ **Campaign-by-campaign breakdowns** showing individual performance
- ✅ **Automated daily email reports** sent on schedule
- ✅ **Console reports** for on-demand viewing

---

## 📊 Features

### Console Report
- Overall email activity (sent, opened, replied, bounced)
- Performance metrics (open rate, reply rate)
- **Campaign-by-campaign breakdown** sorted by volume
- Individual campaign metrics

### Email Report
- Same data as console report
- Beautiful HTML formatting
- Automated daily delivery
- Plain text fallback for compatibility

---

## 🚀 Quick Start

### 1. View Today's Report (Console)
```bash
python3 execution/smartlead_daily_report.py
```

### 2. Set Up Automated Email Reports

#### Step 1: Configure Email Settings
Edit your `.env` file and uncomment/fill in these lines:

```bash
# Email Configuration for Smartlead Daily Reports
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
REPORT_RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

#### Step 2: Get Gmail App Password
1. Go to [Google Account Settings](https://myaccount.google.com/) → Security
2. Enable **2-Factor Authentication** (required)
3. Search for "App Passwords"
4. Generate a new App Password for "Mail"
5. Copy the 16-character password
6. Use this in `SENDER_PASSWORD` (not your regular Gmail password)

#### Step 3: Run Setup Script
```bash
bash execution/setup_daily_email_cron.sh
```

The script will:
- Validate your email configuration
- Ask what time to send daily reports (default: 8:00 AM)
- Install a cron job to automate the reports
- Show you how to verify and manage the automation

#### Step 4: Test Email (Optional)
```bash
python3 execution/smartlead_email_report.py
```

---

## 📖 Usage Examples

### Console Reports

```bash
# Today's report
python3 execution/smartlead_daily_report.py

# Specific date
python3 execution/smartlead_daily_report.py 2025-12-21

# Specific campaigns only
python3 execution/smartlead_daily_report.py 2025-12-22 "2789045,2789046"
```

### Email Reports

```bash
# Send today's report to default recipient
python3 execution/smartlead_email_report.py

# Send specific date to specific recipient
python3 execution/smartlead_email_report.py 2025-12-21 custom@example.com
```

---

## 🔧 Managing Automated Reports

### View Installed Cron Job
```bash
crontab -l
```

### View Email Logs
```bash
tail -f .tmp/smartlead_email_cron.log
```

### Disable Automated Reports
```bash
crontab -e
# Delete the line containing 'smartlead_email_report.py'
```

### Change Schedule Time
```bash
bash execution/setup_daily_email_cron.sh
# Choose 'y' to replace existing job
# Enter new time
```

---

## 📧 Sample Report Output

```
╔══════════════════════════════════════════════════════════╗
║          SMARTLEAD DAILY REPORT - 2025-12-22           ║
╚══════════════════════════════════════════════════════════╝

📧 OVERALL EMAIL ACTIVITY
   ├─ Sent:        2,340
   ├─ Opened:      0
   ├─ Replied:     5
   └─ Bounced:     0

📈 OVERALL PERFORMANCE METRICS
   ├─ Open Rate:   0.00%
   └─ Reply Rate:  0.27%

══════════════════════════════════════════════════════════
📊 CAMPAIGN-BY-CAMPAIGN BREAKDOWN
══════════════════════════════════════════════════════════

1. Regional Accounting - 12-22
   ├─ Sent:        1,350
   ├─ Replied:     4
   ├─ Reply Rate:  0.30%
   └─ Opened:      0

2. Private Equity Firms - 12/17
   ├─ Sent:        990
   ├─ Replied:     0
   ├─ Reply Rate:  0.00%
   └─ Opened:      0
```

---

## 🐛 Troubleshooting

### "SENDER_EMAIL and SENDER_PASSWORD must be set"
- Make sure you've uncommented the email config lines in `.env`
- Fill in your actual email and app password

### "Authentication failed" or "Username and Password not accepted"
- You must use a Gmail App Password, not your regular password
- Make sure 2-Factor Authentication is enabled on your Google account
- Generate a new App Password if needed

### Email not received
- Check your spam folder
- Verify `REPORT_RECIPIENT_EMAIL` is correct
- Test manually first: `python3 execution/smartlead_email_report.py`
- Check logs: `cat .tmp/smartlead_email_cron.log`

### Cron job not running
- Verify installation: `crontab -l`
- Check system logs: `grep CRON /var/log/system.log`
- Test the script manually first
- Make sure the script has execute permissions

### "No data available"
- The date you're querying may not have any activity
- Verify your Smartlead API key is correct
- Check that campaigns were active on that date

---

## 📁 File Structure

```
execution/
├── smartlead_daily_report.py       # Core stats fetching & console display
├── smartlead_email_report.py       # Email sending functionality
└── setup_daily_email_cron.sh       # Automated setup script

directives/
├── smartlead_daily_report.md       # Console report documentation
└── smartlead_automated_email.md    # Email automation documentation

.env                                 # Configuration (API keys, email settings)
.tmp/
└── smartlead_email_cron.log        # Email automation logs
```

---

## 🔐 Security Notes

- Your `.env` file is in `.gitignore` - API keys and passwords won't be committed
- Use Gmail App Passwords, never your actual Gmail password
- App Passwords are safer and can be revoked independently
- Cron logs may contain email addresses but not passwords

---

## 💡 Tips

1. **First time setup**: Test the console report first to verify API access
2. **Email testing**: Send a manual email before setting up automation
3. **Schedule timing**: Choose a time when you'll check your email (e.g., 8 AM)
4. **Multiple recipients**: The script sends to one email, but you can:
   - Use a distribution list
   - Set up email forwarding rules
   - Modify the script to support multiple recipients

---

## 🎉 You're All Set!

Your Smartlead reporting system is ready to go. Run the console report now to see your stats, then set up email automation when you're ready!

Questions? Check the directives or the troubleshooting section above.
