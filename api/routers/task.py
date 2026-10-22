from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user, verify_credentials
from api.dependencies.db import get_session
from api.dependencies.task import get_task_usecase
from api.schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    UserResponseSchema,
)
from enums import TaskStatus
from usecases import TaskUsecase

# Every route needs a valid token, and every query is scoped to the caller's own
# tasks: another user's task ID returns 404, as if it didn't exist.
router = APIRouter(
    prefix="/task", tags=["Task"], dependencies=[Depends(verify_credentials)]
)

CurrentUser = Annotated[UserResponseSchema, Depends(get_current_user)]
Session = Annotated[AsyncSession, Depends(get_session)]
Usecase = Annotated[TaskUsecase, Depends(get_task_usecase)]


@router.post("", summary="Create a task")
async def create(
    body: TaskCreateSchema, user: CurrentUser, session: Session, usecase: Usecase
) -> TaskResponseSchema:
    data = body.model_dump(exclude_none=True) | {"user_id": user.id}
    return TaskResponseSchema.model_validate(await usecase.create(session, data))


@router.get("/list", summary="Your tasks")
async def get_list(
    user: CurrentUser, session: Session, usecase: Usecase
) -> list[TaskResponseSchema]:
    tasks = await usecase.get_all(session, user_id=user.id)
    return [TaskResponseSchema.model_validate(task) for task in tasks]


@router.get("/{id}", summary="One of your tasks")
async def get_by_id(
    id: int, user: CurrentUser, session: Session, usecase: Usecase
) -> TaskResponseSchema:
    task = await usecase.get_by(session, id=id, user_id=user.id)
    return TaskResponseSchema.model_validate(task)


@router.patch("/{id}", summary="Edit a task (send due_at: null to clear it)")
async def update_by_id(
    id: int,
    body: TaskUpdateSchema,
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TaskResponseSchema:
    changes = body.model_dump(exclude_none=True)
    if "due_at" in body.model_fields_set:
        changes["due_at"] = body.due_at  # keep an explicit null
    task = await usecase.update_by(session, changes, id=id, user_id=user.id)
    return TaskResponseSchema.model_validate(task)


@router.delete("/{id}", summary="Delete a task")
async def delete_by_id(
    id: int, user: CurrentUser, session: Session, usecase: Usecase
) -> JSONResponse:
    deleted = await usecase.delete_by(session, id=id, user_id=user.id)
    outcome = "success" if deleted else "fail"
    return JSONResponse(
        {"message": f"Task {outcome} delete"}, status_code=status.HTTP_202_ACCEPTED
    )


@router.get("/transitions/{id}", summary="Statuses this task can move to")
async def get_transitions(
    id: int, user: CurrentUser, session: Session, usecase: Usecase
) -> list[TaskStatus]:
    return await usecase.get_transitions(session, id=id, user_id=user.id)


@router.patch("/transitions/{id}/{status}", summary="Move a task to a new status")
async def update_status(
    id: int,
    status: TaskStatus,
    user: CurrentUser,
    session: Session,
    usecase: Usecase,
) -> TaskResponseSchema:
    task = await usecase.update_status(session, id=id, user_id=user.id, status=status)
    return TaskResponseSchema.model_validate(task)
