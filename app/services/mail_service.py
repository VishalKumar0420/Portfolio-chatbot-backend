from app.core.config.setting import get_settings
import requests


def send_otp_email(email: str, otp: str):
    settings = get_settings()

    if not settings.BREVO_API_KEY or not settings.FROM_EMAIL:
        raise RuntimeError(
            "Email service not configured (BREVO_API_KEY or FROM_EMAIL missing)"
        )

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"email": settings.FROM_EMAIL},
        "to": [{"email": email}],
        "subject": "Your OTP Code",
        "htmlContent": f"""
        <h2>Your OTP Code</h2>
        <p>Your OTP is:</p>
        <h1>{otp}</h1>
        <p>This OTP will expire in 5 minutes.</p>
        """,
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        raise Exception(f"Email failed: {response.text}")
