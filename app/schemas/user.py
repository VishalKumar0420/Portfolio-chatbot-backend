from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from app.models.user import RoleEnum


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password:str
    # role: Optional[RoleEnum] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    # role: str

    model_config = {"from_attributes": True}
