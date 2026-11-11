import hashlib
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, cast
from uuid import UUID

PublicationStatus = Literal["DRAFT", "PENDING_APPROVAL", "APPROVED", "REJECTED", "PUBLISHED"]


@dataclass(frozen=True, slots=True)
class PublicationData:
    id: UUID
    tracking_id: UUID
    client_id: UUID
    current_version_id: UUID | None
    version_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class PublicationVersionData:
    id: UUID
    publication_id: UUID
    version_number: int
    recipient_tracking_id: UUID
    recipient_client_id: UUID
    status: PublicationStatus
    content_text: str
    content_sha256: str
    frozen_at: datetime | None
    approved_at: datetime | None
    published_at: datetime | None


def content_sha256(content_text: str) -> str:
    return hashlib.sha256(content_text.encode("utf-8")).hexdigest()


def publication_status(value: str) -> PublicationStatus:
    return cast(PublicationStatus, value)
