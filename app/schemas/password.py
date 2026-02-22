from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import ResponseData

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=6)



class PasswordResponse(BaseModel):
    message: str
    success:bool
    data:ResponseData