from fastapi import APIRouter
from app.api.v1.health_check import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.otp import router as otp_router
from app.api.v1.password import router as password_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(otp_router)
api_router.include_router(password_router)
