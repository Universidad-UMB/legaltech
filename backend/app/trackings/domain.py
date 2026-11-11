from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProcessData:
    id: UUID
    radicado: str
    label: str | None


@dataclass(frozen=True, slots=True)
class TrackingData:
    id: UUID
    tracking_code: str
    client_id: UUID
    process_id: UUID
    status: str
    baseline_observation_id: UUID | None
    last_adopted_observation_id: UUID | None
    created_at: datetime
    updated_at: datetime
