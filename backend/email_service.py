
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

def send_email_notification(to_email: str, subject: str, html_body: str):
    """
    Sends an email using SMTP.
    Requires SMTP_EMAIL and SMTP_PASSWORD env vars.
    """
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if not smtp_email or not smtp_password:
        print("[EmailService] SMTP credentials not set. Skipping email.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(html_body, 'html'))

        # Connect to SMTP Server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_email, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_email, to_email, text)
        server.quit()
        
        print(f"[EmailService] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EmailService] Failed to send email: {e}")
        return False

def send_job_completion_email(to_email: str, sheet_url: str, job_summary: str = "Your leads have been enriched."):
    subject = "Your Leads are Ready! 🚀"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
          <h2 style="color: #2563eb;">Sipes Automation</h2>
          <p>Great news! Your lead generation job is complete.</p>
          
          <p>{job_summary}</p>
          
          <div style="margin: 30px 0; text-align: center;">
            <a href="{sheet_url}" style="background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
              Open Google Sheet
            </a>
          </div>
          
          <p style="font-size: 12px; color: #666;">
            Or copy this link: <br>
            <a href="{sheet_url}">{sheet_url}</a>
          </p>
          
          <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
          <p style="font-size: 12px; color: #999;">Sipes Automation Backend</p>
        </div>
      </body>
    </html>
    """
    return send_email_notification(to_email, subject, body)

def send_job_failure_email(to_email: str, error_details: str):
    subject = "Lead Generation Failed ⚠️"
    body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>Job Failed</h2>
        <p>Unfortunately, your lead generation job encountered an error.</p>
        <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">{error_details}</pre>
        <p>Please reply to this email for support.</p>
      </body>
    </html>
    """
    return send_email_notification(to_email, subject, body)
