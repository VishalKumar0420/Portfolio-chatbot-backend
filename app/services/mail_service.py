from app.core.config.setting import get_settings
import requests

settings = get_settings()


def send_otp_email(email: str, otp: str):
    url = "https://api.brevo.com/v3/smtp/email"

    print("Sending email to:", email)
    print("Using API KEY:", settings.BREVO_API_KEY)
    print("Using FROM EMAIL:", settings.FROM_EMAIL)

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

    print("Brevo Status Code:", response.status_code)
    print("Brevo Response:", response.text)

    if response.status_code != 201:
        raise Exception(f"Email failed: {response.text}")
