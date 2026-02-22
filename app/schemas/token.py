from typing import Literal
from pydantic import BaseModel


class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    success:bool
class TokenResponse(BaseModel):
    message:str
    data:TokenData

class RefreshTokenRequest(BaseModel):
    refresh_token: str
