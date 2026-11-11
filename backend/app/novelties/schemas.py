from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
