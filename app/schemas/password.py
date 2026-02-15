from pydantic import BaseModel, EmailStr, Field

from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET

class PasswordResetRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=6)

class PasswordRequest(BaseModel):
    email:EmailStr
    Password:str