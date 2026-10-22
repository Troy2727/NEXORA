from pydantic_settings import SettingsConfigDict

from settings.base import BaseSettings


class AuthSettings(BaseSettings):
    """JWT signing and email verification. Env vars start with `AUTH_`."""

    model_config = SettingsConfigDict(env_prefix="auth_")

    secret_key: str = "secret"  # noqa: S105 - dev default, overridden in every deploy
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    token_type: str = "Bearer"  # noqa: S105 - the OAuth scheme name, not a secret
    verify_code_ttl: int = 60  # seconds


auth_settings = AuthSettings()
