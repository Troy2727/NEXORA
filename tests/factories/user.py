from factory.declarations import LazyFunction, Sequence

from db.models import User
from tests.factories.base import AsyncSQLAlchemyModelFactory, fake


class UserFactory(AsyncSQLAlchemyModelFactory):
    """An active, verified user. Pass `hashed_password` to be able to sign in."""

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        model = User

    email = Sequence(lambda n: f"member{n}@example.com")
    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    hashed_password = None
    is_active = True
