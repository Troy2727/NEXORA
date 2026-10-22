import base64
import binascii
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

AVATAR_MAX_BYTES = 256 * 1024
AVATAR_PATTERN = re.compile(r"data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/]+={0,2})")


def _content_matches(kind: str, data: bytes) -> bool:
    """Check the image bytes really are the declared type (magic numbers)."""
    if kind == "png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if kind == "jpeg":
        return data.startswith(b"\xff\xd8\xff")
    return data[:4] == b"RIFF" and data[8:12] == b"WEBP"


class UserCreateSchema(BaseModel):
    email: str = Field(description="Sign-in email; stored lowercase")
    password: str = Field(description="Plain password, hashed with bcrypt on save")
    first_name: str | None = None
    last_name: str | None = None


class UserResponseSchema(BaseModel):
    """The public view of an account; never includes the password hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    email: str
    first_name: str | None = None
    last_name: str | None = None
    avatar: str | None = Field(None, description="Profile photo as a data URL")
    is_active: bool = Field(description="False until the email is verified")
    last_login: datetime | None = None
    created_at: datetime


class UserUpdateSchema(BaseModel):
    first_name: str | None = Field(
        default=None, description="First name", max_length=100
    )
    last_name: str | None = Field(default=None, description="Last name", max_length=100)

    @field_validator("first_name", "last_name")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        """Trim names; an empty name clears it."""
        if value is None:
            return None
        return value.strip() or None


class PasswordChangeSchema(BaseModel):
    current_password: str = Field(default=..., description="Current password")
    new_password: str = Field(
        default=..., description="New password", min_length=8, max_length=128
    )


class AccountDeleteSchema(BaseModel):
    password: str = Field(default=..., description="Password, to confirm")


class AvatarSchema(BaseModel):
    image: str = Field(
        default=...,
        description="PNG, JPEG or WebP image as a base64 data URL, 256 KB max",
        max_length=360_000,  # base64 of 256 KB plus the data URL prefix
    )

    @field_validator("image")
    @classmethod
    def check_image(cls, value: str) -> str:
        match = AVATAR_PATTERN.fullmatch(value)
        if not match:
            msg = "Image must be a PNG, JPEG or WebP data URL"
            raise ValueError(msg)
        try:
            data = base64.b64decode(match[2], validate=True)
        except binascii.Error as e:
            msg = "Image is not valid base64"
            raise ValueError(msg) from e
        if len(data) > AVATAR_MAX_BYTES:
            msg = "Image must be 256 KB or smaller"
            raise ValueError(msg)
        if not _content_matches(match[1], data):
            msg = "Image content does not match its type"
            raise ValueError(msg)
        return value
