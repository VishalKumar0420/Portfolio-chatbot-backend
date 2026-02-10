import random
from app.core.config.redis import redis_client  # should be redis.asyncio.Redis
from app.core.config.setting import settings
from app.services.otp_rate_limit import check_otp_rate_limit
from sqlalchemy.orm import Session
OTP_TTL_SECONDS = settings.OTP_EXPIRE_MINUTES * 60  # configurable TTL


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


async def store_otp(user_id: str, purpose: str) -> str:

    key = f"otp:{purpose}:{user_id}"
    otp = generate_otp()

    # store OTP in Redis with TTL
    await redis_client.set(key, otp, ex=OTP_TTL_SECONDS)

    # Increment OTP request count for rate-limiting
    await check_otp_rate_limit(user_id, purpose)

    return otp


async def verify_otp(user_id: str,otp_code: str, purpose: str) -> bool:
    key = f"otp:{purpose}:{user_id}"
    stored_otp = await redis_client.get(key)

    if not stored_otp:
        return False

    # Redis returns bytes in some clients, decode if needed
    if isinstance(stored_otp, bytes):
        stored_otp = stored_otp.decode()

    if stored_otp != otp_code:
        return False

    # Delete after successful verification
    await redis_client.delete(key)
    return True




