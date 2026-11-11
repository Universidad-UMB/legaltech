from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

ComparisonOutcome = Literal["CHANGES_FOUND", "NO_CHANGES", "NOT_COMPARABLE"]


@dataclass(frozen=True, slots=True)
class ObservationSnapshot:
    id: UUID
    process_id: UUID
    quality: str
    sealed: bool
    observed_at: datetime
    action_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ComparisonDraft:
    result: ComparisonOutcome
    added_action_keys: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TechnicalChangeData:
    id: UUID
    action_key: str
    change_kind: Literal["ADDED"]
    evidence: str


@dataclass(frozen=True, slots=True)
class ComparisonData:
    id: UUID
    process_id: UUID
    old_observation_id: UUID
    new_observation_id: UUID
    rule_version: str
    result: ComparisonOutcome
    changes: tuple[TechnicalChangeData, ...]


def compare_snapshots(old: ObservationSnapshot, new: ObservationSnapshot) -> ComparisonDraft:
    """Compare fixture action identities without interpreting free text."""
    if old.process_id != new.process_id or old.id == new.id:
        return ComparisonDraft(result="NOT_COMPARABLE", added_action_keys=())

    if (
        old.quality != "COMPARABLE"
        or new.quality != "COMPARABLE"
        or not old.sealed
        or not new.sealed
        or old.observed_at >= new.observed_at
        or len(set(old.action_keys)) != len(old.action_keys)
        or len(set(new.action_keys)) != len(new.action_keys)
    ):
        return ComparisonDraft(result="NOT_COMPARABLE", added_action_keys=())

    added = tuple(sorted(set(new.action_keys).difference(old.action_keys)))
    if not added:
        return ComparisonDraft(result="NO_CHANGES", added_action_keys=())
    return ComparisonDraft(result="CHANGES_FOUND", added_action_keys=added)
