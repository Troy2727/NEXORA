from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import auth, db, team
from api.schemas import UserResponseSchema
from api.schemas.team import (
    InviteCreateSchema,
    MessageCreateSchema,
    MessageSchema,
    MyInviteSchema,
    TeamNameSchema,
    TeamResponseSchema,
)

router = APIRouter(prefix="/team", tags=["Team"])

CurrentUser = Annotated[UserResponseSchema, Depends(dependency=auth.get_current_user)]
Session = Annotated[AsyncSession, Depends(dependency=db.get_session)]
Usecase = Annotated[team.TeamUsecase, Depends(dependency=team.get_team_usecase)]


async def _team(usecase: team.TeamUsecase, session: AsyncSession, user_id: int):
    found = await usecase.get_team(session=session, user_id=user_id)
    return TeamResponseSchema.model_validate(found) if found else None


@router.get(path="")
async def get_team(
    user: CurrentUser, session: Session, usecase: Usecase
) -> TeamResponseSchema | None:
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.post(path="")
async def create_team(
    data: Annotated[TeamNameSchema, Body(description="Team name")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.create_team(session=session, user_id=user.id, name=data.name)
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.patch(path="")
async def rename_team(
    data: Annotated[TeamNameSchema, Body(description="New team name")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.rename(session=session, user_id=user.id, name=data.name)
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.delete(path="")
async def delete_team(
    user: CurrentUser, session: Session, usecase: Usecase
) -> JSONResponse:
    await usecase.delete_team(session=session, user_id=user.id)
    return JSONResponse(
        content={"message": "Team deleted"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.post(path="/invites")
async def invite(
    data: Annotated[InviteCreateSchema, Body(description="Who to invite")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.invite(
        session=session, user_id=user.id, user_email=user.email, email=str(data.email)
    )
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.get(path="/invites/mine")
async def my_invites(
    user: CurrentUser, session: Session, usecase: Usecase
) -> list[MyInviteSchema]:
    return [
        MyInviteSchema.model_validate(i)
        for i in await usecase.my_invites(session=session, email=user.email)
    ]


@router.delete(path="/invites/{id}")
async def cancel_invite(
    id: Annotated[int, Path(description="Invite ID")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.cancel_invite(session=session, user_id=user.id, invite_id=id)
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.post(path="/invites/{id}/accept")
async def accept_invite(
    id: Annotated[int, Path(description="Invite ID")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.accept_invite(
        session=session, user_id=user.id, email=user.email, invite_id=id
    )
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.post(path="/invites/{id}/decline")
async def decline_invite(
    id: Annotated[int, Path(description="Invite ID")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> JSONResponse:
    await usecase.decline_invite(session=session, email=user.email, invite_id=id)
    return JSONResponse(
        content={"message": "Invite declined"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.delete(path="/members/{user_id}")
async def remove_member(
    user_id: Annotated[int, Path(description="User ID of the member")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TeamResponseSchema | None:
    await usecase.remove_member(
        session=session, user_id=user.id, member_user_id=user_id
    )
    return await _team(usecase=usecase, session=session, user_id=user.id)


@router.post(path="/leave")
async def leave(user: CurrentUser, session: Session, usecase: Usecase) -> JSONResponse:
    await usecase.leave(session=session, user_id=user.id)
    return JSONResponse(
        content={"message": "You left the team"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.get(path="/messages")
async def list_messages(
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
    after_id: Annotated[
        int | None, Query(description="Only messages after this ID")
    ] = None,
    limit: Annotated[int, Query(description="Maximum messages", ge=1, le=200)] = 100,
) -> list[MessageSchema]:
    return [
        MessageSchema.model_validate(m)
        for m in await usecase.list_messages(
            session=session, user_id=user.id, after_id=after_id, limit=limit
        )
    ]


@router.post(path="/messages")
async def post_message(
    data: Annotated[MessageCreateSchema, Body(description="Message")],
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> MessageSchema:
    return MessageSchema.model_validate(
        await usecase.post_message(session=session, user_id=user.id, body=data.body)
    )
