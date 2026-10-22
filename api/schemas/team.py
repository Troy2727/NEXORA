from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from enums import TeamRole


def _strip(value: str) -> str:
    return value.strip()


class TeamNameSchema(BaseModel):
    name: str = Field(default=..., description="Team name", min_length=1, max_length=60)

    strip_name = field_validator("name", mode="before")(_strip)


class InviteCreateSchema(BaseModel):
    email: EmailStr = Field(default=..., description="Email to invite")


class MemberSchema(BaseModel):
    user_id: int = Field(default=..., description="User ID")
    first_name: str | None = Field(default=None, description="First name")
    last_name: str | None = Field(default=None, description="Last name")
    email: str = Field(default=..., description="Email")
    avatar: str | None = Field(default=None, description="Profile photo data URL")
    role: TeamRole = Field(default=..., description="Role")
    joined_at: datetime = Field(default=..., description="Joined at")


class InviteSchema(BaseModel):
    id: int = Field(default=..., description="Invite ID")
    email: str = Field(default=..., description="Invited email")
    created_at: datetime = Field(default=..., description="Sent at")

    class Config:
        from_attributes = True


class TeamResponseSchema(BaseModel):
    id: int = Field(default=..., description="Team ID")
    name: str = Field(default=..., description="Team name")
    owner_id: int = Field(default=..., description="Owner's user ID")
    created_at: datetime = Field(default=..., description="Created at")
    members: list[MemberSchema] = Field(default=..., description="Members")
    invites: list[InviteSchema] = Field(
        default=..., description="Pending invites (owner only; empty for members)"
    )


class MyInviteSchema(BaseModel):
    id: int = Field(default=..., description="Invite ID")
    team_name: str = Field(default=..., description="Team name")
    invited_by: str = Field(default=..., description="Inviter's name")
    created_at: datetime = Field(default=..., description="Sent at")


class MessageCreateSchema(BaseModel):
    body: str = Field(default=..., description="Message", min_length=1, max_length=2000)

    strip_body = field_validator("body", mode="before")(_strip)


class MessageSchema(BaseModel):
    id: int = Field(default=..., description="Message ID")
    user_id: int | None = Field(
        default=None, description="Sender's user ID (null if the account was deleted)"
    )
    body: str = Field(default=..., description="Message")
    created_at: datetime = Field(default=..., description="Sent at")

    class Config:
        from_attributes = True
