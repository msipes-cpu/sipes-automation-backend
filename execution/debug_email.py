import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load env from parent dir if testing locally
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def test_email():
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    
    # Use a hardcoded recipient for testing, or use the sender
    to_email = sender 

    print(f"Testing Email...")
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"User: {sender}")
    # Don't print password!

    if not sender or not password:
        print("ERROR: SENDER_EMAIL or SENDER_PASSWORD not found.")
        return

    msg = MIMEMultipart()
    msg['From'] = f"Sipes Automation <{sender}>"
    msg['To'] = to_email
    msg['Subject'] = "Test Email from Sipes Automation Debugger"
    
    body = "If you are reading this, the email credentials are correct."
    msg.attach(MIMEText(body, 'plain'))

    try:
        if smtp_port == 465:
            print("Using SMTP_SSL for port 465")
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            # server.starttls() # Not needed for SSL
        else:
            print(f"Using SMTP + STARTTLS for port {smtp_port}")
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
        server.login(sender, password)
        text = msg.as_string()
        server.sendmail(sender, to_email, text)
        server.quit()
        print("SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"FAILURE: Could not send email. Error: {str(e)}")

if __name__ == "__main__":
    test_email()
