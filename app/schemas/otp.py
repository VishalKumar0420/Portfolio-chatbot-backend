from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class OTP_Request(BaseModel):
    email: EmailStr
    purpose: Literal["Login", "Password Reset", "Email Verification"]


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)

class OTPResponse(BaseModel):
    message: str