from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from enums import TaskStatus


def _as_naive_utc(value: datetime | None) -> datetime | None:
    """Offset-aware datetimes become naive UTC, the way timestamps are stored."""
    if value is not None and value.tzinfo is not None:
        value = value.astimezone(UTC).replace(tzinfo=None)
    return value


DueAt = Annotated[datetime | None, AfterValidator(_as_naive_utc)]
Title = Annotated[str, Field(min_length=1, max_length=255, description="Task title")]
Description = Annotated[
    str | None, Field(max_length=1000, description="Optional details")
]


class TaskCreateSchema(BaseModel):
    title: Title
    description: Description = None
    status: TaskStatus = Field(TaskStatus.CREATED, description="Starting status")
    due_at: DueAt = Field(None, description="Deadline; any offset, stored as UTC")


class TaskUpdateSchema(BaseModel):
    """Partial update: omitted fields stay as they are; `due_at: null` clears it."""

    title: Title | None = None
    description: Description = None
    due_at: DueAt = None


class TaskUpdateStatusSchema(BaseModel):
    status: TaskStatus


class TaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
