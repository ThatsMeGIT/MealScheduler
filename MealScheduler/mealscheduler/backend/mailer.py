import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# .env laden
load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

if not GMAIL_USER or not GMAIL_APP_PASSWORD:
    raise RuntimeError("GMAIL Zugangsdaten fehlen (.env prüfen)")

# E-Mail erstellen
msg = EmailMessage()
msg["From"] = GMAIL_USER
msg["To"] = ""
msg["Subject"] = "Testmail aus Python"
msg.set_content("Hallo!\n\nDiese Mail wurde mit Python gesendet.")

# SMTP-Verbindung (Gmail)
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
    server.send_message(msg)

print("Mail gesendet!")
