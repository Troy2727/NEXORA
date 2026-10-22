from http import HTTPStatus

import pytest

from db.models import Task
from enums import TaskStatus
from tests.factories import TaskFactory
from tests.test_api.base import BaseTestCase


class TaskTestCase(BaseTestCase):
    async def _own_task(self, status: TaskStatus = TaskStatus.CREATED):
        """Sign in as a new user who owns one task; returns (task, headers)."""
        user, headers = await self.create_user_and_get_token()
        task = await TaskFactory.create_async(
            session=self.session, user_id=user["id"], status=status
        )
        return task, headers


class TestTaskCrud(TaskTestCase):
    @pytest.mark.asyncio
    async def test_create(self) -> None:
        _, headers = await self.create_user_and_get_token()
        body = {"title": "Write release notes", "description": "For v1.2"}

        response = await self.client.post("/task", json=body, headers=headers)

        data = await self.assert_response_ok(response)
        assert data["id"] > 0
        assert (data["title"], data["description"]) == (
            body["title"],
            body["description"],
        )
        assert data["status"] == TaskStatus.CREATED
        assert data["created_at"]
        assert data["updated_at"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("title", ["", "x" * 256])
    async def test_create_rejects_bad_title(self, title: str) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.post(
            "/task", json={"title": title}, headers=headers
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_requires_sign_in(self) -> None:
        response = await self.client.get("/task/list")

        assert response.status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}

    @pytest.mark.asyncio
    async def test_list(self) -> None:
        user, headers = await self.create_user_and_get_token()
        created = [
            await TaskFactory.create_async(session=self.session, user_id=user["id"])
            for _ in range(3)
        ]

        response = await self.client.get("/task/list", headers=headers)

        data = await self.assert_response_ok(response)
        assert sorted(t["id"] for t in data) == sorted(t.id for t in created)

    @pytest.mark.asyncio
    async def test_get_one(self) -> None:
        task, headers = await self._own_task()

        response = await self.client.get(f"/task/{task.id}", headers=headers)

        data = await self.assert_response_ok(response)
        assert data["id"] == task.id
        assert data["title"] == task.title
        assert data["description"] == task.description

    @pytest.mark.asyncio
    async def test_get_missing_is_not_found(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.get("/task/9999", headers=headers)

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert response.json() == {"detail": "Task not found"}

    @pytest.mark.asyncio
    async def test_partial_update_keeps_other_fields(self) -> None:
        task, headers = await self._own_task()

        response = await self.client.patch(
            f"/task/{task.id}", json={"title": "Renamed"}, headers=headers
        )

        data = await self.assert_response_ok(response)
        assert data["title"] == "Renamed"
        assert data["description"] == task.description

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        task, headers = await self._own_task()

        response = await self.client.delete(f"/task/{task.id}", headers=headers)

        await self.assert_response_no_content(response)
        assert response.json() == {"message": "Task success delete"}
        assert await self.session.get(Task, task.id) is None


class TestTaskStatus(TaskTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("current", "allowed"),
        [
            (TaskStatus.CREATED, [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]),
            (TaskStatus.IN_PROGRESS, [TaskStatus.CREATED, TaskStatus.COMPLETED]),
            (TaskStatus.COMPLETED, [TaskStatus.CREATED]),
        ],
    )
    async def test_transitions(
        self, current: TaskStatus, allowed: list[TaskStatus]
    ) -> None:
        task, headers = await self._own_task(status=current)

        response = await self.client.get(
            f"/task/transitions/{task.id}", headers=headers
        )

        assert await self.assert_response_ok(response) == allowed

    @pytest.mark.asyncio
    async def test_move_to_allowed_status(self) -> None:
        task, headers = await self._own_task()

        response = await self.client.patch(
            f"/task/transitions/{task.id}/{TaskStatus.IN_PROGRESS}", headers=headers
        )

        data = await self.assert_response_ok(response)
        assert data["status"] == TaskStatus.IN_PROGRESS
        assert data["title"] == task.title

    @pytest.mark.asyncio
    async def test_disallowed_move_rejected(self) -> None:
        task, headers = await self._own_task(status=TaskStatus.COMPLETED)

        response = await self.client.patch(
            f"/task/transitions/{task.id}/{TaskStatus.IN_PROGRESS}", headers=headers
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        await self.session.refresh(task)
        assert task.status == TaskStatus.COMPLETED


class TestTaskDueAt(BaseTestCase):
    @pytest.mark.asyncio
    async def test_create_without_due_at(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.post(
            url="/task", json={"title": "No deadline"}, headers=headers
        )

        data = await self.assert_response_ok(response=response)
        assert data["due_at"] is None

    @pytest.mark.asyncio
    async def test_create_normalizes_to_utc(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.post(
            url="/task",
            json={"title": "Deadline", "due_at": "2026-10-20T14:30:00+02:00"},
            headers=headers,
        )

        data = await self.assert_response_ok(response=response)
        assert data["due_at"] == "2026-10-20T12:30:00"

    @pytest.mark.asyncio
    async def test_update_sets_and_clears_due_at(self) -> None:
        user, headers = await self.create_user_and_get_token()
        task = await TaskFactory.create_async(session=self.session, user_id=user["id"])
        url = f"/task/{task.id}"

        set_response = await self.client.patch(
            url=url, json={"due_at": "2026-11-01T09:00:00Z"}, headers=headers
        )
        title_response = await self.client.patch(
            url=url, json={"title": "Renamed"}, headers=headers
        )
        clear_response = await self.client.patch(
            url=url, json={"due_at": None}, headers=headers
        )

        assert (await self.assert_response_ok(set_response))["due_at"] == (
            "2026-11-01T09:00:00"
        )
        assert (await self.assert_response_ok(title_response))["due_at"] == (
            "2026-11-01T09:00:00"
        )
        assert (await self.assert_response_ok(clear_response))["due_at"] is None


class TestTaskOwnership(BaseTestCase):
    """A user must never see or change another user's tasks."""

    async def _other_users_task(self):
        owner, _ = await self.create_user_and_get_token()
        task = await TaskFactory.create_async(
            session=self.session, status=TaskStatus.CREATED, user_id=owner["id"]
        )
        _, intruder_headers = await self.create_user_and_get_token()
        return task, intruder_headers

    @pytest.mark.asyncio
    async def test_create_assigns_owner(self) -> None:
        _, owner_headers = await self.create_user_and_get_token()
        _, other_headers = await self.create_user_and_get_token()

        await self.client.post(
            url="/task", json={"title": "Mine"}, headers=owner_headers
        )

        owner_list = await self.client.get(url="/task/list", headers=owner_headers)
        other_list = await self.client.get(url="/task/list", headers=other_headers)
        assert [t["title"] for t in owner_list.json()] == ["Mine"]
        assert other_list.json() == []

    @pytest.mark.asyncio
    async def test_list_only_own(self) -> None:
        owner, _ = await self.create_user_and_get_token()
        viewer, headers = await self.create_user_and_get_token()
        await TaskFactory.create_async(session=self.session, user_id=owner["id"])
        own = await TaskFactory.create_async(session=self.session, user_id=viewer["id"])

        response = await self.client.get(url="/task/list", headers=headers)

        data = await self.assert_response_ok(response=response)
        assert [t["id"] for t in data] == [own.id]

    @pytest.mark.asyncio
    async def test_get_other_users_task_not_found(self) -> None:
        task, headers = await self._other_users_task()

        response = await self.client.get(url=f"/task/{task.id}", headers=headers)

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_other_users_task_not_found(self) -> None:
        task, headers = await self._other_users_task()

        response = await self.client.patch(
            url=f"/task/{task.id}", json={"title": "Hacked"}, headers=headers
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        await self.session.refresh(task)
        assert task.title != "Hacked"

    @pytest.mark.asyncio
    async def test_transitions_other_users_task_not_found(self) -> None:
        task, headers = await self._other_users_task()

        response = await self.client.get(
            url=f"/task/transitions/{task.id}", headers=headers
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_status_other_users_task_not_found(self) -> None:
        task, headers = await self._other_users_task()

        response = await self.client.patch(
            url=f"/task/transitions/{task.id}/{TaskStatus.COMPLETED}",
            headers=headers,
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        await self.session.refresh(task)
        assert task.status == TaskStatus.CREATED

    @pytest.mark.asyncio
    async def test_delete_other_users_task_keeps_it(self) -> None:
        task, headers = await self._other_users_task()

        response = await self.client.delete(url=f"/task/{task.id}", headers=headers)

        assert response.json() == {"message": "Task fail delete"}
        assert await self.session.get(Task, task.id) is not None
