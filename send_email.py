import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
print("Loading environment variables from .env file...")
# Get email configuration from .env file
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = EMAIL_USER
EMAIL_TO = "standarsov@outlook.com"
EMAIL_FROM_NAME = "Walkdata DB Results"
# Create the email message
msg = MIMEText("This is a test message.")
msg["Subject"] = "Trying out emailing through the relay"
msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"  # Include display name
msg["To"] = EMAIL_TO

# Connect to the SMTP server and send the email
try:
    print("Connecting to SMTP server...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    server.set_debuglevel(1)  # optional: shows SMTP conversation

    server.ehlo()
    print("Starting TLS...")
    server.starttls()
    server.ehlo()

    print("Logging in...")
    server.login(EMAIL_USER, EMAIL_PASSWORD)

    print(f"Sending email to {EMAIL_TO}...")
    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    print(f"✅ Email sent successfully to {EMAIL_TO}")

except Exception as e:
    print(f"❌ Error sending email: {str(e)}")

finally:
    try:
        server.quit()
    except:
        pass
