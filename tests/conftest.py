from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.dependencies.db import get_session
from db.models import Base
from main import app


@pytest_asyncio.fixture
async def test_session() -> AsyncIterator[AsyncSession]:
    """A fresh in-memory SQLite database with every table, per test."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def test_client(test_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """An HTTP client for the app that shares the test's database session."""
    app.dependency_overrides[get_session] = lambda: test_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://nexora.test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
