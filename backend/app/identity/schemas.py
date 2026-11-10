from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=256)

    @field_validator("username")
    @classmethod
    def username_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("username must not be blank")
        return value


class SessionCreated(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(min_length=32)
    token_type: Literal["Bearer"]
    expires_at: datetime


class Principal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: UUID
    person_id: UUID
    account_kind: Literal["INTERNAL", "EXTERNAL"]
    client_id: UUID | None
    roles: list[Literal["ADMIN", "ANALYST", "LAWYER", "PREPARER", "COORDINATOR", "EXTERNAL_READER"]]


class Problem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: int = Field(ge=400, le=599)
    detail: str = Field(default="", min_length=0)
    request_id: UUID
    instance: str = Field(default="", min_length=0)
