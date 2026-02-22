from uuid import UUID

from pydantic import BaseModel, EmailStr
from typing import Generic, Optional, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    message: str
    success: bool = True
    data: Optional[T] = None

class UserData(BaseModel):
    user_id: UUID
    email: EmailStr