from fastapi import BackgroundTasks, HTTPException, status
from app.models.user import User
from app.schemas.otp import OTP_Request
from app.services.mail_service import send_otp_email
from app.services.redis_otp import store_otp, verify_otp
from sqlalchemy.orm import Session


async def create_user_otp(
    request: OTP_Request, background_tasks: BackgroundTasks, db: Session, purpose: str
) -> str:
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    otp_code = await store_otp(str(user.id), purpose)

    # background_tasks.add_task(
    #     send_otp_email,
    #     user.email,
    #     otp_code,
    # )

    return {"message": "OTP sent successfully"}


async def verify_user_otp(
    email: str,
    otp_code: str,
    db: Session,
    purpose: str,
) -> bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    #  verify OTP in Redis
    is_valid = await verify_otp(str(user.id), otp_code, purpose)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )
    if not user.is_verified:
        user.is_verified = True
        db.commit()

    return {"message": "OTP verified successfully"}
