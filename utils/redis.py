from redis.asyncio import Redis

from settings import auth_settings, redis_settings


def _connect() -> Redis:
    if redis_settings.url:
        return Redis.from_url(redis_settings.url, decode_responses=True)
    return Redis(
        host=redis_settings.host,
        port=redis_settings.port,
        db=redis_settings.db,
        decode_responses=True,
    )


redis_client = _connect()


async def set_verify_code(identifier: str, code: str) -> None:
    """Store a verification code that expires after `AUTH_VERIFY_CODE_TTL` seconds."""
    await redis_client.setex(identifier, auth_settings.verify_code_ttl, code)


async def get_verify_code(identifier: str) -> str | None:
    """The pending verification code, or None once it has expired."""
    return await redis_client.get(identifier)
