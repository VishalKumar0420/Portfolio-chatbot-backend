from datetime import datetime, timezone
from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.api.v1.otp import send_otp
from app.core.constants import OTP_PURPOSE_PASSWORD_RESET
from app.db.session import get_db
from app.models.otp import OTP
from app.models.user import User
from app.schemas.otp import OTP_Request
from app.services.otp_service import create_user_otp, send_otp_email
from app.core.security import hash_password

router = APIRouter(prefix="/password", tags=["PASSWORD"])


@router.post("/forget", operation_id="forget_password")
async def forget_password(request: OTP_Request = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not Found"
        )

    otp = create_user_otp(user.id, db, purpose=OTP_PURPOSE_PASSWORD_RESET)
    await send_otp_email(user.email, otp.code)
    return {"message": "OTP send successfuly", "otp_id": str(otp.id)}


@router.post("/reset", operation_id="reset-password")
def reset_password(
    email: str, otp_code: str, new_password: str, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not Found"
        )

    otp = (
        db.query(OTP)
        .filter(
            OTP.user_id == user.id,
            OTP.code == otp_code,
            OTP.purpose == OTP_PURPOSE_PASSWORD_RESET,
            OTP.is_used == False,
            OTP.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )

    if not otp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="OTP is invalid or expires"
        )

    user.password=hash_password(new_password)
    otp.is_used=True
    db.commit()

    return {"message":"Password  reset successfully"}