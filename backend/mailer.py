import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# load .env 
load_dotenv()

# call Data from .env
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT = os.getenv("RECIPIENT")

# Check if credentials are available
if not GMAIL_USER or not GMAIL_APP_PASSWORD:
    raise RuntimeError("GMAIL Zugangsdaten fehlen (.env prüfen)")

# create E-Mail 
msg = EmailMessage()
msg["From"] = GMAIL_USER
msg["To"] = RECIPIENT
msg["Subject"] = "Testmail aus Python"
msg.set_content("Hallo!\n\nDiese Mail wurde mit Python gesendet.")

# SMTP-Connection and send mail
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    server.send_message(msg)

print("Mail gesendet!")
