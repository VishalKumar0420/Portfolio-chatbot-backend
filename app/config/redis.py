"""
Redis client factory — returns a singleton async Redis connection.
"""

from typing import Optional

import redis.asyncio as redis

from app.config.settings import get_settings

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Return the shared async Redis client, creating it on first call.

    Raises:
        RuntimeError: If REDIS_URL is not configured.
    """
    global _redis_client

    if _redis_client is None:
        settings = get_settings()

        if not settings.REDIS_URL:
            raise RuntimeError("REDIS_URL is not configured")

        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

    return _redis_client
