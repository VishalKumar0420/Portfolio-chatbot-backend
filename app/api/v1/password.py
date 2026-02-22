from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET
from app.core.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.password import ResetPasswordRequest
from app.services.password_service import forget_password, reset_password

router = APIRouter(prefix="/password", tags=["PASSWORD"])


@router.post(
    "/forget",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    operation_id="forget_password",
)
async def forget_user_password(
    email: EmailStr,
    db: Session = Depends(get_db),
):
    return await forget_password(email, db=db, purpose=OTP_PURPOSE_PASSWORD_RESET)


@router.post(
    "/reset",
    response_model=APIResponse,
    operation_id="reset_password",
    status_code=status.HTTP_200_OK,
)
async def reset_user_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    return await reset_password(
        request=request, db=db, purpose=OTP_PURPOSE_PASSWORD_RESET
    )
