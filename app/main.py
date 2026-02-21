import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.health_check import router as heath_router
from app.api.v1.auth import router as auth_router
from app.api.v1.otp import router as otp_router
from app.api.v1.password import router as password_router
from app.core.db.session import init_db

# from app.api.v1.chat import router as chat_router

app = FastAPI(title="Portfolio Chatbot API")
@app.on_event("startup")
def startup():
    init_db()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.ERROR)

# --------------------------------------------------
# Global Exception Handler
# --------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}

    for err in exc.errors():
        if err["type"] == "json_invalid":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "success": False,
                    "message": "Invalid JSON body. Please send a valid JSON request.",
                },
            )

        field_path = [str(loc) for loc in err["loc"] if loc != "body"]
        field = ".".join(field_path)
        message = err["msg"]

        if "email" in field.lower():
            message = "Invalid email address"
        # ✅ Remove "Value error, " prefix
        elif message.startswith("Value error, "):
            message = message.replace("Value error, ", "", 1)
        errors[field]=message

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Validation failed",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error. Please try again later."},
    )


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"success": False, "message": exc.detail}
    )


app.include_router(heath_router)
app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(password_router)
# app.include_router(chat_router)
