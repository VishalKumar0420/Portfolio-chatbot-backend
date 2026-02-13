from typing import Literal
from pydantic import BaseModel, EmailStr, Field


class OTP_Request(BaseModel):
    email: EmailStr
    purpose: Literal["Login", "Password Reset", "Email Verification"]


class OTPResponse(BaseModel):
    message: str
