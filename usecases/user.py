from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.repositories import TaskRepository, UserRepository
from exceptions import AuthCredentialsError, AuthError
from usecases.team import TeamUsecase
from utils.crypto import pwd_context


class UserUsecase:
    def __init__(self):
        self._user_repository = UserRepository()
        self._task_repository = TaskRepository()
        self._team_usecase = TeamUsecase()

    async def _update(self, session: AsyncSession, user_id: int, data: dict) -> User:
        user = await self._user_repository.update_by(
            session=session, data=data, id=user_id
        )
        if not user:
            raise AuthCredentialsError

        return user

    async def _check_password(
        self, session: AsyncSession, user_id: int, password: str, message: str
    ) -> None:
        user = await self._user_repository.get_by(session=session, id=user_id)
        if not user:
            raise AuthCredentialsError
        if not user.hashed_password or not pwd_context.verify(
            secret=password, hash=user.hashed_password
        ):
            raise AuthError(message=message, status_code=HTTPStatus.BAD_REQUEST)

    async def set_avatar(
        self, session: AsyncSession, user_id: int, avatar: str | None
    ) -> User:
        """Set or remove the user's profile photo.

        Args:
            session: The session.
            user_id: The user ID.
            avatar: The image as a data URL, or None to remove it.

        Returns:
            The updated user.

        """
        return await self._update(
            session=session, user_id=user_id, data={"avatar": avatar}
        )

    async def update_profile(
        self, session: AsyncSession, user_id: int, data: dict
    ) -> User:
        """Update the user's name.

        Args:
            session: The session.
            user_id: The user ID.
            data: The fields to change (first_name, last_name).

        Returns:
            The updated user.

        """
        return await self._update(session=session, user_id=user_id, data=data)

    async def change_password(
        self,
        session: AsyncSession,
        user_id: int,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change the user's password after checking the current one.

        Args:
            session: The session.
            user_id: The user ID.
            current_password: The current password.
            new_password: The new password.

        """
        await self._check_password(
            session=session,
            user_id=user_id,
            password=current_password,
            message="Current password is incorrect",
        )
        await self._update(
            session=session,
            user_id=user_id,
            data={"hashed_password": pwd_context.hash(secret=new_password)},
        )

    async def delete_account(
        self, session: AsyncSession, user_id: int, password: str
    ) -> None:
        """Delete the user and all their tasks after checking the password.

        Args:
            session: The session.
            user_id: The user ID.
            password: The user's password.

        """
        await self._check_password(
            session=session,
            user_id=user_id,
            password=password,
            message="Password is incorrect",
        )
        await self._team_usecase.remove_user(session=session, user_id=user_id)
        await self._task_repository.delete_all_by(session=session, user_id=user_id)
        await self._user_repository.delete_by(session=session, id=user_id)
