import redis.asyncio as redis
from app.core.config.setting import get_settings

settings = get_settings()

redis_client: redis.Redis = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)
