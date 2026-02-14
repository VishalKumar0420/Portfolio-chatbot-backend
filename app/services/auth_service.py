from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config.constants import OTP_PURPOSE_LOGIN
from app.models.user import User
from app.core.config.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import user
from app.models.refresh_token import RefreshToken
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin
from passlib.context import CryptContext
from app.core.config.setting import get_settings
from app.services.redis_otp import store_otp
# from app.services.mail_service import send_otp_email
from fastapi import BackgroundTasks

settings = get_settings()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


# async def signup(
#     db: Session,
#     data: UserCreate,
#     background_tasks: BackgroundTasks,
#     purpose: str = OTP_PURPOSE_LOGIN,
# ):

#     existing_user = db.query(User).filter(User.email == data.email).first()

#     if existing_user:
#         if existing_user.is_verified:
#             # Verified user → block signup
#             raise HTTPException(
#                 status_code=409,
#                 detail="User already exists and is verified",
#         )
#     else:
#         # Unverified user → resend OTP
#         otp_code = await store_otp(str(existing_user.id), purpose)
#         # try:
#         #     await send_otp_email(existing_user.email, otp_code)
#         # except Exception as e:
#         #     # Log error properly in production
#         #     raise HTTPException(
#         #         status_code=500,
#         #         detail="Failed to send OTP email",
#         #     )
#         background_tasks.add_task(
#             send_otp_email,
#             existing_user.email,
#             otp_code,
#         )
#         return {
#             "message": "User already exists but not verified. OTP resent.",
#             "user_id": existing_user.id,
#             "email": existing_user.email,
#         }

# # User does not exist → create new
# new_user = User(
#     full_name=data.full_name,
#     email=data.email,
#     hashed_password=hash_password(data.password),
# )
# db.add(new_user)
# db.commit()
# db.refresh(new_user)

# # Generate OTP in Redis
# otp_code = await store_otp(str(new_user.id), purpose)
# background_tasks.add_task(
#     send_otp_email,
#     existing_user.email,
#     otp_code,
# )

# return {
#     "message": "Signup successful. OTP sent to email.",
#     "user_id": new_user.id,
#     "email": new_user.email,
# }


async def signup(
    db: Session,
    data: UserCreate,
    background_tasks: BackgroundTasks,
    purpose: str = OTP_PURPOSE_LOGIN,
):
    # ------------------------------------
    # 1️⃣ Check if user already exists
    # ------------------------------------
    existing_user = db.query(User).filter(User.email == data.email).first()

    # if existing_user:
    #     if existing_user.is_verified:
    #         # Verified user → block signup
    #         raise HTTPException(
    #             status_code=409,
    #             detail="User already exists and is verified",
    #         )
    #     else:
    #         # Unverified user → resend OTP
    #         otp_code = await store_otp(str(existing_user.id), purpose)
    #         try:
    #             send_otp_email(existing_user.email, otp_code)
    #         except Exception as e:
    #             # Log error properly in production
    #             raise HTTPException(
    #                 status_code=500,
    #                 detail="Failed to send OTP email",
    #             )
    #         return {
    #             "message": "User already exists but not verified. OTP resent.",
    #             "user_id": existing_user.id,
    #             "email": existing_user.email,
    #         }

    # CASE 2: User exists but NOT verified → resend OTP
    if existing_user and not existing_user.is_verified:
        otp_code = await store_otp(str(existing_user.id), purpose)

        # background_tasks.add_task(
        #     send_otp_email,
        #     existing_user.email,
        #     otp_code,
        # )

        return {
            "message": "User already exists but not verified. OTP resent.",
            "user_id": existing_user.id,
            "email": existing_user.email,
        }

    # ------------------------------------
    # 3️⃣ User does NOT exist → create new
    # ------------------------------------
    new_user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate OTP in Redis
    otp_code = await store_otp(str(new_user.id), purpose)
    # try:
    #     background_tasks.add_task(
    #         send_otp_email,
    #         new_user.email,
    #         otp_code,
    #     )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500,
    #         detail="Failed to send OTP email",
    #     )

    return {
        "message": "Signup successful. OTP sent to email.",
        "user_id": new_user.id,
        "email": new_user.email,
    }


def login(db: Session, data: UserLogin):

    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified. Please verify before login.",
        )

    access_token, refresh_token = issue_tokens(str(user.id), user.email, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


def issue_tokens(user_id: str, email: str, db: Session):

    payload = {"sub": user_id, "email": email}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    token_hash = pwd_context.hash(refresh_token)

    # Save refresh token in DB
    db_token = RefreshToken(
        user_id=user_id,
        token=token_hash,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(db_token)
    db.commit()

    return access_token, refresh_token


def rotate_refresh_token(refresh_token: str, db: Session):

    payload = decode_token(refresh_token, "refresh")

    # Retrieve all refresh tokens for the user
    db_tokens = (
        db.query(RefreshToken).filter(RefreshToken.user_id == payload["sub"]).all()
    )

    valid_token = None
    for t in db_tokens:
        if pwd_context.verify(refresh_token, t.token):
            valid_token = t
            break

    if not valid_token:
        # Potential token reuse detected
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected",
        )

    # Delete the used refresh token
    db.delete(valid_token)
    db.commit()

    return issue_tokens(payload["sub"], payload["email"], db)
