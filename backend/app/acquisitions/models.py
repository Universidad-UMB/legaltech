from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AcquisitionRun(Base):
    __tablename__ = "acquisition_runs"
    __table_args__ = (
        CheckConstraint("source_code = 'DEMO-FIXTURE'", name="source_code"),
        CheckConstraint(
            "fixture_code IN ('OBS_001', 'OBS_002', 'FAILED', 'INCOMPLETE')",
            name="fixture_code",
        ),
        CheckConstraint("status IN ('PENDING', 'SUCCESS', 'INCOMPLETE', 'FAILED')", name="status"),
        CheckConstraint(
            "(status = 'PENDING' AND finished_at IS NULL) "
            "OR (status <> 'PENDING' AND finished_at IS NOT NULL)",
            name="finish_state",
        ),
        CheckConstraint("status <> 'FAILED' OR error_code IS NOT NULL", name="failed_error"),
        CheckConstraint("request_payload_sha256 ~ '^[0-9a-f]{64}$'", name="payload_sha256"),
        UniqueConstraint("id", "process_id", name="uq_acquisition_runs_id_process_id"),
        Index("ix_acquisition_process_requested", "process_id", text("requested_at DESC")),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    process_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("judicial_processes.id", ondelete="RESTRICT"), nullable=False
    )
    source_code: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'DEMO-FIXTURE'")
    )
    fixture_code: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(12), nullable=False)
    request_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    request_payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    coverage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint("quality IN ('COMPARABLE', 'INCOMPLETE', 'INDETERMINATE')", name="quality"),
        CheckConstraint("payload_sha256 ~ '^[0-9a-f]{64}$'", name="payload_sha256"),
        CheckConstraint("provenance = 'DEMO-FIXTURE'", name="provenance"),
        CheckConstraint("received_at >= observed_at", name="received_after_observed"),
        CheckConstraint(
            "sealed_at IS NULL OR sealed_at >= received_at", name="seal_after_received"
        ),
        UniqueConstraint("acquisition_run_id", name="uq_observations_acquisition_run_id"),
        UniqueConstraint("id", "process_id", name="uq_observations_id_process_id"),
        ForeignKeyConstraint(
            ["acquisition_run_id", "process_id"],
            ["acquisition_runs.id", "acquisition_runs.process_id"],
            ondelete="RESTRICT",
            name="fk_observations_acquisition_process",
        ),
        Index("ix_observations_process_observed", "process_id", text("observed_at DESC")),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    process_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("judicial_processes.id", ondelete="RESTRICT"), nullable=False
    )
    acquisition_run_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quality: Mapped[str] = mapped_column(String(16), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    sealed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    payload_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    provenance: Mapped[str] = mapped_column(
        String(80), nullable=False, server_default=text("'DEMO-FIXTURE'")
    )
    coverage_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class ObservedAction(Base):
    __tablename__ = "observed_actions"
    __table_args__ = (
        CheckConstraint("action_key ~ '^ACT-[0-9]{2,}$'", name="action_key_format"),
        CheckConstraint("btrim(description) <> ''", name="description_nonblank"),
        CheckConstraint("content_sha256 ~ '^[0-9a-f]{64}$'", name="content_sha256"),
        ForeignKeyConstraint(
            ["observation_id"],
            ["observations.id"],
            ondelete="RESTRICT",
            name="fk_observed_actions_observation",
        ),
    )

    observation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    action_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_on: Mapped[date | None] = mapped_column(Date, nullable=True)
