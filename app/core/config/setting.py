from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENV: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 5
    BREVO_API_KEY: Optional[str] = None
    FROM_EMAIL: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
