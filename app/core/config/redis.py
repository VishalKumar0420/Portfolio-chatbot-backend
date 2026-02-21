import redis.asyncio as redis
from typing import Optional
from app.core.config.setting import get_settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    global _redis_client

    if _redis_client is None:
        settings = get_settings()

        if not settings.REDIS_URL:
            raise RuntimeError("REDIS_URL is not set")

        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

    return _redis_client
