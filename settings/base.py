from pathlib import Path

import pydantic_settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class BaseSettings(pydantic_settings.BaseSettings):
    """Reads settings from the environment, falling back to the repo's `.env`."""

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", case_sensitive=False, extra="ignore"
    )
