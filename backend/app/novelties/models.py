from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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


class TrackingEvaluation(Base):
    __tablename__ = "tracking_evaluations"
    __table_args__ = (
        UniqueConstraint(
            "tracking_id", "comparison_id", name="uq_tracking_evaluations_tracking_comparison"
        ),
        UniqueConstraint(
            "id", "tracking_id", "comparison_id", name="uq_tracking_evaluations_identity"
        ),
        UniqueConstraint(
            "id",
            "tracking_id",
            "comparison_id",
            "decision",
            name="uq_tracking_evaluations_identity_decision",
        ),
        ForeignKeyConstraint(
            ["tracking_id", "process_id"],
            ["trackings.id", "trackings.process_id"],
            ondelete="RESTRICT",
            name="fk_tracking_evaluations_tracking_process",
        ),
        ForeignKeyConstraint(
            ["comparison_id", "process_id"],
            ["comparisons.id", "comparisons.process_id"],
            ondelete="RESTRICT",
            name="fk_tracking_evaluations_comparison_process",
        ),
        CheckConstraint("decision IN ('ELIGIBLE', 'SKIPPED')", name="decision"),
        CheckConstraint("btrim(reason) <> ''", name="reason_nonblank"),
        Index("ix_tracking_evaluations_comparison", "comparison_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    process_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    comparison_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(String(12), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Novelty(Base):
    __tablename__ = "novelties"
    __table_args__ = (
        UniqueConstraint("novelty_code", name="uq_novelties_code"),
        UniqueConstraint("tracking_id", "change_id", name="uq_novelties_tracking_change"),
        UniqueConstraint("id", "tracking_id", name="uq_novelties_id_tracking"),
        ForeignKeyConstraint(
            ["tracking_id", "client_id", "process_id"],
            ["trackings.id", "trackings.client_id", "trackings.process_id"],
            ondelete="RESTRICT",
            name="fk_novelties_tracking_client_process",
        ),
        ForeignKeyConstraint(
            ["change_id", "comparison_id", "process_id"],
            [
                "technical_changes.id",
                "technical_changes.comparison_id",
                "technical_changes.process_id",
            ],
            ondelete="RESTRICT",
            name="fk_novelties_change_comparison_process",
        ),
        ForeignKeyConstraint(
            ["evaluation_id", "tracking_id", "comparison_id", "evaluation_decision"],
            [
                "tracking_evaluations.id",
                "tracking_evaluations.tracking_id",
                "tracking_evaluations.comparison_id",
                "tracking_evaluations.decision",
            ],
            ondelete="RESTRICT",
            name="fk_novelties_eligible_evaluation",
        ),
        CheckConstraint("evaluation_decision = 'ELIGIBLE'", name="evaluation_eligible"),
        CheckConstraint(
            "status IN ('PENDING_OPERATIVE', 'IN_OPERATIVE_REVIEW', 'PENDING_LEGAL', "
            "'TREATMENT_DEFINED', 'IN_FOLLOWUP', 'DISCARDED')",
            name="status",
        ),
        Index("ix_novelties_tracking_status_created", "tracking_id", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    novelty_code: Mapped[str] = mapped_column(String(40), nullable=False)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    client_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    process_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    comparison_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    change_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    evaluation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    evaluation_decision: Mapped[str] = mapped_column(
        String(12), nullable=False, server_default=text("'ELIGIBLE'")
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default=text("'PENDING_OPERATIVE'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
