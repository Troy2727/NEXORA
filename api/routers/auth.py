from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_auth_usecase
from api.dependencies.db import get_session
from api.schemas import LoginSchema, TokenSchema, UserCreateSchema, UserResponseSchema
from settings import auth_settings
from usecases import AuthUsecase

router = APIRouter(prefix="/auth", tags=["Auth"])

Session = Annotated[AsyncSession, Depends(get_session)]
Usecase = Annotated[AuthUsecase, Depends(get_auth_usecase)]


def _accepted(message: str) -> JSONResponse:
    return JSONResponse({"message": message}, status_code=status.HTTP_202_ACCEPTED)


@router.post("/register", summary="Create an account (inactive until verified)")
async def register(
    body: UserCreateSchema, session: Session, usecase: Usecase
) -> UserResponseSchema:
    user = await usecase.register(session, **body.model_dump(exclude_none=True))
    return UserResponseSchema.model_validate(user)


@router.post("/send/{email}/code", summary="Email a 6-digit verification code")
async def send_email_code(
    email: str, session: Session, usecase: Usecase
) -> JSONResponse:
    await usecase.send_email_code(session, email)
    return _accepted("Email code sent successfully")


@router.post("/verify/{email}/{code}", summary="Activate the account")
async def verify_email(
    email: str, code: str, session: Session, usecase: Usecase
) -> JSONResponse:
    await usecase.verify_email(email=email, code=code, session=session)
    return _accepted("Email verified successfully")


@router.post("/login", summary="Sign in and get a JWT")
async def login(body: LoginSchema, session: Session, usecase: Usecase) -> TokenSchema:
    token = await usecase.login(session, body.email or "", body.password)
    return TokenSchema(access_token=token, token_type=auth_settings.token_type)
