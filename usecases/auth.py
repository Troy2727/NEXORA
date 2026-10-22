import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.repositories import UserRepository
from exceptions import (
    AuthCredentialsError,
    EmailTakenError,
    InvalidCodeError,
    UserAlreadyActiveError,
    UserNotFoundError,
)
from settings import auth_settings
from utils.crypto import pwd_context
from utils.email import send_email
from utils.redis import get_verify_code, set_verify_code

VERIFICATION_EMAIL = """\
<html><body>
<p>Your NEXORA verification code:</p>
<h2 style="letter-spacing: 4px">{code}</h2>
<p>It expires in {minutes} minute(s).
If you didn't sign up, you can ignore this email.</p>
</body></html>"""


def normalize_email(email: str | None) -> str:
    """Emails are matched case-insensitively and without surrounding spaces."""
    return (email or "").strip().lower()


class AuthUsecase:
    """Sign-up, email verification, sign-in and JWT checks."""

    def __init__(self) -> None:
        self._users = UserRepository()

    # Tokens

    def verify_token(self, token: str) -> dict[str, Any]:
        """Decode a JWT; AuthCredentialsError (401) if it's invalid or expired."""
        try:
            return jwt.decode(
                token, auth_settings.secret_key, algorithms=[auth_settings.algorithm]
            )
        except JWTError as error:
            raise AuthCredentialsError from error

    @staticmethod
    def _issue_token(subject: str) -> str:
        expires = datetime.now(UTC) + timedelta(
            minutes=auth_settings.access_token_expire_minutes
        )
        return jwt.encode(
            {"sub": subject, "exp": expires},
            auth_settings.secret_key,
            algorithm=auth_settings.algorithm,
        )

    async def get_current(self, session: AsyncSession, token: str) -> User:
        """The active user the token was issued to."""
        email = self.verify_token(token).get("sub")
        user = await self._users.get_by(session, email=email) if email else None
        if user is None or not user.is_active:
            raise AuthCredentialsError
        return user

    # Sign-in and sign-up

    async def login(self, session: AsyncSession, email: str, password: str) -> str:
        """Check the password, record the sign-in time and return a fresh JWT.

        Unknown emails, wrong passwords and unverified accounts all get the same
        401, so the response doesn't reveal which accounts exist.
        """
        user = await self._users.get_by(session, email=normalize_email(email))
        if (
            user is None
            or not user.is_active
            or not user.hashed_password
            or not pwd_context.verify(password, user.hashed_password)
        ):
            raise AuthCredentialsError

        now = datetime.now(UTC).replace(tzinfo=None)  # timestamps are naive UTC
        await self._users.update_by(session, {"last_login": now}, id=user.id)
        return self._issue_token(user.email)

    async def register(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Create an inactive account; it activates once the email is verified."""
        email = normalize_email(email)
        if await self._users.get_by(session, email=email):
            raise EmailTakenError

        return await self._users.create(
            session,
            {
                "email": email,
                "hashed_password": pwd_context.hash(password),
                "first_name": first_name,
                "last_name": last_name,
                "is_active": False,
            },
        )

    # Email verification

    @staticmethod
    def _generate_code() -> str:
        """A random six-digit code (100000-999999)."""
        return f"{secrets.randbelow(900_000) + 100_000}"

    async def _pending_user(self, session: AsyncSession, email: str) -> User:
        """The account waiting for verification under this email."""
        user = await self._users.get_by(session, email=normalize_email(email))
        if user is None:
            raise UserNotFoundError
        if user.is_active:
            raise UserAlreadyActiveError
        return user

    async def send_email_code(self, session: AsyncSession, email: str) -> None:
        """Email a new verification code, replacing any earlier one."""
        user = await self._pending_user(session, email)
        code = self._generate_code()
        await set_verify_code(identifier=user.email, code=code)

        minutes = max(1, auth_settings.verify_code_ttl // 60)
        send_email(
            email=user.email,
            subject="Your verification code",
            html_content=VERIFICATION_EMAIL.format(code=code, minutes=minutes),
        )

    async def verify_email(self, email: str, code: str, session: AsyncSession) -> None:
        """Activate the account if `code` matches the one we emailed."""
        user = await self._pending_user(session, email)
        if await get_verify_code(identifier=user.email) != code:
            raise InvalidCodeError
        await self._users.update_by(session, {"is_active": True}, id=user.id)
