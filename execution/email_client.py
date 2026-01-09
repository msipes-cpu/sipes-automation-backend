import os
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Load env vars
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465)) # 465 for SSL, 587 for TLS
SMTP_USER = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_NAME = "Michael Sipes"

def send_email(to_email, subject, body, attachment_path=None, is_html=False):
    if not SMTP_USER or not SMTP_PASSWORD:
        print("Error: SMTP_EMAIL or SMTP_PASSWORD not set in .env")
        return False

    msg = MIMEMultipart()
    # Format: "Michael Sipes <msipes@sipesautomation.com>"
    msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    try:
        print(f"Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
        
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.starttls()
            
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("Sending mail...")
        text = msg.as_string()
        server.sendmail(SMTP_USER, to_email, text)
        server.quit()
        print(f"Email sent successfully to {to_email}!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send Email via SMTP")
    parser.add_argument("--to", required=True, help="Recipient email")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", required=True, help="Email body")
    parser.add_argument("--attachment", help="Path to attachment")
    parser.add_argument("--html", action="store_true", help="Send as HTML")
    
    args = parser.parse_args()
    
    # Handle newlines in body (only needed for plain text mainly, but good for HTML source too)
    body = args.body.replace('\\n', '\n')
    
    send_email(args.to, args.subject, body, args.attachment, is_html=args.html)
