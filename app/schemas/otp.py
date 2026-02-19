from pydantic import BaseModel, EmailStr
from enum import Enum
from uuid import UUID
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET

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
