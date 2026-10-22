from factory.declarations import LazyFunction

from db.models import Task
from enums import TaskStatus
from tests.factories.base import AsyncSQLAlchemyModelFactory, fake


class TaskFactory(AsyncSQLAlchemyModelFactory):
    """A to-do task. Always pass `user_id`; tasks can't exist without an owner."""

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = Task

    title = LazyFunction(lambda: fake.sentence(nb_words=4).rstrip("."))
    description = LazyFunction(lambda: fake.paragraph(nb_sentences=2))
    status = TaskStatus.CREATED
