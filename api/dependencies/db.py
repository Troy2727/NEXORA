from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import async_session


async def get_session() -> AsyncIterator[AsyncSession]:
    """One database session per request, closed when the response is sent."""
    async with async_session() as session:
        yield session
