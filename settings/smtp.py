from pydantic_settings import SettingsConfigDict

from settings.base import BaseSettings


class SMTPSettings(BaseSettings):
    """Outgoing mail. Defaults point at the development MailCatcher container."""

    model_config = SettingsConfigDict(env_prefix="smtp_")

    host: str = "mailcatcher"
    port: int = 1025
    ssl: bool = False
    username: str = "noreply@example.com"
    password: str = ""


smtp_settings = SMTPSettings()
