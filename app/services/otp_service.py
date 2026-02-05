import random
import uuid
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from app.core.config.setting import settings
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone, timedelta
import os

from app.models.otp import OTP

# Email config
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


def generate_otp_code(length=6):
    return str(random.randint(10 ** (length - 1), ((10**length) - 1)))


async def send_otp_email(email: str, otp_code: str):
    message = MessageSchema(
        subject="Your OTP code",
        recipients=[email],
        body=f"Your OTP code is {otp_code}.It expires in {settings.OTP_EXPIRE_MINUTES} minutes.",
        subtype="plain",
    )
    fm = FastMail(conf)
    await fm.send_message(message)

def create_user_otp(user_id: uuid.UUID, db: Session,purpose:str) -> OTP:

    try:
        now = datetime.now(timezone.utc)

        db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.purpose==purpose,
            OTP.is_used==False,
            OTP.expires_at > now
        ).update(
            {OTP.is_used: True},
            synchronize_session=False
        )

        otp = OTP(
            user_id=user_id,
            code=generate_otp_code(),
            purpose=purpose,
            is_used=False,
            expires_at=now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )

        db.add(otp)
        db.commit()
        db.refresh(otp)

        return otp

    except SQLAlchemyError:
        db.rollback()
        raise 