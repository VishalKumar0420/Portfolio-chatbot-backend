"""
Auth service: core business logic for signup, login, OTP, password flows.

This layer owns all DB queries and external calls (Redis, email).
Controllers call into here and only deal with HTTP concerns.
"""

import logging
import random
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.config.constants import OTP_PURPOSE_PASSWORD_RESET, OTP_PURPOSE_SIGNUP
from app.config.redis import get_redis_client
from app.config.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.config.settings import get_settings
from app.modules.auth.model import RefreshToken, User
from app.modules.auth.schema import (
    OTPPurpose,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    UserSignupRequest,
    VerifyOTPRequest,
)

logger = logging.getLogger(__name__)

# Used only for hashing/verifying refresh tokens stored in the DB
_pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OTP rate-limit settings
_MAX_OTP_PER_HOUR = 10
_RATE_LIMIT_WINDOW = 3600  # seconds


# ── OTP helpers ───────────────────────────────────────────────────────────────

def _generate_otp() -> str:
    """Generate a random 6-digit OTP string."""
    return str(random.randint(100000, 999999))


async def _store_otp(user_id: str, purpose: str) -> str:
    """
    Generate an OTP, store it in Redis with a TTL, and enforce rate limiting.

    Raises:
        HTTPException 429: Rate limit exceeded.
    """
    settings = get_settings()
    redis = get_redis_client()

    ttl = (settings.OTP_EXPIRE_MINUTES or 5) * 60
    otp = _generate_otp()

    await redis.set(f"otp:{purpose}:{user_id}", otp, ex=ttl)
    await _check_otp_rate_limit(user_id, purpose)

    return otp


async def _check_otp_rate_limit(user_id: str, purpose: str) -> None:
    """Raise 429 if the user has exceeded the OTP request limit for this hour."""
    redis = get_redis_client()
    key = f"otp_count:{purpose}:{user_id}"
    count = await redis.incr(key)

    if count == 1:
        await redis.expire(key, _RATE_LIMIT_WINDOW)

    if count > _MAX_OTP_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again later.",
        )


async def _verify_otp(user_id: str, otp_code: str, purpose: str) -> bool:
    """
    Verify the submitted OTP against Redis. Deletes it on success (single-use).

    Returns:
        True if valid, False if missing or incorrect.
    """
    redis = get_redis_client()
    key = f"otp:{purpose}:{user_id}"
    stored = await redis.get(key)

    if not stored:
        return False

    if isinstance(stored, bytes):
        stored = stored.decode()

    if stored != otp_code:
        return False

    await redis.delete(key)
    return True


def _send_otp_email(email: str, otp: str) -> None:
    """
    Send an OTP email via Brevo. Imported inline to avoid circular imports.

    Raises:
        RuntimeError: Brevo credentials not configured.
        Exception: Brevo API returned a non-2xx status.
    """
    import requests
    from app.config.settings import get_settings

    settings = get_settings()

    if not settings.BREVO_API_KEY or not settings.FROM_EMAIL:
        raise RuntimeError("Email service not configured (BREVO_API_KEY / FROM_EMAIL missing)")

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json={
            "sender": {"email": settings.FROM_EMAIL},
            "to": [{"email": email}],
            "subject": "Your OTP Code",
            "htmlContent": (
                f"<h2>Your OTP Code</h2>"
                f"<p>Use the code below — it expires in 5 minutes.</p>"
                f"<h1 style='letter-spacing:4px'>{otp}</h1>"
                f"<p>If you did not request this, ignore this email.</p>"
            ),
        },
        headers={
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json",
        },
        timeout=10,
    )

    if response.status_code not in (200, 201):
        raise Exception(f"Brevo API error: {response.text}")


# ── Token helpers ─────────────────────────────────────────────────────────────

def _issue_tokens(user_id: str, email: str, db: Session) -> TokenResponse:
    """
    Create an access + refresh token pair and persist the refresh token hash.

    Returns:
        TokenResponse with both tokens.
    """
    settings = get_settings()
    payload = {"sub": user_id, "email": email}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    db.add(
        RefreshToken(
            user_id=user_id,
            token=_pwd_context.hash(refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


# ── Auth flows ────────────────────────────────────────────────────────────────

async def signup(db: Session, data: UserSignupRequest) -> tuple[str, UserResponse]:
    """
    Register a new user or resend OTP to an unverified account.

    Returns:
        (message, UserResponse)

    Raises:
        HTTPException 409: Email already registered and verified.
        HTTPException 500: OTP email failed to send.
    """
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        if existing.is_verified:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )
        # Resend OTP for unverified account
        otp = await _store_otp(str(existing.id), OTP_PURPOSE_SIGNUP)
        try:
            _send_otp_email(existing.email, otp)
        except Exception:
            logger.exception("OTP send failed for %s", existing.email)
            raise HTTPException(status_code=500, detail="Failed to send OTP")

        return "Account already registered. OTP resent to email.", UserResponse(
            user_id=existing.id, email=existing.email
        )

    # Create new user
    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    otp = await _store_otp(str(user.id), OTP_PURPOSE_SIGNUP)
    try:
        _send_otp_email(user.email, otp)
    except Exception:
        logger.exception("OTP send failed for %s", user.email)
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return "Signup successful. OTP sent to email.", UserResponse(
        user_id=user.id, email=user.email
    )


def login(db: Session, email: str, password: str) -> TokenResponse:
    """
    Authenticate a user and return a token pair.

    Raises:
        HTTPException 401: Invalid credentials or unverified account.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please verify your account before logging in.",
        )

    return _issue_tokens(str(user.id), user.email, db)


def rotate_refresh_token(refresh_token: str, db: Session) -> TokenResponse:
    """
    Validate the refresh token, revoke it, and issue a new token pair.

    Raises:
        HTTPException 401: Token invalid or already used (reuse detection).
    """
    payload = decode_token(refresh_token, expected_type="refresh")

    db_tokens = db.query(RefreshToken).filter(RefreshToken.user_id == payload["sub"]).all()
    valid_token = next(
        (t for t in db_tokens if _pwd_context.verify(refresh_token, t.token)), None
    )

    if not valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or has already been used",
        )

    db.delete(valid_token)
    db.commit()

    return _issue_tokens(payload["sub"], payload["email"], db)


# ── OTP flows ─────────────────────────────────────────────────────────────────

async def send_otp(email: EmailStr, purpose: OTPPurpose, db: Session) -> UserResponse:
    """
    Generate and email an OTP for the given purpose.

    Raises:
        HTTPException 404: User not found.
        HTTPException 409: Already verified (signup purpose).
        HTTPException 403: Not verified (login/reset purpose).
        HTTPException 500: Email send failure.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if purpose == OTPPurpose.signup and user.is_verified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already verified")

    if purpose in (OTPPurpose.login, OTPPurpose.reset_password) and not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not verified")

    otp = await _store_otp(str(user.id), purpose.value)
    try:
        _send_otp_email(user.email, otp)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send OTP")

    return UserResponse(user_id=user.id, email=user.email)


async def verify_otp(request: VerifyOTPRequest, purpose: str, db: Session) -> None:
    """
    Verify the submitted OTP and mark the user as verified if purpose is signup.

    Raises:
        HTTPException 404: User not found.
        HTTPException 400: Invalid or expired OTP.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_valid = await _verify_otp(str(user.id), request.otp_code, purpose)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP"
        )

    if not user.is_verified:
        user.is_verified = True
        db.commit()


async def forget_password(email: EmailStr, db: Session) -> UserResponse:
    """
    Send a password-reset OTP to the user's email.

    Raises:
        HTTPException 404: User not found.
        HTTPException 400: Account not verified.
        HTTPException 429: Rate limit exceeded.
        HTTPException 500: Email send failure.
    """
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not verified")

    await _check_otp_rate_limit(str(user.id), OTP_PURPOSE_PASSWORD_RESET)
    otp = await _store_otp(str(user.id), OTP_PURPOSE_PASSWORD_RESET)

    try:
        _send_otp_email(user.email, otp)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")

    return UserResponse(user_id=user.id, email=user.email)


async def reset_password(request: ResetPasswordRequest, db: Session) -> None:
    """
    Verify the OTP and update the user's password.

    Raises:
        HTTPException 404: User not found.
        HTTPException 400: Invalid or expired OTP.
    """
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    is_valid = await _verify_otp(str(user.id), request.otp_code, OTP_PURPOSE_PASSWORD_RESET)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OTP"
        )

    user.hashed_password = hash_password(request.new_password)
    db.commit()
