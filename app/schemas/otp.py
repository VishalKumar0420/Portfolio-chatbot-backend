from pydantic import BaseModel, EmailStr
from enum import Enum


class OTPPurpose(str, Enum):
    signup = "signup"
    login = "login"
    reset_password = "reset_password"


class OTPRequest(BaseModel):
    email: EmailStr
    purpose: OTPPurpose


class VerifyOTPResquest(BaseModel):
    email: EmailStr
    otp_code: str
