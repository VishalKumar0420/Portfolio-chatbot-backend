"""
Security utilities: Argon2 password hashing and JWT token creation / decoding.
"""

from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config.settings import get_settings

settings = get_settings()
_ph = PasswordHasher()


# ── Password ──────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plain-text password with Argon2."""
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compare a plain-text password against an Argon2 hash.
    Returns False on mismatch instead of raising.
    """
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a short-lived JWT access token.

    Args:
        data: Payload dict — must include 'sub' (user_id).
        expires_delta: Custom TTL; defaults to ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived JWT refresh token.

    Args:
        data: Payload dict — must include 'sub' (user_id).
    """
    payload = data.copy()
    payload.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "type": "refresh",
        }
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: Encoded JWT string.
        expected_type: 'access' or 'refresh' — enforces the token type claim.

    Raises:
        HTTPException 401: Token is invalid, expired, or wrong type.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
