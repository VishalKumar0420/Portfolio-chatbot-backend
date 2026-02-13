from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_LOGIN
from app.core.db.session import get_db
from app.models.user import User
from app.schemas.otp import OTP_Request
from fastapi import HTTPException, status
from app.services.mail_service import send_otp_email
from app.services.otp_service import create_user_otp, verify_user_otp
from app.services.redis_otp import store_otp, verify_otp
from app.schemas.otp import OTPResponse
from pydantic import EmailStr


router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/send", operation_id="send-otp",response_model=OTPResponse,status_code=status.HTTP_200_OK)
async def send_otp(
    request: OTP_Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return await create_user_otp(
        request=request,
        background_tasks=background_tasks,
        db=db,
        purpose=OTP_PURPOSE_LOGIN,
    )


@router.get("/verify", operation_id="verify-otp",response_model=OTPResponse)
async def verify_otp_endpoint(
    email: EmailStr,
    otp_code: str,
    db: Session = Depends(get_db),
):
    return await verify_user_otp(email=email,otp_code=otp_code,db=db,purpose=OTP_PURPOSE_LOGIN)


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
