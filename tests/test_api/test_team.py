from http import HTTPStatus

import pytest
from sqlalchemy import select

from db.models import Message, Team, TeamMember
from tests.test_api.base import BaseTestCase


class TeamTestCase(BaseTestCase):
    async def create_team(self, name: str = "Core") -> tuple[dict, dict]:
        owner, headers = await self.create_user_and_get_token()
        response = await self.client.post(
            url="/team", json={"name": name}, headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        return owner, headers

    async def add_member(self, owner_headers: dict) -> tuple[dict, dict]:
        """Invite a new user and have them accept."""
        member, headers = await self.create_user_and_get_token()
        await self.client.post(
            url="/team/invites", json={"email": member["email"]}, headers=owner_headers
        )
        invite = (
            await self.client.get(url="/team/invites/mine", headers=headers)
        ).json()[0]
        accepted = await self.client.post(
            url=f"/team/invites/{invite['id']}/accept", headers=headers
        )
        assert accepted.status_code == HTTPStatus.OK
        return member, headers


class TestTeamBasics(TeamTestCase):
    @pytest.mark.asyncio
    async def test_no_team_returns_null(self) -> None:
        _, headers = await self.create_user_and_get_token()

        response = await self.client.get(url="/team", headers=headers)

        assert (await self.assert_response_ok(response)) is None

    @pytest.mark.asyncio
    async def test_create_team_makes_owner(self) -> None:
        owner, headers = await self.create_team(name="  Core  ")

        data = (await self.client.get(url="/team", headers=headers)).json()

        assert data["name"] == "Core"
        assert data["owner_id"] == owner["id"]
        assert [(m["user_id"], m["role"]) for m in data["members"]] == [
            (owner["id"], "owner")
        ]

    @pytest.mark.asyncio
    async def test_cannot_create_second_team(self) -> None:
        _, headers = await self.create_team()

        response = await self.client.post(
            url="/team", json={"name": "Two"}, headers=headers
        )

        assert response.status_code == HTTPStatus.CONFLICT

    @pytest.mark.asyncio
    async def test_rename_owner_only(self) -> None:
        _, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)

        renamed = await self.client.patch(
            url="/team", json={"name": "Platform"}, headers=owner_headers
        )
        denied = await self.client.patch(
            url="/team", json={"name": "Hijack"}, headers=member_headers
        )

        assert (await self.assert_response_ok(renamed))["name"] == "Platform"
        assert denied.status_code == HTTPStatus.FORBIDDEN


class TestTeamInvites(TeamTestCase):
    @pytest.mark.asyncio
    async def test_invite_accept_flow(self) -> None:
        owner, owner_headers = await self.create_team()
        member, member_headers = await self.add_member(owner_headers)

        data = (await self.client.get(url="/team", headers=owner_headers)).json()

        assert {m["user_id"] for m in data["members"]} == {owner["id"], member["id"]}
        assert data["invites"] == []

    @pytest.mark.asyncio
    async def test_invite_is_case_insensitive_and_listed(self) -> None:
        _, owner_headers = await self.create_team()
        invitee, invitee_headers = await self.create_user_and_get_token()

        await self.client.post(
            url="/team/invites",
            json={"email": invitee["email"].upper()},
            headers=owner_headers,
        )
        mine = (
            await self.client.get(url="/team/invites/mine", headers=invitee_headers)
        ).json()

        assert [(i["team_name"]) for i in mine] == ["Core"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("target", ["self", "duplicate", "member"])
    async def test_invite_conflicts(self, target: str) -> None:
        owner, owner_headers = await self.create_team()
        member, _ = await self.add_member(owner_headers)
        email = {
            "self": owner["email"],
            "duplicate": "someone@example.com",
            "member": member["email"],
        }[target]
        if target == "duplicate":
            await self.client.post(
                url="/team/invites", json={"email": email}, headers=owner_headers
            )

        response = await self.client.post(
            url="/team/invites", json={"email": email}, headers=owner_headers
        )

        assert response.status_code == HTTPStatus.CONFLICT

    @pytest.mark.asyncio
    async def test_member_cannot_invite(self) -> None:
        _, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)

        response = await self.client.post(
            url="/team/invites", json={"email": "x@example.com"}, headers=member_headers
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.asyncio
    async def test_invalid_email_rejected(self) -> None:
        _, owner_headers = await self.create_team()

        response = await self.client.post(
            url="/team/invites", json={"email": "not-an-email"}, headers=owner_headers
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_cannot_accept_someone_elses_invite(self) -> None:
        _, owner_headers = await self.create_team()
        invitee, _ = await self.create_user_and_get_token()
        _, stranger_headers = await self.create_user_and_get_token()
        await self.client.post(
            url="/team/invites", json={"email": invitee["email"]}, headers=owner_headers
        )
        invite_id = (await self.client.get(url="/team", headers=owner_headers)).json()[
            "invites"
        ][0]["id"]

        response = await self.client.post(
            url=f"/team/invites/{invite_id}/accept", headers=stranger_headers
        )

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    async def test_accept_while_in_team_conflicts(self) -> None:
        _, owner_headers = await self.create_team()
        other_owner, other_headers = await self.create_team(name="Other")
        await self.client.post(
            url="/team/invites",
            json={"email": other_owner["email"]},
            headers=owner_headers,
        )
        invite = (
            await self.client.get(url="/team/invites/mine", headers=other_headers)
        ).json()[0]

        response = await self.client.post(
            url=f"/team/invites/{invite['id']}/accept", headers=other_headers
        )

        assert response.status_code == HTTPStatus.CONFLICT

    @pytest.mark.asyncio
    async def test_decline_and_cancel(self) -> None:
        _, owner_headers = await self.create_team()
        invitee, invitee_headers = await self.create_user_and_get_token()
        await self.client.post(
            url="/team/invites", json={"email": invitee["email"]}, headers=owner_headers
        )
        await self.client.post(
            url="/team/invites",
            json={"email": "later@example.com"},
            headers=owner_headers,
        )
        mine = (
            await self.client.get(url="/team/invites/mine", headers=invitee_headers)
        ).json()

        declined = await self.client.post(
            url=f"/team/invites/{mine[0]['id']}/decline", headers=invitee_headers
        )
        team = (await self.client.get(url="/team", headers=owner_headers)).json()
        cancelled = await self.client.delete(
            url=f"/team/invites/{team['invites'][0]['id']}", headers=owner_headers
        )

        assert declined.status_code == HTTPStatus.ACCEPTED
        assert [i["email"] for i in team["invites"]] == ["later@example.com"]
        assert (await self.assert_response_ok(cancelled))["invites"] == []


class TestTeamMembership(TeamTestCase):
    @pytest.mark.asyncio
    async def test_owner_removes_member(self) -> None:
        owner, owner_headers = await self.create_team()
        member, member_headers = await self.add_member(owner_headers)

        removed = await self.client.delete(
            url=f"/team/members/{member['id']}", headers=owner_headers
        )
        member_view = await self.client.get(url="/team", headers=member_headers)

        assert [
            m["user_id"] for m in (await self.assert_response_ok(removed))["members"]
        ] == [owner["id"]]
        assert member_view.json() is None

    @pytest.mark.asyncio
    async def test_member_cannot_remove_and_owner_cannot_remove_self(self) -> None:
        owner, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)

        by_member = await self.client.delete(
            url=f"/team/members/{owner['id']}", headers=member_headers
        )
        self_remove = await self.client.delete(
            url=f"/team/members/{owner['id']}", headers=owner_headers
        )

        assert by_member.status_code == HTTPStatus.FORBIDDEN
        assert self_remove.status_code == HTTPStatus.CONFLICT

    @pytest.mark.asyncio
    async def test_member_leaves_owner_cannot(self) -> None:
        _, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)

        left = await self.client.post(url="/team/leave", headers=member_headers)
        owner_leave = await self.client.post(url="/team/leave", headers=owner_headers)

        assert left.status_code == HTTPStatus.ACCEPTED
        assert owner_leave.status_code == HTTPStatus.CONFLICT

    @pytest.mark.asyncio
    async def test_owner_deletes_team(self) -> None:
        _, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)
        await self.client.post(
            url="/team/messages", json={"body": "hi"}, headers=member_headers
        )

        denied = await self.client.delete(url="/team", headers=member_headers)
        deleted = await self.client.delete(url="/team", headers=owner_headers)

        assert denied.status_code == HTTPStatus.FORBIDDEN
        assert deleted.status_code == HTTPStatus.ACCEPTED
        assert (
            await self.client.get(url="/team", headers=member_headers)
        ).json() is None
        assert (await self.session.execute(select(Message))).scalars().all() == []


class TestTeamMessages(TeamTestCase):
    @pytest.mark.asyncio
    async def test_post_and_list(self) -> None:
        owner, owner_headers = await self.create_team()
        member, member_headers = await self.add_member(owner_headers)

        first = await self.client.post(
            url="/team/messages", json={"body": "  Hello team  "}, headers=owner_headers
        )
        await self.client.post(
            url="/team/messages", json={"body": "Hi!"}, headers=member_headers
        )
        listed = await self.client.get(url="/team/messages", headers=member_headers)
        after = await self.client.get(
            url=f"/team/messages?after_id={first.json()['id']}", headers=owner_headers
        )

        assert [(m["user_id"], m["body"]) for m in listed.json()] == [
            (owner["id"], "Hello team"),
            (member["id"], "Hi!"),
        ]
        assert [m["body"] for m in after.json()] == ["Hi!"]

    @pytest.mark.asyncio
    async def test_limit_returns_latest(self) -> None:
        _, headers = await self.create_team()
        for i in range(5):
            await self.client.post(
                url="/team/messages", json={"body": f"m{i}"}, headers=headers
            )

        response = await self.client.get(url="/team/messages?limit=2", headers=headers)

        assert [m["body"] for m in response.json()] == ["m3", "m4"]

    @pytest.mark.asyncio
    async def test_outsiders_cannot_read_or_post(self) -> None:
        _, owner_headers = await self.create_team()
        await self.client.post(
            url="/team/messages", json={"body": "secret"}, headers=owner_headers
        )
        _, other_headers = await self.create_team(name="Other team")
        _, lonely_headers = await self.create_user_and_get_token()

        other_view = await self.client.get(url="/team/messages", headers=other_headers)
        lonely_read = await self.client.get(
            url="/team/messages", headers=lonely_headers
        )
        lonely_post = await self.client.post(
            url="/team/messages", json={"body": "hi"}, headers=lonely_headers
        )

        assert other_view.json() == []
        assert lonely_read.status_code == HTTPStatus.NOT_FOUND
        assert lonely_post.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.asyncio
    @pytest.mark.parametrize("body", ["   ", "x" * 2001])
    async def test_invalid_body_rejected(self, body: str) -> None:
        _, headers = await self.create_team()

        response = await self.client.post(
            url="/team/messages", json={"body": body}, headers=headers
        )

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestTeamAccountDeletion(TeamTestCase):
    @pytest.mark.asyncio
    async def test_deleting_member_keeps_their_messages_anonymised(self) -> None:
        _, owner_headers = await self.create_team()
        member, member_headers = await self.add_member(owner_headers)
        await self.client.post(
            url="/team/messages", json={"body": "bye"}, headers=member_headers
        )

        await self.client.request(
            method="DELETE",
            url="/user/me",
            json={"password": "secure_password123"},
            headers=member_headers,
        )
        messages = (
            await self.client.get(url="/team/messages", headers=owner_headers)
        ).json()
        members = (
            (await self.session.execute(select(TeamMember.user_id))).scalars().all()
        )

        assert [(m["user_id"], m["body"]) for m in messages] == [(None, "bye")]
        assert member["id"] not in members

    @pytest.mark.asyncio
    async def test_deleting_owner_removes_team(self) -> None:
        _, owner_headers = await self.create_team()
        _, member_headers = await self.add_member(owner_headers)

        await self.client.request(
            method="DELETE",
            url="/user/me",
            json={"password": "secure_password123"},
            headers=owner_headers,
        )

        assert (await self.session.execute(select(Team))).scalars().all() == []
        assert (
            await self.client.get(url="/team", headers=member_headers)
        ).json() is None
