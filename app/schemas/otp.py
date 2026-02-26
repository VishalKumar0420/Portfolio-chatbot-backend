from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class OTPPurpose(str, Enum):
    signup = "signup"
    login = "login"
    reset_password = "reset_password"


class SendOTPRequest(BaseModel):
    email: EmailStr
    purpose: OTPPurpose


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    purpose: OTPPurpose