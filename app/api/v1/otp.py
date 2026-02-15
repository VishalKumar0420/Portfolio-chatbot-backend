from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_SIGNUP
from app.core.db.session import get_db
from app.schemas.otp import OTP_Request, OTPResponse
from fastapi import status
from app.services.otp_service import create_user_otp, verify_user_otp
from pydantic import EmailStr

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/send", operation_id="send-otp",response_model=OTPResponse,status_code=status.HTTP_200_OK)
async def send_otp(
    request: OTP_Request,
    db: Session = Depends(get_db),
):
    return await create_user_otp(
        request=request,
        db=db,
    )


@router.post("/verify", operation_id="verify-otp",status_code=status.HTTP_200_OK)
async def verify_otp_endpoint(
    email: EmailStr,
    otp_code: str,
    db: Session = Depends(get_db),
):
    return await verify_user_otp(email=email,otp_code=otp_code,db=db,purpose=OTP_PURPOSE_SIGNUP)


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
