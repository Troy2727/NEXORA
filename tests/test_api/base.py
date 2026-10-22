from collections.abc import Iterator
from http import HTTPStatus
from typing import Any
from unittest import mock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from settings import auth_settings
from tests.factories import UserFactory
from utils.crypto import pwd_context

DEFAULT_PASSWORD = "secure_password123"


class FakeRedis:
    """Just enough of the Redis client for verification codes, kept in a dict."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def setex(self, name: str, _ttl: int, value: str) -> None:
        self.values[name] = value

    async def get(self, name: str) -> str | None:
        return self.values.get(name)


def unique_email(prefix: str = "user") -> str:
    return f"{prefix}-{uuid4().hex[:10]}@example.com"


class BaseTestCase:
    """API test base: an HTTP client on a fresh database, with Redis faked and
    outgoing mail captured instead of sent."""

    session: AsyncSession
    client: AsyncClient
    redis: FakeRedis
    smtp: mock.MagicMock

    @pytest_asyncio.fixture(autouse=True)
    async def _wire(self, test_session: AsyncSession, test_client: AsyncClient):
        self.session = test_session
        self.client = test_client

    @pytest.fixture(autouse=True)
    def _fake_services(self) -> Iterator[None]:
        self.redis = FakeRedis()
        with (
            mock.patch("utils.redis.redis_client", self.redis),
            mock.patch("smtplib.SMTP") as smtp,
        ):
            self.smtp = smtp
            yield

    @property
    def sent_emails(self) -> list[Any]:
        """Messages handed to the fake SMTP server, oldest first."""
        server = self.smtp.return_value.__enter__.return_value
        return [call.args[0] for call in server.send_message.call_args_list]

    async def assert_response_ok(self, response: Response) -> Any:
        assert response.status_code == HTTPStatus.OK, response.text
        return response.json()

    async def assert_response_no_content(self, response: Response) -> None:
        assert response.status_code in {
            HTTPStatus.CREATED,
            HTTPStatus.ACCEPTED,
            HTTPStatus.NO_CONTENT,
        }, response.text

    async def create_user_and_get_token(
        self, email: str | None = None, password: str = DEFAULT_PASSWORD
    ) -> tuple[dict[str, Any], dict[str, str]]:
        """Create an active user, sign in, and return (user fields, auth headers)."""
        email = email or unique_email()
        user = await UserFactory.create_async(
            session=self.session,
            email=email,
            hashed_password=pwd_context.hash(password),
        )
        login = await self.client.post(
            "/auth/login", json={"email": email, "password": password}
        )
        token = login.json()["access_token"]
        return vars(user), {"Authorization": f"{auth_settings.token_type} {token}"}
