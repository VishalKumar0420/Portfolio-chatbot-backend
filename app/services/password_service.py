from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET
from app.models.user import User
from app.schemas.password import PasswordResponse, ResetPasswordRequest
from app.core.config.security import hash_password
from app.schemas.user import ResponseData
from app.services.mail_service import send_otp_email
from app.services.otp_rate_limit import check_otp_rate_limit
from app.services.redis_otp import store_otp, verify_otp


async def forget_password(
    email:EmailStr,
    db: Session,
    purpose:str=OTP_PURPOSE_PASSWORD_RESET
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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

    return PasswordResponse(
        message="OTP sent successfully",
        success=True,
        data=ResponseData(
            user_id=user.id,
            email=user.email,
        )
    )


async def reset_password(
    request: ResetPasswordRequest,
    db: Session,
    purpose:str=OTP_PURPOSE_PASSWORD_RESET
)->PasswordResponse:
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    #  Verify OTP
    is_valid = await verify_otp(str(user.id),request.otp_code,purpose)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    #  Hash new password
    user.hashed_password = hash_password(request.new_password)

    db.commit()
    db.refresh(user)

    return PasswordResponse(
        message="Password reset successfully",
        success=True,
        data=ResponseData(
            user_id=user.id,
            email=user.email,
        )
    )
