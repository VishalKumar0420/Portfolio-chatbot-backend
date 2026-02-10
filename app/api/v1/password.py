from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.config.security import hash_password
from app.models.user import User
from app.schemas.password import PasswordResetRequest
from app.schemas.otp import OTP_Request
from app.services.otp_service import send_otp_email
from app.services.redis_otp import store_otp, verify_otp
from app.services.otp_rate_limit import check_otp_rate_limit
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET

router = APIRouter(prefix="/password", tags=["PASSWORD"])


@router.post("/forget", operation_id="forget_password")
async def forget_password(
    request: OTP_Request = Body(...),
    db: Session = Depends(get_db),
    purpose=OTP_PURPOSE_PASSWORD_RESET
):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2. Rate limit OTP requests
    check_otp_rate_limit(str(user.id),purpose)

    # 3. Store OTP in Redis (5 minutes TTL)
    otp_code =await store_otp(str(user.id), purpose)

    # 4. Send OTP via email
    await send_otp_email(user.email, otp_code)

    return {"message": "OTP sent successfully"}


@router.post("/reset", operation_id="reset_password")
def reset_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
    purpose=OTP_PURPOSE_PASSWORD_RESET
):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 2. Verify OTP from Redis
    if not verify_otp(str(user.id), purpose, data.otp_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password reset successfully"}
