from typing import Any

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

fake = Faker()


class AsyncSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    """factory_boy only knows sync sessions, so build the object and save it
    through the async session ourselves."""

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        abstract = True

    @classmethod
    async def create_async(cls, session: AsyncSession, **overrides: Any) -> Any:
        row = cls.build(**overrides)
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row
