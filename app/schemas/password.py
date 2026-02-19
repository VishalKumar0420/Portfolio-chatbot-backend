from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=6)

class ForgetPasswordRequest(BaseModel):
    email:EmailStr

class ForgetPasswordResponse(BaseModel):
    message: str
    user_id: UUID
    email: EmailStr