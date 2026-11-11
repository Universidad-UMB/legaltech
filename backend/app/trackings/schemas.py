from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProcessCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    radicado: str = Field(min_length=23, max_length=23, pattern=r"^[0-9]{23}$")
    label: str | None = Field(default=None, min_length=1, max_length=180)

    @field_validator("label")
    @classmethod
    def label_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("label must not be blank")
        return value.strip() if value is not None else None


class Process(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    radicado: str = Field(min_length=23, max_length=23, pattern=r"^[0-9]{23}$")
    label: str | None


class TrackingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: UUID
    process_id: UUID


class Tracking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    tracking_code: str = Field(min_length=1)
    client_id: UUID
    process_id: UUID
    status: Literal["PENDING", "ACTIVE", "FINISHED"]
    baseline_observation_id: UUID | None
    last_adopted_observation_id: UUID | None
