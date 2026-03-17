"""
Application entry point.

Registers middleware, global exception handlers, and all module routers.
Swagger UI is available at /docs — use the Authorize button to set your
Bearer token once and it applies to all protected routes.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.config.database import init_db
from app.modules.auth.router import auth_router, otp_router, password_router
from app.modules.chat.router import router as chat_router
from app.modules.health.router import router as health_router
from app.modules.resume.router import router as resume_router
from app.schemas.response import error_response, validation_response

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the database on startup."""
    init_db()
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Portfolio Chatbot API",
    version="1.0.0",
    description="Backend API for portfolio chatbot — auth, resume parsing, and AI chat.",
    lifespan=lifespan,
)


# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Exception handlers ────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic / FastAPI validation errors (422)."""
    errors = {}
    for err in exc.errors():
        if err["type"] == "json_invalid":
            return error_response(
                message="Invalid JSON body. Please send a valid JSON request.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        field_path = [str(loc) for loc in err["loc"] if loc != "body"]
        field = ".".join(field_path)
        message = err["msg"]

        if "email" in field.lower():
            message = "Invalid email address"
        elif message.startswith("Value error, "):
            message = message.replace("Value error, ", "", 1)

        errors[field] = message

    return validation_response(errors=errors)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle all HTTPExceptions with the unified error envelope."""
    return error_response(message=exc.detail, status_code=exc.status_code)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unhandled exceptions — returns 500."""
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return error_response(
        message="Internal server error. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(password_router)
app.include_router(chat_router)
app.include_router(resume_router)


# ── Custom OpenAPI — adds BearerAuth to Swagger UI ────────────────────────────

def custom_openapi():
    """
    Inject a single BearerAuth security scheme into the OpenAPI schema.

    This adds the Authorize button in Swagger UI so users can enter their
    JWT once and it applies to all protected routes automatically.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema.setdefault("components", {})
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT access token (without the 'Bearer ' prefix).",
        }
    }

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
