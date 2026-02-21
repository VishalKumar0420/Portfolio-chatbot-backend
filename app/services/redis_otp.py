import random
from app.core.config.setting import get_settings
from app.core.config.redis import get_redis_client
from app.services.otp_rate_limit import check_otp_rate_limit


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


async def store_otp(user_id: str, purpose: str) -> str:
    settings = get_settings()

    if not settings.REDIS_URL:
        raise RuntimeError("REDIS_URL is not set")

    redis_client = get_redis_client()
    otp_ttl = (settings.OTP_EXPIRE_MINUTES or 5) * 60

    key = f"otp:{purpose}:{user_id}"
    otp = generate_otp()

    # store OTP in Redis with TTL
    await redis_client.set(key, otp, ex=otp_ttl)

    # Increment OTP request count for rate-limiting
    await check_otp_rate_limit(user_id, purpose)

    return otp


async def verify_otp(user_id: str, otp_code: str, purpose: str) -> bool:
    key = f"otp:{purpose}:{user_id}"
    stored_otp = await redis_client.get(key)

    if not stored_otp:
        return False

    if isinstance(stored_otp, bytes):
        stored_otp = stored_otp.decode()

    if stored_otp != otp_code:
        return False

    await redis_client.delete(key)
    return True
