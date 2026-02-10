from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from app.core.config.setting import settings
from app.models.user import User
from app.services.redis_otp import store_otp, verify_otp
from sqlalchemy.orm import Session
import uuid

# Email config
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
        subject="Your OTP code",
        recipients=[email],
        body=f"Your OTP code is {otp_code}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes.",
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def create_user_otp(user_id: uuid.UUID, purpose: str) -> str:
    otp_code = await store_otp(str(user_id), purpose)
    return otp_code


async def verify_user_otp(
    db: Session,
    user_id: uuid.UUID,
    otp_code: str,
    purpose: str,
) -> bool:
    #  verify OTP in Redis
    is_valid = await verify_otp(str(user_id), otp_code, purpose)

    if not is_valid:
        return False

    #  mark user as verified
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    if not user.is_verified:
        user.is_verified = True
        db.commit()

    return True
