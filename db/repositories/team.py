from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Message, Team, TeamInvite, TeamMember, User
from db.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    def __init__(self):
        super().__init__(model=Team)


class TeamMemberRepository(BaseRepository[TeamMember]):
    def __init__(self):
        super().__init__(model=TeamMember)

    async def list_with_users(
        self, session: AsyncSession, team_id: int
    ) -> list[tuple[TeamMember, User]]:
        """Get a team's members together with their user accounts, oldest first.

        Args:
            session: The async session.
            team_id: The team ID.

        Returns:
            The (member, user) pairs.

        """
        result = await session.execute(
            statement=select(TeamMember, User)
            .join(User, User.id == TeamMember.user_id)
            .where(TeamMember.team_id == team_id)
            .order_by(TeamMember.created_at, TeamMember.id)
        )
        return [(member, user) for member, user in result.all()]


class TeamInviteRepository(BaseRepository[TeamInvite]):
    def __init__(self):
        super().__init__(model=TeamInvite)

    async def list_for_email(
        self, session: AsyncSession, email: str
    ) -> list[tuple[TeamInvite, Team, User]]:
        """Get invites sent to an email, with their team and inviter.

        Args:
            session: The async session.
            email: The invited email (lowercase).

        Returns:
            The (invite, team, inviter) triples, newest first.

        """
        result = await session.execute(
            statement=select(TeamInvite, Team, User)
            .join(Team, Team.id == TeamInvite.team_id)
            .join(User, User.id == TeamInvite.invited_by)
            .where(TeamInvite.email == email)
            .order_by(TeamInvite.created_at.desc(), TeamInvite.id.desc())
        )
        return [(invite, team, user) for invite, team, user in result.all()]


class MessageRepository(BaseRepository[Message]):
    def __init__(self):
        super().__init__(model=Message)

    async def list_page(
        self, session: AsyncSession, team_id: int, after_id: int | None, limit: int
    ) -> list[Message]:
        """Get a team's messages in order: the newest `limit`, or those after an ID.

        Args:
            session: The async session.
            team_id: The team ID.
            after_id: Only return messages with a greater ID, if given.
            limit: The maximum number of messages.

        Returns:
            The messages, oldest first.

        """
        statement = select(Message).where(Message.team_id == team_id)
        if after_id is not None:
            statement = statement.where(Message.id > after_id).order_by(Message.id)
            result = await session.execute(statement=statement.limit(limit))
            return list(result.scalars().all())

        result = await session.execute(
            statement=statement.order_by(Message.id.desc()).limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def detach_author(self, session: AsyncSession, user_id: int) -> None:
        """Keep a deleted user's messages but remove the link to them.

        Args:
            session: The async session.
            user_id: The user ID.

        """
        await session.execute(
            statement=update(Message)
            .where(Message.user_id == user_id)
            .values(user_id=None)
        )
        await session.commit()
