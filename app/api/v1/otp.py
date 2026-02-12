from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_LOGIN
from app.core.db.session import get_db
from app.models.user import User
from app.schemas.otp import OTP_Request
from fastapi import HTTPException, status
from app.services.mail_service import send_otp_email
from app.services.redis_otp import store_otp,verify_otp


router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/send", operation_id="send-otp")
async def send_otp(
    request: OTP_Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    purpose: str = OTP_PURPOSE_LOGIN,
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    otp_code = await store_otp(str(user.id), purpose)

    # 🔥 background email
    background_tasks.add_task(
        send_otp_email,
        user.email,
        otp_code,
    )

    return {"message": "OTP sent successfully"}



@router.get("/verify", operation_id="verify-otp")
async def verify_otp_endpoint(
    email: str,
    otp_code: str,
    purpose: str = OTP_PURPOSE_LOGIN,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    is_valid = await verify_otp(user.id, otp_code, purpose)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # ✅ mark verified
    user.is_verified = True
    db.commit()

    return {"message": "OTP verified successfully"}



# @router.post("/resend", operation_id="resend-otp")
# async def resend_otp(
#     request: OTP_Request,
#     db: Session = Depends(get_db),
#     purpose: str = OTP_PURPOSE_LOGIN,
# ):
#     user = db.query(User).filter(User.email == request.email).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )

#     otp = create_user_otp(user.id, db, purpose=purpose)
#     await send_otp_email(user.email, otp.code)
#     db.add(otp)
#     db.commit()

#     return {"message": "OTP resend successfully"}
