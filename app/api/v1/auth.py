from fastapi import APIRouter
from fastapi import status, Depends
from sqlalchemy.orm import Session
from app.core.db.session import get_db
from app.schemas.common import APIResponse,UserData
from app.schemas.token import RefreshTokenRequest, TokenData
from app.schemas.user import UserCreate, UserLogin
from app.services.auth_service import login, rotate_refresh_token, signup


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup",
    response_model=APIResponse[UserData],
    status_code=status.HTTP_201_CREATED,
    operation_id="signup",
)
async def user_signup(data: UserCreate, db: Session = Depends(get_db)):
    return await signup(db=db, data=data)


@router.post("/login", response_model=APIResponse[TokenData], status_code=status.HTTP_200_OK)
def user_login(data: UserLogin, db: Session = Depends(get_db)):
    return login(db=db, data=data)


@router.post(
    "/refresh",
    response_model=APIResponse[TokenData],
    status_code=status.HTTP_201_CREATED,
    operation_id="refresh token",
)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return rotate_refresh_token(data.refresh_token, db=db)
