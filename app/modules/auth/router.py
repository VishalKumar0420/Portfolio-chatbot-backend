"""
Auth router: registers all auth, OTP, and password routes.

Routes are kept thin — they delegate immediately to the controller.
"""

from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.config.constants import OTP_PURPOSE_SIGNUP
from app.config.database import get_db
from app.modules.auth import controller
from app.modules.auth.schema import (
    OTPPurpose,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserSignupRequest,
    UserLoginRequest,
    VerifyOTPRequest,
    UserProfileResoponse
)
from app.schemas.response import APIResponse
from app.middleware.auth import verify_token
_BEARER_SECURITY = [{"BearerAuth": []}]
# ── Auth ──────────────────────────────────────────────────────────────────────
auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/signup",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new account and sends a verification OTP to the email.",
    operation_id="signup",
)
async def signup(data: UserSignupRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    return await controller.handle_signup(data=data, db=db)


@auth_router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Login with email and password",
    description="Authenticates the user and returns a JWT access token and refresh token.",
    operation_id="login"
)
def login(data: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return token pair."""
    return controller.handle_login(data=data, db=db)


@auth_router.get(
    "/profile",
    response_model=APIResponse[UserProfileResoponse],
    status_code=status.HTTP_200_OK,
    summary="User data & Profile data",
    description="Verify User data based on that fetch profile data",
    operation_id="get_profile",
    openapi_extra={"security": _BEARER_SECURITY},
)
async def get_profile(db: Session = Depends(get_db),user_id: str = Depends(verify_token)):
    """Get User Profile"""
    return await controller.handle_user_profile(db=db,user_id=user_id)


@auth_router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token",
    description="Exchanges a valid refresh token for a new access + refresh token pair.",
    operation_id="refresh_token",
)
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Rotate the refresh token."""
    return controller.handle_refresh_token(data=data, db=db)


# ── OTP ───────────────────────────────────────────────────────────────────────
otp_router = APIRouter(prefix="/otp", tags=["OTP"])


@otp_router.post(
    "/send",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Send OTP to email",
    description="Generates and emails a 6-digit OTP for the given purpose (signup / login / reset_password).",
    operation_id="send_otp",
)
async def send_otp(
    email: EmailStr,
    purpose: OTPPurpose,
    db: Session = Depends(get_db),
):
    """Send a one-time password to the user's email."""
    return await controller.handle_send_otp(email=email, purpose=purpose, db=db)


@otp_router.post(
    "/verify",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify OTP",
    description="Validates the OTP. Marks the account as verified when purpose is signup.",
    operation_id="verify_otp",
)
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    """Verify the submitted OTP code."""
    return await controller.handle_verify_otp(
        request=request, purpose=OTP_PURPOSE_SIGNUP, db=db
    )


# ── Password ──────────────────────────────────────────────────────────────────
password_router = APIRouter(prefix="/password", tags=["Password"])


@password_router.post(
    "/forget",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Request password reset OTP",
    description="Sends a password-reset OTP to the user's registered email.",
    operation_id="forget_password",
)
async def forget_password(email: EmailStr, db: Session = Depends(get_db)):
    """Trigger a password-reset OTP email."""
    return await controller.handle_forget_password(email=email, db=db)


@password_router.post(
    "/reset",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password with OTP",
    description="Verifies the OTP and updates the user's password.",
    operation_id="reset_password",
)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Verify OTP and set a new password."""
    return await controller.handle_reset_password(request=request, db=db)
