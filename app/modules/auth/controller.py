"""
Auth controller: thin layer between HTTP routes and the auth service.

Responsible for building APIResponse envelopes — the service returns
plain data, the controller wraps it in the standard response shape.
"""

from fastapi import status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.modules.auth import service
from app.modules.auth.schema import (
    OTPPurpose,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserSignupRequest,
    UserLoginRequest,
    VerifyOTPRequest,
)
from app.schemas.response import APIResponse


async def handle_signup(data: UserSignupRequest, db: Session) -> APIResponse[UserResponse]:
    """Handle user registration and return a 201 response."""
    message, user_data = await service.signup(db=db, data=data)
    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message=message,
        data=user_data,
    )


def handle_login(data: UserLoginRequest, db: Session) -> APIResponse[TokenResponse]:
    """Handle login and return access + refresh tokens."""
    tokens = service.login(db=db, email=data.email, password=data.password)
    return APIResponse(message="Login successful", data=tokens)


def handle_refresh_token(data: RefreshTokenRequest, db: Session) -> APIResponse[TokenResponse]:
    """Handle refresh token rotation and return a new token pair."""
    tokens = service.rotate_refresh_token(data.refresh_token, db=db)
    return APIResponse(message="Token refreshed successfully", data=tokens)


async def handle_send_otp(
    email: EmailStr, purpose: OTPPurpose, db: Session
) -> APIResponse[UserResponse]:
    """Handle OTP generation and email dispatch."""
    user_data = await service.send_otp(email=email, purpose=purpose, db=db)
    return APIResponse(message="OTP sent successfully", data=user_data)


async def handle_verify_otp(
    request: VerifyOTPRequest, purpose: str, db: Session
) -> APIResponse:
    """Handle OTP verification and account activation."""
    await service.verify_otp(request=request, purpose=purpose, db=db)
    return APIResponse(message="OTP verified successfully")


async def handle_forget_password(
    email: EmailStr, db: Session
) -> APIResponse[UserResponse]:
    """Handle forgot-password OTP dispatch."""
    user_data = await service.forget_password(email=email, db=db)
    return APIResponse(message="Password reset OTP sent successfully", data=user_data)


async def handle_reset_password(
    request: ResetPasswordRequest, db: Session
) -> APIResponse:
    """Handle OTP verification and password update."""
    await service.reset_password(request=request, db=db)
    return APIResponse(message="Password reset successfully")
