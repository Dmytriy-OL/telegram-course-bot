import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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


def password_change_notification(to_email: str, token: str):
    verification_link = f"{BASE_URL}/reset_password?token={token}"

    reset_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Відновлення пароля</h2>
            <p>Ви отримали цей лист, тому що запросили зміну пароля.</p>
            <p>Щоб скинути пароль, натисніть на кнопку нижче:</p>
            <p>
                <a href="{verification_link}" 
                   style="display:inline-block; padding:10px 20px; background-color:#ff4b2b; color:white; 
                   text-decoration:none; border-radius:5px; font-weight:bold;">
                    Змінити пароль
                </a>
            </p>
            <p>Якщо ви не надсилали запит на зміну пароля, просто проігноруйте цей лист.</p>
            <hr>
            <small>Посилання дійсне протягом 1 години.</small>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Відновлення пароля"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(reset_content, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)






