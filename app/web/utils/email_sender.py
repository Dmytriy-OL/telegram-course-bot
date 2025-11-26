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
    <body style="margin:0; padding:0; background:#f5f7fa; font-family:Segoe UI, Arial, sans-serif;">
        <div style="max-width:600px; margin:40px auto; background:white; padding:30px; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.05);">

            <h2 style="color:#4f46e5;">🔐 Відновлення пароля</h2>

            <p style="font-size:15px; color:#333;">
                Ви запросили зміну пароля для вашого облікового запису LinguaPro.
            </p>

            <p style="font-size:15px;">
                Натисніть кнопку нижче, щоб встановити новий пароль:
            </p>

            <div style="text-align:center; margin:30px 0;">
                <a href="{verification_link}"
                   style="display:inline-block; padding:14px 26px; background:linear-gradient(135deg,#6366f1,#a78bfa); 
                   color:white; text-decoration:none; border-radius:30px; font-weight:600; font-size:15px;">
                    🔁 Змінити пароль
                </a>
            </div>

            <p style="font-size:14px; color:#555;">
                Якщо ви не надсилали цей запит — просто проігноруйте цей лист.
            </p>

            <hr style="margin:30px 0; border:none; border-top:1px solid #eee;">

            <p style="font-size:12px; color:#888;">
                Посилання дійсне протягом <strong>1 години</strong>.
            </p>

            <p style="font-size:12px; color:#888;">
                З повагою,<br>
                команда <strong>LinguaPro</strong>
            </p>

        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🔐 Відновлення пароля LinguaPro"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.attach(MIMEText(reset_content, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)







