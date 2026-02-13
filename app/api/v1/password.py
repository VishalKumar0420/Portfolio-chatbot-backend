from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db.session import get_db
from app.core.config.security import hash_password
from app.models.user import User
from app.schemas.password import PasswordResetRequest
from app.schemas.otp import OTP_Request, OTPResponse
from app.services.mail_service import send_otp_email
from app.services.password_service import forget_password, reset_password
from app.services.redis_otp import store_otp, verify_otp
from app.services.otp_rate_limit import check_otp_rate_limit
from fastapi import BackgroundTasks
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET

router = APIRouter(prefix="/password", tags=["PASSWORD"])


@router.post(
    "/forget",
    response_model=OTPResponse,
    status_code=status.HTTP_200_OK,
    operation_id="forget_password",
)
async def forget_user_password(
    request: OTP_Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return await forget_password(
        request=request,
        db=db,
        background_tasks=background_tasks,
        purpose=OTP_PURPOSE_PASSWORD_RESET,
    )

@router.post(
    "/reset",
    operation_id="reset_password",
    status_code=status.HTTP_200_OK,
)
async def reset_user_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    return await reset_password(data=data, db=db, purpose=OTP_PURPOSE_PASSWORD_RESET)
