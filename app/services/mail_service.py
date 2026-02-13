from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from fastapi import HTTPException
from app.core.config.setting import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_otp_email(email: str, otp_code: str):
    message = MessageSchema(
        subject="Your OTP Code",
        recipients=[email],
        body=(
            f"Your OTP code is {otp_code}.\n\n"
            f"It expires in {settings.OTP_EXPIRE_MINUTES} minutes."
        ),
        subtype="plain",
    )

    fm = FastMail(conf)

    try:
        await fm.send_message(message)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email",
        )
