from http import HTTPStatus

import pytest
from sqlalchemy import select

from db.models import User
from settings import auth_settings
from tests.factories import UserFactory
from tests.test_api.base import DEFAULT_PASSWORD, BaseTestCase, unique_email
from utils.crypto import pwd_context

pytestmark = pytest.mark.asyncio


class TestRegister(BaseTestCase):
    async def _register(self, **overrides: str):
        body = {
            "email": unique_email("ada"),
            "password": DEFAULT_PASSWORD,
            "first_name": "Ada",
            "last_name": "Lovelace",
        } | overrides
        return body, await self.client.post("/auth/register", json=body)

    async def test_creates_inactive_account(self) -> None:
        body, response = await self._register()

        data = await self.assert_response_ok(response)
        assert data["id"] > 0
        assert data["email"] == body["email"]
        assert (data["first_name"], data["last_name"]) == ("Ada", "Lovelace")
        assert data["is_active"] is False
        assert data["created_at"]

    async def test_never_returns_password(self) -> None:
        _, response = await self._register()

        data = await self.assert_response_ok(response)
        assert not {"password", "hashed_password"} & data.keys()

    async def test_stores_password_hashed(self) -> None:
        _, response = await self._register()

        user = await self.session.get(User, response.json()["id"])
        assert user is not None
        assert user.hashed_password != DEFAULT_PASSWORD
        assert pwd_context.verify(DEFAULT_PASSWORD, user.hashed_password)

    async def test_email_is_stored_lowercase(self) -> None:
        email = unique_email("grace")

        _, response = await self._register(email=f"  {email.upper()} ")

        assert (await self.assert_response_ok(response))["email"] == email

    async def test_duplicate_email_rejected(self) -> None:
        email = unique_email()
        await self._register(email=email)

        _, response = await self._register(email=email.upper())

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": "Email already registered"}


class TestLogin(BaseTestCase):
    async def _user(self, *, active: bool = True) -> str:
        email = unique_email()
        await UserFactory.create_async(
            session=self.session,
            email=email,
            hashed_password=pwd_context.hash(DEFAULT_PASSWORD),
            is_active=active,
        )
        return email

    async def _login(self, email: str, password: str = DEFAULT_PASSWORD):
        return await self.client.post(
            "/auth/login", json={"email": email, "password": password}
        )

    async def test_returns_bearer_token(self) -> None:
        email = await self._user()

        data = await self.assert_response_ok(await self._login(email))

        assert data["token_type"] == auth_settings.token_type
        me = await self.client.get(
            "/user/me", headers={"Authorization": f"Bearer {data['access_token']}"}
        )
        assert (await self.assert_response_ok(me))["email"] == email

    async def test_email_ignores_case_and_spaces(self) -> None:
        email = await self._user()

        response = await self._login(f" {email.capitalize()} ")

        assert "access_token" in await self.assert_response_ok(response)

    @pytest.mark.parametrize(
        ("case", "password"),
        [("wrong password", "not-the-password"), ("unknown email", DEFAULT_PASSWORD)],
    )
    async def test_bad_credentials_unauthorized(self, case: str, password: str) -> None:
        email = await self._user()
        if case == "unknown email":
            email = unique_email("nobody")

        response = await self._login(email, password)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_unverified_account_cannot_sign_in(self) -> None:
        email = await self._user(active=False)

        response = await self._login(email)

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_protected_route_rejects_bad_token(self) -> None:
        response = await self.client.get(
            "/task/list", headers={"Authorization": "Bearer not-a-jwt"}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestEmailVerification(BaseTestCase):
    async def _pending_user(self) -> str:
        email = unique_email("new")
        await UserFactory.create_async(
            session=self.session, email=email, is_active=False
        )
        return email

    async def test_send_code_emails_six_digits(self) -> None:
        email = await self._pending_user()

        response = await self.client.post(f"/auth/send/{email}/code")

        await self.assert_response_no_content(response)
        code = self.redis.values[email]
        assert code.isdigit()
        assert len(code) == 6
        [message] = self.sent_emails
        assert message["To"] == email
        assert code in message.get_content()

    async def test_correct_code_activates_account(self) -> None:
        email = await self._pending_user()
        await self.client.post(f"/auth/send/{email}/code")

        response = await self.client.post(
            f"/auth/verify/{email}/{self.redis.values[email]}"
        )

        await self.assert_response_no_content(response)
        user = await self.session.scalar(select(User).filter_by(email=email))
        assert user is not None
        await self.session.refresh(user)
        assert user.is_active is True

    async def test_wrong_code_rejected(self) -> None:
        email = await self._pending_user()
        await self.client.post(f"/auth/send/{email}/code")

        response = await self.client.post(f"/auth/verify/{email}/000000")

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": "Invalid code"}

    async def test_unknown_email_not_found(self) -> None:
        response = await self.client.post(f"/auth/send/{unique_email()}/code")

        assert response.status_code == HTTPStatus.NOT_FOUND

    async def test_active_account_needs_no_code(self) -> None:
        user, _ = await self.create_user_and_get_token()

        response = await self.client.post(f"/auth/send/{user['email']}/code")

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert self.sent_emails == []
