import base64
from http import HTTPStatus

import pytest
from sqlalchemy import select

from db.models import Task
from tests.factories import TaskFactory
from tests.test_api.base import BaseTestCase

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 32


def data_url(kind: str, data: bytes) -> str:
    return f"data:image/{kind};base64,{base64.b64encode(data).decode()}"


class TestUserMe(BaseTestCase):
    @pytest.mark.asyncio
    async def test_returns_signed_in_account(self) -> None:
        me, headers = await self.create_user_and_get_token()

        data = await self.assert_response_ok(
            await self.client.get("/user/me", headers=headers)
        )

        assert (data["id"], data["email"]) == (me["id"], me["email"])
        assert "hashed_password" not in data
        assert data["avatar"] is None


class TestUserLastLogin(BaseTestCase):
    @pytest.mark.asyncio
    async def test_login_records_last_login(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.get(url="/user/me", headers=headers)

        assert (await self.assert_response_ok(response))["last_login"] is not None


class TestUserUpdate(BaseTestCase):
    url = "/user/me"

    @pytest.mark.asyncio
    async def test_change_and_clear_name(self) -> None:
        _, headers = await self.create_user_and_get_token()

        changed = await self.client.patch(
            url=self.url,
            json={"first_name": "  Alex ", "last_name": "Mieses"},
            headers=headers,
        )
        first_only = await self.client.patch(
            url=self.url, json={"first_name": "Al"}, headers=headers
        )
        cleared = await self.client.patch(
            url=self.url, json={"last_name": ""}, headers=headers
        )

        data = await self.assert_response_ok(changed)
        assert (data["first_name"], data["last_name"]) == ("Alex", "Mieses")
        data = await self.assert_response_ok(first_only)
        assert (data["first_name"], data["last_name"]) == ("Al", "Mieses")
        data = await self.assert_response_ok(cleared)
        assert (data["first_name"], data["last_name"]) == ("Al", None)

    @pytest.mark.asyncio
    async def test_rejects_too_long_name(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.patch(
            url=self.url, json={"first_name": "x" * 101}, headers=headers
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUserPassword(BaseTestCase):
    url = "/user/me/password"

    async def _login(self, email: str, password: str) -> int:
        response = await self.client.post(
            url="/auth/login", json={"email": email, "password": password}
        )
        return response.status_code

    @pytest.mark.asyncio
    async def test_change_password(self) -> None:
        user, headers = await self.create_user_and_get_token(password="old-pass-123")

        response = await self.client.put(
            url=self.url,
            json={"current_password": "old-pass-123", "new_password": "new-pass-456"},
            headers=headers,
        )

        assert response.status_code == HTTPStatus.OK
        assert await self._login(user["email"], "new-pass-456") == HTTPStatus.OK
        assert await self._login(user["email"], "old-pass-123") == (
            HTTPStatus.UNAUTHORIZED
        )

    @pytest.mark.asyncio
    async def test_wrong_current_password(self) -> None:
        user, headers = await self.create_user_and_get_token(password="old-pass-123")

        response = await self.client.put(
            url=self.url,
            json={"current_password": "guess-123", "new_password": "new-pass-456"},
            headers=headers,
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"detail": "Current password is incorrect"}
        assert await self._login(user["email"], "old-pass-123") == HTTPStatus.OK

    @pytest.mark.asyncio
    async def test_rejects_short_new_password(self) -> None:
        _, headers = await self.create_user_and_get_token(password="old-pass-123")

        response = await self.client.put(
            url=self.url,
            json={"current_password": "old-pass-123", "new_password": "short"},
            headers=headers,
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUserDelete(BaseTestCase):
    url = "/user/me"

    @pytest.mark.asyncio
    async def test_delete_account_and_tasks(self) -> None:
        user, headers = await self.create_user_and_get_token(password="pass-1234")
        await TaskFactory.create_async(session=self.session, user_id=user["id"])
        other, _ = await self.create_user_and_get_token()
        await TaskFactory.create_async(session=self.session, user_id=other["id"])

        response = await self.client.request(
            method="DELETE",
            url=self.url,
            json={"password": "pass-1234"},
            headers=headers,
        )
        me = await self.client.get(url=self.url, headers=headers)
        remaining = (await self.session.execute(select(Task.user_id))).scalars().all()

        assert response.status_code == HTTPStatus.ACCEPTED
        assert me.status_code == HTTPStatus.UNAUTHORIZED
        assert remaining == [other["id"]]

    @pytest.mark.asyncio
    async def test_wrong_password_keeps_account(self) -> None:
        _, headers = await self.create_user_and_get_token(password="pass-1234")

        response = await self.client.request(
            method="DELETE", url=self.url, json={"password": "nope"}, headers=headers
        )
        me = await self.client.get(url=self.url, headers=headers)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert me.status_code == HTTPStatus.OK


class TestUserAvatar(BaseTestCase):
    url = "/user/me/avatar"

    @pytest.mark.asyncio
    async def test_set_replace_and_remove(self) -> None:
        _, headers = await self.create_user_and_get_token()

        first = await self.client.put(
            url=self.url, json={"image": data_url("png", PNG)}, headers=headers
        )
        second = await self.client.put(
            url=self.url, json={"image": data_url("jpeg", JPEG)}, headers=headers
        )
        me = await self.client.get(url="/user/me", headers=headers)
        removed = await self.client.delete(url=self.url, headers=headers)

        assert (await self.assert_response_ok(first))["avatar"] == data_url("png", PNG)
        assert (await self.assert_response_ok(second))["avatar"] == data_url(
            "jpeg", JPEG
        )
        assert (await self.assert_response_ok(me))["avatar"] == data_url("jpeg", JPEG)
        assert (await self.assert_response_ok(removed))["avatar"] is None

    @pytest.mark.asyncio
    async def test_requires_login(self) -> None:
        response = await self.client.put(
            url=self.url, json={"image": data_url("png", PNG)}
        )

        assert response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "image",
        [
            pytest.param(data_url("svg+xml", b"<svg onload=alert(1)>"), id="svg"),
            pytest.param(data_url("png", JPEG), id="content-mismatch"),
            pytest.param("data:image/png;base64,not*base64", id="bad-base64"),
            pytest.param("https://example.com/me.png", id="not-data-url"),
            pytest.param(data_url("png", PNG + b"\x00" * 256 * 1024), id="too-large"),
        ],
    )
    async def test_rejects_invalid_images(self, image: str) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.put(
            url=self.url, json={"image": image}, headers=headers
        )
        me = await self.client.get(url="/user/me", headers=headers)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (await self.assert_response_ok(me))["avatar"] is None
