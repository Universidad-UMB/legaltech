from dataclasses import dataclass
from typing import Literal
from uuid import UUID

EvaluationDecision = Literal["ELIGIBLE", "SKIPPED"]


@dataclass(frozen=True, slots=True)
class EvaluationData:
    id: UUID
    tracking_id: UUID
    comparison_id: UUID
    decision: EvaluationDecision
    reason: str
    novelty_ids: tuple[UUID, ...]


def evaluation_decision(
    comparison_result: str, change_count: int
) -> tuple[EvaluationDecision, str]:
    if comparison_result == "CHANGES_FOUND" and change_count > 0:
        return "ELIGIBLE", "The comparable fixture snapshots contain new action keys."
    if comparison_result == "NO_CHANGES" and change_count == 0:
        return "SKIPPED", "The comparable fixture snapshots contain no new action keys."
    raise ValueError("The comparison result and technical change set are inconsistent.")
