from db.models import Task
from db.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self) -> None:
        super().__init__(model=Task)
