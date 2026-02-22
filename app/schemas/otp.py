from pydantic import BaseModel, EmailStr
from enum import Enum
from app.core.config.constants import OTP_PURPOSE_PASSWORD_RESET
from app.schemas.user import ResponseData

class OTPPurpose(str, Enum):
    signup = "signup"
    login = "login"
    reset_password = "reset_password"

class OTPRequest(BaseModel):
    email: EmailStr
    purpose: OTPPurpose


class OTPResponse(BaseModel):
    message: str
    data:ResponseData

class VerifyOTPResquest(BaseModel):
    email: EmailStr
    otp_code: str

class VerifyOTPResponse(BaseModel):
    message:str
    success:bool