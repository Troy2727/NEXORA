from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Task
from db.repositories import TaskRepository
from enums import TaskStatus
from exceptions import TaskNotAvailableTransitionError, TaskNotFoundError


class TaskUsecase:
    """Task rules. Callers always filter by `user_id`, so a task that belongs to
    someone else behaves exactly like one that doesn't exist."""

    def __init__(self) -> None:
        self._tasks = TaskRepository()

    async def create(self, session: AsyncSession, data: dict[str, Any]) -> Task:
        return await self._tasks.create(session=session, data=data)

    async def get_all(self, session: AsyncSession, **filters: Any) -> list[Task]:
        return await self._tasks.get_all(session, **filters)

    async def get_by(self, session: AsyncSession, **filters: Any) -> Task:
        """The matching task; raises TaskNotFoundError (404) when there is none."""
        task = await self._tasks.get_by(session, **filters)
        if task is None:
            raise TaskNotFoundError
        return task

    async def update_by(
        self, session: AsyncSession, data: dict[str, Any], **filters: Any
    ) -> Task:
        task = await self._tasks.update_by(session, data, **filters)
        if task is None:
            raise TaskNotFoundError
        return task

    async def delete_by(self, session: AsyncSession, **filters: Any) -> bool:
        return await self._tasks.delete_by(session, **filters)

    async def get_transitions(
        self, session: AsyncSession, id: int, user_id: int
    ) -> list[TaskStatus]:
        """Statuses the user's task may move to from where it is now."""
        task = await self.get_by(session, id=id, user_id=user_id)
        return task.status.transitions

    async def update_status(
        self,
        session: AsyncSession,
        id: int,
        user_id: int,
        status: TaskStatus,
    ) -> Task:
        """Move the task to `status`, rejecting moves the lifecycle doesn't allow."""
        task = await self.get_by(session, id=id, user_id=user_id)
        if status not in task.status.transitions:
            raise TaskNotAvailableTransitionError
        return await self.update_by(session, {"status": status}, id=id, user_id=user_id)
