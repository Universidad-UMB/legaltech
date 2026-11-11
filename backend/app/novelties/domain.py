import base64
import binascii
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal, cast
from uuid import UUID

EvaluationDecision = Literal["ELIGIBLE", "SKIPPED"]
NoveltyStatus = Literal[
    "PENDING_OPERATIVE",
    "IN_OPERATIVE_REVIEW",
    "PENDING_LEGAL",
    "TREATMENT_DEFINED",
    "IN_FOLLOWUP",
    "DISCARDED",
]
ReviewKind = Literal["OPERATIVE", "LEGAL"]


@dataclass(frozen=True, slots=True)
class EvaluationData:
    id: UUID
    tracking_id: UUID
    comparison_id: UUID
    decision: EvaluationDecision
    reason: str
    novelty_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class NoveltyData:
    id: UUID
    novelty_code: str
    tracking_id: UUID
    status: NoveltyStatus
    change_id: UUID


@dataclass(frozen=True, slots=True)
class NoveltyPageData:
    items: tuple[NoveltyData, ...]
    next_cursor: str | None


def transition_novelty_status(current: str, target: NoveltyStatus) -> None:
    allowed: dict[str, frozenset[str]] = {
        "PENDING_OPERATIVE": frozenset({"IN_OPERATIVE_REVIEW"}),
        "IN_OPERATIVE_REVIEW": frozenset({"PENDING_LEGAL"}),
        "PENDING_LEGAL": frozenset({"TREATMENT_DEFINED"}),
    }
    if target not in allowed.get(current, frozenset()):
        raise ValueError("The novelty status transition is not allowed.")


def encode_novelty_cursor(created_at: datetime, novelty_id: UUID) -> str:
    timestamp = created_at.astimezone(UTC).isoformat(timespec="microseconds")
    payload = f"{timestamp}|{novelty_id}".encode("ascii")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def decode_novelty_cursor(cursor: str) -> tuple[datetime, UUID]:
    try:
        encoded = cursor.encode("ascii")
        padded = encoded + b"=" * (-len(encoded) % 4)
        decoded = base64.b64decode(padded, altchars=b"-_", validate=True).decode("ascii")
        timestamp, novelty_id = decoded.split("|", maxsplit=1)
        created_at = datetime.fromisoformat(timestamp)
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("Cursor timestamp must include a timezone.")
        parsed_id = UUID(novelty_id)
    except (UnicodeEncodeError, UnicodeDecodeError, binascii.Error, ValueError) as exc:
        raise ValueError("The novelty cursor is invalid.") from exc
    return created_at.astimezone(UTC), parsed_id


def evaluation_decision(
    comparison_result: str, change_count: int
) -> tuple[EvaluationDecision, str]:
    if comparison_result == "CHANGES_FOUND" and change_count > 0:
        return "ELIGIBLE", "The comparable fixture snapshots contain new action keys."
    if comparison_result == "NO_CHANGES" and change_count == 0:
        return "SKIPPED", "The comparable fixture snapshots contain no new action keys."
    raise ValueError("The comparison result and technical change set are inconsistent.")


def novelty_status(value: str) -> NoveltyStatus:
    return cast(NoveltyStatus, value)
