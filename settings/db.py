from pydantic import AliasChoices, Field
from pydantic_settings import SettingsConfigDict

from settings.base import BaseSettings


class DbSettings(BaseSettings):
    """PostgreSQL connection. Each field takes our `DB_*` variable first, then the
    PG* variable that Vercel's Neon integration sets."""

    model_config = SettingsConfigDict(env_prefix="db_")

    host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("db_host", "pghost_unpooled", "pghost"),
    )
    port: int = 5432
    login: str = Field(
        default="postgres", validation_alias=AliasChoices("db_login", "pguser")
    )
    password: str = Field(
        default="postgres", validation_alias=AliasChoices("db_password", "pgpassword")
    )
    name: str = Field(
        default="auth", validation_alias=AliasChoices("db_name", "pgdatabase")
    )

    @property
    def url(self) -> str:
        """Async SQLAlchemy URL for PostgreSQL."""
        credentials = f"{self.login}:{self.password}"
        return f"postgresql+asyncpg://{credentials}@{self.host}:{self.port}/{self.name}"


db_settings = DbSettings()
