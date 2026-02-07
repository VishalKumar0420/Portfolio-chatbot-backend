import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.db.base import Base
from app.core.db.session import engine
from app.api.v1.auth import router as auth_router
from app.api.v1.otp import router as otp_router
from app.api.v1.password import router as password_router
from app.api.v1.chat import router as chat_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Portfolio Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://portfolio-chatbot-omega-one.vercel.app/",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err["loc"][-1]
        message = err["msg"]
        errors.append(f"{field}: {message}")

    return JSONResponse(
        status_code=422,
        content={"message": errors}
    )
logging.basicConfig(level=logging.ERROR)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}", exc_info=True)

    # Send clean message to frontend
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error. Please try again later."
        }
    )


#Routes

app.include_router(auth_router) 
app.include_router(otp_router)
app.include_router(password_router)
app.include_router(chat_router)


