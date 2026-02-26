from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config.exceptions import register_exception_handlers
from app.core.db.session import init_db
from app.api.router import api_router
from app.core.config.logging_config import setup_logging

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Portfolio Chatbot API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  exception handlers
register_exception_handlers(app)

#  API routes
app.include_router(api_router)

