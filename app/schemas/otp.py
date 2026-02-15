from typing import Literal
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from uuid import UUID

class OTPPurpose(str, Enum):
    signup = "signup"
    login = "login"
    reset_password = "reset_password"


class OTP_Request(BaseModel):
    email: EmailStr
    purpose: OTPPurpose


class OTPResponse(BaseModel):
    message: str
    user_id: UUID
    email: EmailStr
