from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ComparisonCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    old_observation_id: UUID
    new_observation_id: UUID
    rule_version: str = Field(min_length=1, max_length=32)

    @field_validator("rule_version")
    @classmethod
    def rule_version_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("rule_version must not be blank")
        return normalized


class TechnicalChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    action_key: str = Field(min_length=1)
    change_kind: Literal["ADDED"]
    evidence: str = Field(min_length=1)


class Comparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    process_id: UUID
    old_observation_id: UUID
    new_observation_id: UUID
    rule_version: str = Field(min_length=1)
    result: Literal["CHANGES_FOUND", "NO_CHANGES", "NOT_COMPARABLE"]
    changes: list[TechnicalChange]
