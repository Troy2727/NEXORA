from api.schemas.auth import LoginSchema, TokenSchema
from api.schemas.task import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    TaskUpdateStatusSchema,
)
from api.schemas.user import (
    AccountDeleteSchema,
    AvatarSchema,
    PasswordChangeSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
)

__all__ = (
    "AccountDeleteSchema",
    "AvatarSchema",
    "LoginSchema",
    "PasswordChangeSchema",
    "TaskCreateSchema",
    "TaskResponseSchema",
    "TaskUpdateSchema",
    "TaskUpdateStatusSchema",
    "TokenSchema",
    "UserCreateSchema",
    "UserResponseSchema",
    "UserUpdateSchema",
)
