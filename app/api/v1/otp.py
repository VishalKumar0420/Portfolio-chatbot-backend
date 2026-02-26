from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas import APIResponse, UserData
from app.schemas.otp import OTPPurpose, SendOTPRequest, VerifyOTPRequest
from app.services.otp_service import create_user_otp, verify_user_otp

router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post(
    "/send",
    response_model=APIResponse[UserData],
    status_code=status.HTTP_200_OK,
    operation_id="send_otp",
)
async def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db),
):
    return await create_user_otp(
        email=request.email,
        purpose=request.purpose,
        db=db,
    )


@router.post(
    "/verify",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    operation_id="verify_otp",
)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    return await verify_user_otp(
        request=request,
        db=db,
        purpose=request.purpose,
    )


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
