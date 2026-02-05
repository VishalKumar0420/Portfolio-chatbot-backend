from pydantic import BaseModel, EmailStr


class OTP_Request(BaseModel):
    email: EmailStr
