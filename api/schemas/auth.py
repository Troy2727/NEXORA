from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    email: str | None = Field(None, description="Account email (case-insensitive)")
    password: str = Field(description="Account password")


class TokenSchema(BaseModel):
    access_token: str = Field(description="JWT to send as `Authorization: Bearer ...`")
    token_type: str = Field(description='Always "Bearer"')
