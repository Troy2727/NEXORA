from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import auth, db, user
from api.schemas import (
    AccountDeleteSchema,
    AvatarSchema,
    PasswordChangeSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

router = APIRouter(prefix="/user", tags=["User"])


@router.get(path="/me", summary="The signed-in account")
async def get_me(
    me: Annotated[UserResponseSchema, Depends(auth.get_current_user)],
) -> UserResponseSchema:
    return me


@router.patch(path="/me")
async def update_me(
    data: Annotated[UserUpdateSchema, Body(description="Name fields to change")],
    current_user: Annotated[
        UserResponseSchema, Depends(dependency=auth.get_current_user)
    ],
    session: Annotated[AsyncSession, Depends(dependency=db.get_session)],
    usecase: Annotated[user.UserUsecase, Depends(dependency=user.get_user_usecase)],
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(
        await usecase.update_profile(
            session=session,
            user_id=current_user.id,
            data=data.model_dump(exclude_unset=True),
        )
    )


@router.put(path="/me/password")
async def change_password(
    data: Annotated[PasswordChangeSchema, Body(description="Current and new password")],
    current_user: Annotated[
        UserResponseSchema, Depends(dependency=auth.get_current_user)
    ],
    session: Annotated[AsyncSession, Depends(dependency=db.get_session)],
    usecase: Annotated[user.UserUsecase, Depends(dependency=user.get_user_usecase)],
) -> JSONResponse:
    await usecase.change_password(
        session=session,
        user_id=current_user.id,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return JSONResponse(
        content={"message": "Password changed"}, status_code=status.HTTP_200_OK
    )


@router.delete(path="/me")
async def delete_me(
    data: Annotated[AccountDeleteSchema, Body(description="Password, to confirm")],
    current_user: Annotated[
        UserResponseSchema, Depends(dependency=auth.get_current_user)
    ],
    session: Annotated[AsyncSession, Depends(dependency=db.get_session)],
    usecase: Annotated[user.UserUsecase, Depends(dependency=user.get_user_usecase)],
) -> JSONResponse:
    await usecase.delete_account(
        session=session, user_id=current_user.id, password=data.password
    )
    return JSONResponse(
        content={"message": "Account deleted"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.put(path="/me/avatar")
async def set_avatar(
    data: Annotated[AvatarSchema, Body(description="Profile photo")],
    current_user: Annotated[
        UserResponseSchema, Depends(dependency=auth.get_current_user)
    ],
    session: Annotated[AsyncSession, Depends(dependency=db.get_session)],
    usecase: Annotated[user.UserUsecase, Depends(dependency=user.get_user_usecase)],
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(
        await usecase.set_avatar(
            session=session, user_id=current_user.id, avatar=data.image
        )
    )


@router.delete(path="/me/avatar")
async def delete_avatar(
    current_user: Annotated[
        UserResponseSchema, Depends(dependency=auth.get_current_user)
    ],
    session: Annotated[AsyncSession, Depends(dependency=db.get_session)],
    usecase: Annotated[user.UserUsecase, Depends(dependency=user.get_user_usecase)],
) -> UserResponseSchema:
    return UserResponseSchema.model_validate(
        await usecase.set_avatar(session=session, user_id=current_user.id, avatar=None)
    )
