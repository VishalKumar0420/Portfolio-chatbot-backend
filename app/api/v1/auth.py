from fastapi import APIRouter
from fastapi import status, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import SignupResponse, UserCreate, UserLogin
from app.services.auth_service import login, rotate_refresh_token, signup
from fastapi import BackgroundTasks


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="signup",
)
async def user_signup(data: UserCreate,db: Session = Depends(get_db)):
    return await signup(db, data)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def user_login(data: UserLogin, db: Session = Depends(get_db)):
    return login(db, data)


@router.post("/refresh",response_model=TokenResponse,operation_id="refresh token",status_code=status.HTTP_201_CREATED)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return rotate_refresh_token(data.refresh_token, db)
