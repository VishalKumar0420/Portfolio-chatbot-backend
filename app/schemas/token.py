from typing import Literal
from pydantic import BaseModel


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str
