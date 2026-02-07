from fastapi import APIRouter, HTTPException
from fastapi import status, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import login, rotate_refresh_token, signup

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", operation_id="signup")
def user_signup(data: UserCreate, db: Session = Depends(get_db)):
    return signup(db, data)


@router.post("/login", response_model=TokenResponse)
def user_login(data: UserLogin, db: Session = Depends(get_db)):
    return login(db, data)


@router.post("/refresh")
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    access_token, new_refresh_token = rotate_refresh_token(refresh_token, db)

    return {"access_token": access_token, "refresh_token": new_refresh_token}
