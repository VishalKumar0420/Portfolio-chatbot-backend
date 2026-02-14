from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str | None = None
    REDIS_URL: str | None = None
    SECRET_KEY: str | None = None

    PINECONE_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings()
