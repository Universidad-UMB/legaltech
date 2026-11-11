from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PortalTracking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    tracking_code: str = Field(min_length=1)
    radicado: str = Field(min_length=23, max_length=23, pattern=r"^[0-9]{23}$")
    has_publication: bool
    coverage_status: Literal["COMPARABLE", "INCOMPLETE", "FAILED", "NOT_OBSERVED"]


class PortalTrackingList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PortalTracking]
    next_cursor: str | None = Field(min_length=1)


class PortalPublication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_id: UUID
    published_at: datetime
    content_text: str = Field(min_length=1)


class PortalPublicationResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "description": (
                "El valor available=false es válido únicamente para seguimientos autorizados, "
                "no revela recursos ajenos"
            )
        },
    )

    available: bool
    coverage_status: Literal["COMPARABLE", "INCOMPLETE", "FAILED", "NOT_OBSERVED"]
    publication: PortalPublication | None
