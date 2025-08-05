import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
BASE_URL = os.getenv("BASE_URL")


def send_verification_email(to_email: str, token: str):
    verification_link = f"{BASE_URL}/verify-email?token={token}"
    msg = MIMEText(f"Привіт! Натисни, щоб підтвердити свою пошту: {verification_link}")
    msg["Subject"] = "Підтвердження пошти"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
