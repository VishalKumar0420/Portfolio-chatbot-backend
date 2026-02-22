from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

class UserCreate(BaseModel):
    full_name: str = Field(...,max_length=100)
    email: EmailStr
    password: str = Field(...,max_length=50)

    @field_validator("full_name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.strip()) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str




