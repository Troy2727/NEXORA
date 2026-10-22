from enum import StrEnum


class TaskStatus(StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

    @property
    def transitions(self) -> list["TaskStatus"]:
        """Statuses a task in this status may move to next."""
        return list(_NEXT_STATUSES[self])


_NEXT_STATUSES: dict[TaskStatus, tuple[TaskStatus, ...]] = {
    TaskStatus.CREATED: (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED),
    TaskStatus.IN_PROGRESS: (TaskStatus.CREATED, TaskStatus.COMPLETED),
    TaskStatus.COMPLETED: (TaskStatus.CREATED,),
}
