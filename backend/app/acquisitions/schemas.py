from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.acquisitions.domain import FixtureCode
from app.trackings.schemas import Tracking


class AcquisitionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    process_id: UUID
    fixture_code: FixtureCode
    request_key: str = Field(min_length=8, max_length=100)


class Acquisition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    process_id: UUID
    source_code: Literal["DEMO-FIXTURE"]
    status: Literal["PENDING", "SUCCESS", "INCOMPLETE", "FAILED"]
    request_key: str = Field(min_length=1)
    observation_id: UUID | None
    error_code: str | None = Field(min_length=1)
    coverage_note: str | None = Field(min_length=0)


class ObservedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_key: str = Field(min_length=1)
    description: str = Field(min_length=1)
    occurred_on: date | None


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    process_id: UUID
    quality: Literal["COMPARABLE", "INCOMPLETE", "INDETERMINATE"]
    sealed: bool
    observed_at: datetime
    actions: list[ObservedAction]
    coverage_note: str | None = Field(min_length=0)


class AdoptObservationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: UUID


class AdoptionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tracking: Tracking
    outcome: Literal["BASELINE_SET", "ADVANCED", "ALREADY_ADOPTED"]
