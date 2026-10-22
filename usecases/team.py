from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Message, TeamInvite, TeamMember, User
from db.repositories import (
    MessageRepository,
    TeamInviteRepository,
    TeamMemberRepository,
    TeamRepository,
)
from enums import TeamRole
from exceptions import TeamConflictError, TeamNotFoundError, TeamPermissionError


def _name(user: User) -> str:
    return (
        " ".join(n for n in (user.first_name, user.last_name) if n)
        or user.email.split("@")[0]
    )


class TeamUsecase:
    def __init__(self):
        self._teams = TeamRepository()
        self._members = TeamMemberRepository()
        self._invites = TeamInviteRepository()
        self._messages = MessageRepository()

    async def _membership(self, session: AsyncSession, user_id: int) -> TeamMember:
        member = await self._members.get_by(session=session, user_id=user_id)
        if not member:
            raise TeamNotFoundError

        return member

    async def _ownership(self, session: AsyncSession, user_id: int) -> TeamMember:
        member = await self._membership(session=session, user_id=user_id)
        if member.role != TeamRole.OWNER:
            raise TeamPermissionError

        return member

    async def get_team(self, session: AsyncSession, user_id: int) -> dict | None:
        """Get the user's team with its members (and invites, for the owner).

        Args:
            session: The session.
            user_id: The user ID.

        Returns:
            The team as a dict, or None if the user isn't in a team.

        """
        member = await self._members.get_by(session=session, user_id=user_id)
        if not member:
            return None

        team = await self._teams.get_by(session=session, id=member.team_id)
        if not team:
            raise TeamNotFoundError

        rows = await self._members.list_with_users(session=session, team_id=team.id)
        invites = (
            await self._invites.get_all(session=session, team_id=team.id)
            if member.role == TeamRole.OWNER
            else []
        )
        return {
            "id": team.id,
            "name": team.name,
            "owner_id": team.owner_id,
            "created_at": team.created_at,
            "members": [
                {
                    "user_id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "avatar": user.avatar,
                    "role": m.role,
                    "joined_at": m.created_at,
                }
                for m, user in rows
            ],
            "invites": invites,
        }

    async def create_team(self, session: AsyncSession, user_id: int, name: str) -> None:
        """Create a team with the user as its owner.

        Args:
            session: The session.
            user_id: The user ID.
            name: The team name.

        """
        if await self._members.get_by(session=session, user_id=user_id):
            raise TeamConflictError(message="You're already in a team")

        team = await self._teams.create(
            session=session, data={"name": name, "owner_id": user_id}
        )
        await self._members.create(
            session=session,
            data={"team_id": team.id, "user_id": user_id, "role": TeamRole.OWNER},
        )

    async def rename(self, session: AsyncSession, user_id: int, name: str) -> None:
        """Rename the owner's team.

        Args:
            session: The session.
            user_id: The owner's user ID.
            name: The new name.

        """
        owner = await self._ownership(session=session, user_id=user_id)
        await self._teams.update_by(
            session=session, data={"name": name}, id=owner.team_id
        )

    async def _delete_team(self, session: AsyncSession, team_id: int) -> None:
        # Explicit deletes so this works even where foreign keys aren't enforced.
        await self._messages.delete_all_by(session=session, team_id=team_id)
        await self._invites.delete_all_by(session=session, team_id=team_id)
        await self._members.delete_all_by(session=session, team_id=team_id)
        await self._teams.delete_by(session=session, id=team_id)

    async def delete_team(self, session: AsyncSession, user_id: int) -> None:
        """Delete the owner's team with its members, invites and messages.

        Args:
            session: The session.
            user_id: The owner's user ID.

        """
        owner = await self._ownership(session=session, user_id=user_id)
        await self._delete_team(session=session, team_id=owner.team_id)

    async def invite(
        self, session: AsyncSession, user_id: int, user_email: str, email: str
    ) -> None:
        """Invite an email address to the owner's team.

        Args:
            session: The session.
            user_id: The owner's user ID.
            user_email: The owner's email.
            email: The email to invite.

        """
        owner = await self._ownership(session=session, user_id=user_id)
        email = email.strip().lower()
        if email == user_email.lower():
            raise TeamConflictError(message="You can't invite yourself")

        rows = await self._members.list_with_users(
            session=session, team_id=owner.team_id
        )
        if any(u.email.lower() == email for _, u in rows):
            raise TeamConflictError(message="That person is already in your team")
        if await self._invites.get_by(
            session=session, team_id=owner.team_id, email=email
        ):
            raise TeamConflictError(message="That email has already been invited")

        await self._invites.create(
            session=session,
            data={"team_id": owner.team_id, "email": email, "invited_by": user_id},
        )

    async def cancel_invite(
        self, session: AsyncSession, user_id: int, invite_id: int
    ) -> None:
        """Cancel one of the owner's pending invites.

        Args:
            session: The session.
            user_id: The owner's user ID.
            invite_id: The invite ID.

        """
        owner = await self._ownership(session=session, user_id=user_id)
        if not await self._invites.delete_by(
            session=session, id=invite_id, team_id=owner.team_id
        ):
            raise TeamNotFoundError(message="Invite not found")

    async def my_invites(self, session: AsyncSession, email: str) -> list[dict]:
        """Get invites sent to the user's email.

        Args:
            session: The session.
            email: The user's email.

        Returns:
            The invites with their team and inviter names.

        """
        rows = await self._invites.list_for_email(session=session, email=email.lower())
        return [
            {
                "id": invite.id,
                "team_name": team.name,
                "invited_by": _name(inviter),
                "created_at": invite.created_at,
            }
            for invite, team, inviter in rows
        ]

    async def _invite_for(
        self, session: AsyncSession, email: str, invite_id: int
    ) -> TeamInvite:
        # Only the person an invite was sent to can see or answer it.
        invite = await self._invites.get_by(
            session=session, id=invite_id, email=email.lower()
        )
        if not invite:
            raise TeamNotFoundError(message="Invite not found")

        return invite

    async def accept_invite(
        self, session: AsyncSession, user_id: int, email: str, invite_id: int
    ) -> None:
        """Join the team that invited the user.

        Args:
            session: The session.
            user_id: The invited user's ID.
            email: The invited user's email.
            invite_id: The invite ID.

        """
        invite = await self._invite_for(
            session=session, email=email, invite_id=invite_id
        )
        if await self._members.get_by(session=session, user_id=user_id):
            raise TeamConflictError(message="Leave your current team first")

        await self._members.create(
            session=session,
            data={
                "team_id": invite.team_id,
                "user_id": user_id,
                "role": TeamRole.MEMBER,
            },
        )
        await self._invites.delete_by(session=session, id=invite.id)

    async def decline_invite(
        self, session: AsyncSession, email: str, invite_id: int
    ) -> None:
        """Decline an invite sent to the user.

        Args:
            session: The session.
            email: The invited user's email.
            invite_id: The invite ID.

        """
        invite = await self._invite_for(
            session=session, email=email, invite_id=invite_id
        )
        await self._invites.delete_by(session=session, id=invite.id)

    async def remove_member(
        self, session: AsyncSession, user_id: int, member_user_id: int
    ) -> None:
        """Remove a member from the owner's team.

        Args:
            session: The session.
            user_id: The owner's user ID.
            member_user_id: The user ID of the member to remove.

        """
        owner = await self._ownership(session=session, user_id=user_id)
        if member_user_id == user_id:
            raise TeamConflictError(message="Owners can't remove themselves")
        if not await self._members.delete_by(
            session=session, user_id=member_user_id, team_id=owner.team_id
        ):
            raise TeamNotFoundError(message="Member not found")

    async def leave(self, session: AsyncSession, user_id: int) -> None:
        """Leave the user's team.

        Args:
            session: The session.
            user_id: The user ID.

        """
        member = await self._membership(session=session, user_id=user_id)
        if member.role == TeamRole.OWNER:
            raise TeamConflictError(
                message="Owners can't leave their team. Delete it instead."
            )

        await self._members.delete_by(session=session, id=member.id)

    async def list_messages(
        self, session: AsyncSession, user_id: int, after_id: int | None, limit: int
    ) -> list[Message]:
        """Get messages from the user's team chat.

        Args:
            session: The session.
            user_id: The user ID.
            after_id: Only messages after this ID, if given.
            limit: The maximum number of messages.

        Returns:
            The messages, oldest first.

        """
        member = await self._membership(session=session, user_id=user_id)
        return await self._messages.list_page(
            session=session, team_id=member.team_id, after_id=after_id, limit=limit
        )

    async def post_message(
        self, session: AsyncSession, user_id: int, body: str
    ) -> Message:
        """Post a message to the user's team chat.

        Args:
            session: The session.
            user_id: The user ID.
            body: The message.

        Returns:
            The new message.

        """
        member = await self._membership(session=session, user_id=user_id)
        return await self._messages.create(
            session=session,
            data={"team_id": member.team_id, "user_id": user_id, "body": body},
        )

    async def remove_user(self, session: AsyncSession, user_id: int) -> None:
        """Clean up team data for a user whose account is being deleted.

        Args:
            session: The session.
            user_id: The user ID.

        """
        member = await self._members.get_by(session=session, user_id=user_id)
        if member and member.role == TeamRole.OWNER:
            await self._delete_team(session=session, team_id=member.team_id)
        elif member:
            await self._members.delete_by(session=session, id=member.id)
        await self._messages.detach_author(session=session, user_id=user_id)
        await self._invites.delete_all_by(session=session, invited_by=user_id)
