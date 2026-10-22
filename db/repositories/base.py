from typing import Any, Generic, TypeVar

from sqlalchemy import Select, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """CRUD for one model. Filters are column=value keyword arguments, and every
    write commits immediately."""

    def __init__(self, model: type[ModelT]):
        self.model = model

    def _query(self, **filters: Any) -> Select[tuple[ModelT]]:
        return select(self.model).filter_by(**filters)

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> ModelT:
        """Insert a row and return it with server defaults loaded."""
        row = self.model(**data)
        session.add(row)
        await session.commit()
        await session.refresh(row)
        return row

    async def get_by(self, session: AsyncSession, **filters: Any) -> ModelT | None:
        """The single matching row, or None."""
        return (await session.scalars(self._query(**filters))).one_or_none()

    async def get_all(self, session: AsyncSession, **filters: Any) -> list[ModelT]:
        """Every matching row."""
        return list(await session.scalars(self._query(**filters)))

    async def update_by(
        self, session: AsyncSession, data: dict[str, Any], **filters: Any
    ) -> ModelT | None:
        """Apply `data` to the matching row; None when nothing matches."""
        row = await self.get_by(session, **filters)
        if row is None:
            return None
        for field, value in data.items():
            setattr(row, field, value)
        await session.commit()
        await session.refresh(row)
        return row

    async def delete_by(self, session: AsyncSession, **filters: Any) -> bool:
        """Delete the matching row. Returns whether one existed."""
        row = await self.get_by(session, **filters)
        if row is None:
            return False
        await session.delete(row)
        await session.commit()
        return True

    async def delete_all_by(self, session: AsyncSession, **filters: Any) -> None:
        """Bulk-delete every matching row in one statement."""
        await session.execute(delete(self.model).filter_by(**filters))
        await session.commit()
