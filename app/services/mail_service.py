from app.core.config.setting import settings
import smtplib
from email.message import EmailMessage


def send_otp_email(email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your OTP Code"
    msg["From"] = settings.MAIL_FROM
    msg["To"] = email
    msg.set_content(f"Your OTP is: {otp}")

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(msg)
