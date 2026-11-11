from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_code: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=180)

    @field_validator("client_code", "name")
    @classmethod
    def value_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("value must not be blank")
        return value.strip()


class Client(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    client_code: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: Literal["ACTIVE", "SUSPENDED"]
