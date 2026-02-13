import logging
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db.base import Base
from app.core.db.session import engine, get_db
from app.api.v1.auth import router as auth_router
from app.api.v1.otp import router as otp_router
from app.api.v1.password import router as password_router
from app.api.v1.chat import router as chat_router
from fastapi import APIRouter

# ------------------------------------------------  --
# App setup
# --------------------------------------------------

app = FastAPI(title="Portfolio Chatbot API")

# --------------------------------------------------
# CORS
# --------------------------------------------------
print("🔥 main.py loaded")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://portfolio-chatbot-omega-one.vercel.app","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Validation Error Handler (IMPORTANT)
# --------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []

    for err in exc.errors():
        # Invalid JSON body
        if err["type"] == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": "Invalid JSON body. Please send a valid JSON request."
                },
            )

        # Field validation errors
        field_path = [str(loc) for loc in err["loc"] if loc != "body"]
        field = ".".join(field_path)
        errors.append(f"{field}: {err['msg']}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": errors},
    )


# --------------------------------------------------
# Global Exception Handler (LAST)
# --------------------------------------------------

logging.basicConfig(level=logging.ERROR)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error. Please try again later."},
    )


# --------------------------------------------------
# Health Check
# --------------------------------------------------

health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get("/", summary="Health Check")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": True}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "fail",
                "db": False,
                "error": str(e),
            },
        )



# --------------------------------------------------
# Routes
# --------------------------------------------------

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(password_router)
app.include_router(chat_router)
