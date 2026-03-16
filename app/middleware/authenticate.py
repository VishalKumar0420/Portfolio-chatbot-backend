from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from app.core.config.security import decode_token

security = HTTPBearer()


async def token_verify(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials
    
    access_token=token.split(" ")[1]
    

    try:
        payload = decode_token(access_token,"")
        

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired"
        )