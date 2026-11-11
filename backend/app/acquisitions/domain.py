from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from uuid import UUID

FixtureCode = Literal["OBS_001", "OBS_002", "FAILED", "INCOMPLETE"]
AcquisitionStatus = Literal["SUCCESS", "INCOMPLETE", "FAILED"]
ObservationQuality = Literal["COMPARABLE", "INCOMPLETE", "INDETERMINATE"]


@dataclass(frozen=True, slots=True)
class FixtureAction:
    action_key: str
    description: str
    occurred_on: date | None


@dataclass(frozen=True, slots=True)
class AcquisitionFixture:
    fixture_code: FixtureCode
    process_alias: str
    process_radicado: str
    status: AcquisitionStatus
    error_code: str | None
    coverage_note: str | None
    observed_at: datetime | None
    quality: ObservationQuality | None
    actions: tuple[FixtureAction, ...]
    payload_sha256: str


@dataclass(frozen=True, slots=True)
class AcquisitionData:
    id: UUID
    process_id: UUID
    source_code: Literal["DEMO-FIXTURE"]
    status: Literal["PENDING", "SUCCESS", "INCOMPLETE", "FAILED"]
    request_key: str
    observation_id: UUID | None
    error_code: str | None
    coverage_note: str | None


@dataclass(frozen=True, slots=True)
class AcquisitionCreateResult:
    acquisition: AcquisitionData
    created: bool


@dataclass(frozen=True, slots=True)
class ObservedActionData:
    action_key: str
    description: str
    occurred_on: date | None


@dataclass(frozen=True, slots=True)
class ObservationData:
    id: UUID
    process_id: UUID
    quality: ObservationQuality
    sealed: bool
    observed_at: datetime
    actions: tuple[ObservedActionData, ...]
    coverage_note: str | None
