# from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
# from fastapi import HTTPException
from app.core.config.setting import get_settings
import requests
settings = get_settings()
# conf = ConnectionConfig(
#     MAIL_USERNAME=settings.MAIL_USERNAME,
#     MAIL_PASSWORD=settings.MAIL_PASSWORD,
#     MAIL_FROM=settings.MAIL_FROM,
#     MAIL_PORT=settings.MAIL_PORT,
#     MAIL_SERVER=settings.MAIL_SERVER,
#     MAIL_STARTTLS=True,
#     MAIL_SSL_TLS=False,
#     USE_CREDENTIALS=True,
# )


# async def send_otp_email(email: str, otp_code: str):
#     print(email,otp_code,"FIRST")
#     message = MessageSchema(
#         subject="Your OTP Code",
#         recipients=[email],
#         body=(
#             f"Your OTP code is {otp_code}.\n\n"
#             f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes."
#         ),
#         subtype="plain",
#     )
#     print(message,"SECOND")

#     fm = FastMail(conf)
#     print(conf,"CONFIG")
#     print(fm,"fm")
#     try:
#         await fm.send_message(message)
#         print("FOURTH")
#     except Exception as e:
#         print("ERROR",e)
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to send OTP email",
#         )


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
        <p>This OTP will expire soon.</p>
        """
    }

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print("Brevo Status Code:", response.status_code)
    print("Brevo Response:", response.text)

    if response.status_code != 201:
        raise Exception(f"Email failed: {response.text}")
