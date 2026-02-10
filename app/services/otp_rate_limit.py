from app.core.config.redis import redis_client
from fastapi import HTTPException,status

MAX_OTP_PER_HOUR = 10
RATE_LIMIT_WINDOW = 60 * 60  # seconds


async def check_otp_rate_limit(user_id: str, purpose: str):
    key = f"otp_count:{purpose}:{user_id}"
    count = await redis_client.incr(key)

    if count == 1:
        # first request, set expiry for window
        await redis_client.expire(key, RATE_LIMIT_WINDOW)

    if count > MAX_OTP_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please try again later.",
        )

