"""Alembic runner. The database URL always comes from `settings.db_settings`, so
migrations use the same `DB_*` / Neon variables as the API."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from db.models import Base
from settings import db_settings

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)

URL = db_settings.url
METADATA = Base.metadata


def _migrate(connection: Connection) -> None:
    context.configure(
        connection=connection, target_metadata=METADATA, compare_type=True
    )
    with context.begin_transaction():
        context.run_migrations()


async def _migrate_online() -> None:
    engine = create_async_engine(URL)
    async with engine.connect() as connection:
        await connection.run_sync(_migrate)
    await engine.dispose()


def _migrate_offline() -> None:
    """`alembic upgrade --sql`: print the SQL instead of running it."""
    context.configure(
        url=URL,
        target_metadata=METADATA,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    _migrate_offline()
else:
    asyncio.run(_migrate_online())
