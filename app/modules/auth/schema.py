"""
Auth Pydantic schemas: request bodies and response data shapes.
"""

from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.modules.resume.schema import ResumeData
# ── User ──────────────────────────────────────────────────────────────────────

class UserSignupRequest(BaseModel):
    """Request body for POST /auth/signup."""

    full_name: str = Field(..., max_length=100)
    email: EmailStr
    password: str = Field(..., max_length=50)

    @field_validator("full_name")
    @classmethod
    def name_min_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v.strip()) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Minimal user info returned after auth/OTP operations."""

    user_id: UUID
    email: EmailStr

class ChatSummary(BaseModel):
    """Single chat entry in user profile."""

    chat_id: str
    chat_name: str
    chat_content: ResumeData | None


class UserProfileResoponse(BaseModel):
    """User info + User Profile data"""

    full_name: str
    email: str
    profileData: ChatSummary | None

class UserProfileRequest(BaseModel):
    refresh_token:str


# ── Token ─────────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """JWT token pair returned after login or token refresh."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class RefreshTokenRequest(BaseModel):
    """Request body for POST /auth/refresh."""

    refresh_token: str


# ── OTP ───────────────────────────────────────────────────────────────────────

class OTPPurpose(str, Enum):
    signup = "signup"
    login = "login"
    reset_password = "reset_password"


class VerifyOTPRequest(BaseModel):
    """Request body for POST /otp/verify."""

    email: EmailStr
    otp_code: str


# ── Password ──────────────────────────────────────────────────────────────────

class ResetPasswordRequest(BaseModel):
    """Request body for POST /password/reset."""

    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=6)
