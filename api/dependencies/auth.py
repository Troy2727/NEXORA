from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.db import get_session
from api.schemas import UserResponseSchema
from usecases import AuthUsecase

bearer_scheme = HTTPBearer()
Credentials = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


def get_auth_usecase() -> AuthUsecase:
    return AuthUsecase()


def verify_credentials(credentials: Credentials) -> None:
    """Router-level guard: reject requests without a valid, unexpired JWT."""
    AuthUsecase().verify_token(credentials.credentials)


async def get_current_user(
    credentials: Credentials,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponseSchema:
    """The signed-in user behind the request's Bearer token."""
    user = await AuthUsecase().get_current(session, credentials.credentials)
    return UserResponseSchema.model_validate(user)
