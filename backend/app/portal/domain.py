import base64
import binascii
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

PortalCoverageStatus = Literal["COMPARABLE", "INCOMPLETE", "FAILED", "NOT_OBSERVED"]


@dataclass(frozen=True, slots=True)
class PortalTrackingData:
    id: UUID
    tracking_code: str
    radicado: str
    has_publication: bool
    coverage_status: PortalCoverageStatus


@dataclass(frozen=True, slots=True)
class PortalTrackingPageData:
    items: tuple[PortalTrackingData, ...]
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class PortalPublicationData:
    version_id: UUID
    published_at: datetime
    content_text: str


@dataclass(frozen=True, slots=True)
class PortalPublicationResultData:
    available: bool
    coverage_status: PortalCoverageStatus
    publication: PortalPublicationData | None


def encode_portal_cursor(tracking_id: UUID) -> str:
    payload = str(tracking_id).encode("ascii")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_portal_cursor(cursor: str) -> UUID:
    try:
        encoded = cursor.encode("ascii")
        padded = encoded + b"=" * (-len(encoded) % 4)
        decoded = base64.b64decode(padded, altchars=b"-_", validate=True).decode("ascii")
        tracking_id = UUID(decoded)
        if encode_portal_cursor(tracking_id) != cursor:
            raise ValueError("Cursor is not canonical.")
    except (UnicodeEncodeError, UnicodeDecodeError, binascii.Error, ValueError) as exc:
        raise ValueError("The portal cursor is invalid.") from exc
    return tracking_id


def portal_coverage_status(
    run_status: str | None, observation_quality: str | None
) -> PortalCoverageStatus:
    if run_status == "FAILED":
        return "FAILED"
    if run_status == "INCOMPLETE" or observation_quality in {"INCOMPLETE", "INDETERMINATE"}:
        return "INCOMPLETE"
    if run_status == "SUCCESS" and observation_quality == "COMPARABLE":
        return "COMPARABLE"
    return "NOT_OBSERVED"
