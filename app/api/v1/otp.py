from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.constants import OTP_PURPOSE_LOGIN
from app.db.session import get_db
from app.models.otp import OTP
from app.models.user import User
from app.schemas.otp import OTP_Request
from app.services.otp_service import create_user_otp, send_otp_email
from fastapi import HTTPException, status


router = APIRouter(prefix="/otp", tags=["OTP"])


@router.post("/send", operation_id="send-otp")
async def send_otp(
    request: OTP_Request,
    db: Session = Depends(get_db),
    purpose: str = OTP_PURPOSE_LOGIN,
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    otp = create_user_otp(user.id, db, purpose=purpose)
    await send_otp_email(user.email, otp.code)
    return {"message": "OTP send successfuly", "otp_id": str(otp.id)}


@router.get("/verify", operation_id="verify-otp")
async def verify_otp(
    email: str,
    otp_code: str,
    db: Session = Depends(get_db),
    purpose: str = OTP_PURPOSE_LOGIN,
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    otp = (
        db.query(OTP)
        .filter(
            OTP.user_id == user.id,
            OTP.code == otp_code,
            OTP.purpose == purpose,
            OTP.is_used == False,
            OTP.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid or Expired OTP"
        )

    otp.is_used = True
    db.commit()

    return {"message": "OTP verified successfully"}


@router.post("/resend", operation_id="resend-otp")
async def resend_otp(
    request: OTP_Request,
    db: Session = Depends(get_db),
    purpose: str = OTP_PURPOSE_LOGIN,
):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    otp = create_user_otp(user.id, db, purpose=purpose)
    await send_otp_email(user.email,otp.code)
    db.add(otp)
    db.commit()
    
    return {"message":"OTP resend successfully"}