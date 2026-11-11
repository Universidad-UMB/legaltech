from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
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


class NoveltyReview(Base):
    __tablename__ = "novelty_reviews"
    __table_args__ = (
        UniqueConstraint(
            "novelty_id", "review_kind", "review_sequence", name="uq_novelty_reviews_sequence"
        ),
        ForeignKeyConstraint(
            ["actor_account_id", "actor_person_id"],
            ["accounts.id", "accounts.person_id"],
            ondelete="RESTRICT",
            name="fk_novelty_reviews_actor_person",
        ),
        CheckConstraint("review_kind IN ('OPERATIVE', 'LEGAL')", name="review_kind"),
        CheckConstraint("review_sequence > 0", name="review_sequence_positive"),
        CheckConstraint("btrim(decision) <> ''", name="decision_nonblank"),
        CheckConstraint("btrim(evidence_note) <> ''", name="evidence_note_nonblank"),
        Index("ix_novelty_reviews_novelty_kind", "novelty_id", "review_kind"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    novelty_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("novelties.id", ondelete="RESTRICT"), nullable=False
    )
    review_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    review_sequence: Mapped[int] = mapped_column(nullable=False, server_default=text("1"))
    actor_account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_person_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_note: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class StateTransition(Base):
    __tablename__ = "state_transitions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["actor_account_id", "actor_person_id"],
            ["accounts.id", "accounts.person_id"],
            ondelete="RESTRICT",
            name="fk_state_transitions_actor_person",
        ),
        CheckConstraint("resource_type IN ('CLIENT', 'TRACKING', 'NOVELTY')", name="resource_type"),
        CheckConstraint("actor_kind IN ('USER', 'SYSTEM')", name="actor_kind"),
        CheckConstraint(
            "((client_id IS NOT NULL)::int + (tracking_id IS NOT NULL)::int + "
            "(novelty_id IS NOT NULL)::int + (version_id IS NOT NULL)::int) = 1",
            name="exactly_one_resource",
        ),
        CheckConstraint(
            "(resource_type = 'CLIENT' AND client_id IS NOT NULL) OR "
            "(resource_type = 'TRACKING' AND tracking_id IS NOT NULL) OR "
            "(resource_type = 'NOVELTY' AND novelty_id IS NOT NULL)",
            name="resource_type_matches_id",
        ),
        CheckConstraint(
            "(actor_kind = 'USER' AND actor_account_id IS NOT NULL "
            "AND actor_person_id IS NOT NULL) "
            "OR (actor_kind = 'SYSTEM' AND actor_account_id IS NULL AND actor_person_id IS NULL)",
            name="actor_identity",
        ),
        CheckConstraint("btrim(reason) <> ''", name="reason_nonblank"),
        ForeignKeyConstraint(
            ["client_id"], ["clients.id"], ondelete="RESTRICT", name="fk_state_transitions_client"
        ),
        ForeignKeyConstraint(
            ["tracking_id"],
            ["trackings.id"],
            ondelete="RESTRICT",
            name="fk_state_transitions_tracking",
        ),
        ForeignKeyConstraint(
            ["novelty_id"],
            ["novelties.id"],
            ondelete="RESTRICT",
            name="fk_state_transitions_novelty",
        ),
        Index(
            "ix_state_transitions_tracking_occurred",
            "tracking_id",
            "occurred_at",
            postgresql_where=text("tracking_id IS NOT NULL"),
        ),
        Index(
            "ix_state_transitions_novelty_occurred",
            "novelty_id",
            "occurred_at",
            postgresql_where=text("novelty_id IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    resource_type: Mapped[str] = mapped_column(String(24), nullable=False)
    client_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    tracking_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    novelty_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    version_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    from_state: Mapped[str | None] = mapped_column(String(40), nullable=True)
    to_state: Mapped[str] = mapped_column(String(40), nullable=False)
    actor_account_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    actor_person_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    actor_kind: Mapped[str] = mapped_column(String(8), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    request_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
