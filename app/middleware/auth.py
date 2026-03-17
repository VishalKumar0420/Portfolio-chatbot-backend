"""
JWT authentication middleware.

Extracts and validates the Bearer token from the Authorization header.
Returns the authenticated user's ID (UUID string) for use in route handlers.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.config.security import decode_token

# HTTPBearer reads the Authorization: Bearer <token> header automatically
_security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> str:
    """
    Validate the JWT access token from the Authorization header.

    Returns:
        user_id (str): The authenticated user's UUID as a string.

    Raises:
        HTTPException 401: Token is missing, malformed, or expired.
    """
    try:
        payload = decode_token(credentials.credentials, expected_type="access")

        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid or expired",
        )
