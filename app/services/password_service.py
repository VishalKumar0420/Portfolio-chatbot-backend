from fastapi import HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET
from app.models.user import User
from app.schemas.otp import OTP_Request
from app.schemas.password import PasswordRequest, PasswordResetRequest
from app.core.config.security import hash_password
from app.services.mail_service import send_otp_email
from app.services.otp_rate_limit import check_otp_rate_limit
from app.services.redis_otp import store_otp, verify_otp


async def forget_password(
    request: PasswordRequest,
    db: Session,
    purpose=OTP_PURPOSE_PASSWORD_RESET,
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2️⃣ Rate limit OTP requests
    check_otp_rate_limit(str(user.id), purpose)
    otp_code = await store_otp(str(user.id), purpose)

    try:
        send_otp_email(user.email, otp_code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP email",
        )

    return {"message": "OTP sent successfully"}


async def reset_password(
    data: PasswordResetRequest,
    db: Session,
    purpose=OTP_PURPOSE_PASSWORD_RESET,
):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    #  Verify OTP
    is_valid = await verify_otp(str(user.id), purpose, data.otp_code)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    #  Hash new password
    user.hashed_password = hash_password(data.new_password)

    db.commit()
    db.refresh(user)

    return {"message": "Password reset successfully"}
