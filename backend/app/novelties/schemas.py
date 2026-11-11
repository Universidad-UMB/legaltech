from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ReviewText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=2000)]


class EvaluationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    comparison_id: UUID


class Evaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    tracking_id: UUID
    comparison_id: UUID
    decision: Literal["ELIGIBLE", "SKIPPED"]
    reason: str = Field(min_length=1)
    novelty_ids: list[UUID]


class Novelty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    novelty_code: str = Field(min_length=1)
    tracking_id: UUID
    status: Literal[
        "PENDING_OPERATIVE",
        "IN_OPERATIVE_REVIEW",
        "PENDING_LEGAL",
        "TREATMENT_DEFINED",
        "IN_FOLLOWUP",
        "DISCARDED",
    ]
    change_id: UUID


class NoveltyList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[Novelty]
    next_cursor: str | None = Field(..., min_length=1)


class OperativeEscalation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReviewText
    evidence_note: ReviewText


class LegalReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: ReviewText
    evidence_note: ReviewText
