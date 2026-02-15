import uuid
from fastapi import BackgroundTasks, HTTPException, status
from app.core.config.constants import OTP_PURPOSE_SIGNUP
from app.models.user import User
from app.schemas.otp import OTP_Request, OTPResponse
from app.services.mail_service import send_otp_email
from app.services.redis_otp import store_otp, verify_otp
from sqlalchemy.orm import Session


# async def create_user_otp(request: OTP_Request, db: Session, purpose: str) -> str:
#     user = db.query(User).filter(User.email == request.email).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )

#     otp_code = await store_otp(str(user.id), purpose)
#     try:
#         send_otp_email(user.email, otp_code)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail="Failed to send OTP email",
#         )

#     return {"message": "OTP sent successfully"}


async def create_user_otp(request: OTP_Request, db: Session):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found"
        )

    if request.purpose == "signup" and user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists"
        )
    if request.purpose in ("login", "reset_password") and not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not verified"
        )

    otp_code = await store_otp(str(user.id), purpose=request.purpose)

    try:
        send_otp_email(user.email, otp_code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send  OTP",
        )
    return OTPResponse(
        message="OTP sent succssfully", user_id=user.id, email=user.email
    )


# async def create_user_otp(user_id: uuid.UUID, purpose: str) -> str:
#     otp_code = await store_otp(str(user_id), purpose)
#     return otp_code


async def verify_user_otp(
    email: str,
    otp_code: str,
    db: Session,
    purpose=OTP_PURPOSE_SIGNUP,
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
