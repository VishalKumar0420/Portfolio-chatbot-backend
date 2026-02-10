import redis.asyncio as redis
from app.core.config.setting import settings

redis_client: redis.Redis = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)