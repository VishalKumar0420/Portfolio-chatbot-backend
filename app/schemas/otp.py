from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class OTP_Request(BaseModel):
    email: EmailStr
    purpose: Literal["signup", "login", "password_reset"]


class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)

class OTPResponse(BaseModel):
    message: str