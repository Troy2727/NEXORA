from pydantic_settings import SettingsConfigDict

from settings.base import BaseSettings


class RedisSettings(BaseSettings):
    """Redis keeps short-lived email verification codes. Env: `REDIS_*`."""

    model_config = SettingsConfigDict(env_prefix="redis_")

    url: str | None = None  # e.g. Upstash; takes priority over host/port/db
    host: str = "redis"
    port: int = 6379
    db: int = 0


redis_settings = RedisSettings()
