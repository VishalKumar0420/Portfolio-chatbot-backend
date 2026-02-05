from datetime import datetime, timedelta, timezone
import os
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import user
from app.models.refresh_token import RefreshToken
from app.models.user import User, RoleEnum
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin
from passlib.context import CryptContext
from app.core.config.setting import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# signup

def signup(db: Session, data:UserCreate):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User Already Exist"
        )
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=RoleEnum.user,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login(db:Session,data:UserLogin):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token, refresh_token = issue_tokens(str(user.id), user.email, db)

    return TokenResponse(
        access_token=access_token, 
        refresh_token=refresh_token,
        token_type="bearer"
    )



def issue_tokens(user_id: str, email: str, db: Session):
    payload = {"sub": user_id, "email": email}

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    token_hash = pwd_context.hash(refresh_token)

    db_token = RefreshToken(
        user_id=user_id,
        token=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )
    db.add(db_token)
    db.commit()

    return access_token, refresh_token

def rotate_refresh_token(refresh_token: str, db: Session):
    payload = decode_token(refresh_token, "refresh")

    db_tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == payload["sub"]
    ).all()

    valid_token = None
    for t in db_tokens:
        if pwd_context.verify(refresh_token, t.token):
            valid_token = t
            break

    if not valid_token:
        raise Exception("Refresh token reuse detected")

    db.delete(valid_token)
    db.commit()

    return issue_tokens(payload["sub"], payload["email"], db)