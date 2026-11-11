from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

PublicationText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=10, max_length=10_000)
]
JustificationText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=8, max_length=2_000)
]
PublicationVersionStatus = Literal["DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED", "PUBLISHED"]


class PublicationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tracking_id: UUID
    novelty_ids: list[UUID]
    content_text: PublicationText


class VersionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    novelty_ids: list[UUID]
    content_text: PublicationText


class Publication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    tracking_id: UUID
    client_id: UUID
    current_version_id: UUID | None
    versions: list[UUID]


class PublicationVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    publication_id: UUID
    version_number: int = Field(ge=1)
    recipient_tracking_id: UUID
    recipient_client_id: UUID
    status: PublicationVersionStatus
    content_text: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64, pattern="^[0-9a-f]{64}$")
    frozen_at: datetime | None
    approved_at: datetime | None
    published_at: datetime | None


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: Literal["APPROVE", "REJECT"]
    justification: JustificationText
