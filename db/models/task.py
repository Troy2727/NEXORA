from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base
from enums import TaskStatus


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, comment="ID")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, comment="Owner ID"
    )
    title: Mapped[str] = mapped_column(comment="Title")
    description: Mapped[str | None] = mapped_column(comment="Description")
    status: Mapped[TaskStatus] = mapped_column(comment="Status")
    due_at: Mapped[datetime | None] = mapped_column(comment="Due at")
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), comment="Created at"
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), comment="Updated at"
    )
