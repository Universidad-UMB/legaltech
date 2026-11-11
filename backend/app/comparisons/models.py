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


class Comparison(Base):
    __tablename__ = "comparisons"
    __table_args__ = (
        UniqueConstraint(
            "old_observation_id",
            "new_observation_id",
            "rule_version",
            name="uq_comparisons_pair_rule",
        ),
        UniqueConstraint("id", "process_id", name="uq_comparisons_id_process_id"),
        UniqueConstraint(
            "id",
            "process_id",
            "new_observation_id",
            name="uq_comparisons_id_process_new_observation",
        ),
        ForeignKeyConstraint(
            ["old_observation_id", "process_id"],
            ["observations.id", "observations.process_id"],
            ondelete="RESTRICT",
            name="fk_comparisons_old_observation_process",
        ),
        ForeignKeyConstraint(
            ["new_observation_id", "process_id"],
            ["observations.id", "observations.process_id"],
            ondelete="RESTRICT",
            name="fk_comparisons_new_observation_process",
        ),
        CheckConstraint("old_observation_id <> new_observation_id", name="different_observations"),
        CheckConstraint("btrim(rule_version) <> ''", name="rule_version_nonblank"),
        CheckConstraint(
            "result IN ('CHANGES_FOUND', 'NO_CHANGES', 'NOT_COMPARABLE')", name="result"
        ),
        Index("ix_comparisons_process_created", "process_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    process_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    old_observation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    new_observation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(32), nullable=False)
    result: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class TechnicalChange(Base):
    __tablename__ = "technical_changes"
    __table_args__ = (
        UniqueConstraint(
            "comparison_id", "action_key", "change_kind", name="uq_technical_changes_logical"
        ),
        UniqueConstraint("id", "process_id", name="uq_technical_changes_id_process_id"),
        UniqueConstraint(
            "id",
            "comparison_id",
            "process_id",
            name="uq_technical_changes_id_comparison_process",
        ),
        ForeignKeyConstraint(
            ["comparison_id", "process_id", "new_observation_id"],
            ["comparisons.id", "comparisons.process_id", "comparisons.new_observation_id"],
            ondelete="RESTRICT",
            name="fk_technical_changes_comparison_process_new_observation",
        ),
        ForeignKeyConstraint(
            ["new_observation_id", "action_key"],
            ["observed_actions.observation_id", "observed_actions.action_key"],
            ondelete="RESTRICT",
            name="fk_technical_changes_action_in_new_observation",
        ),
        CheckConstraint("change_kind = 'ADDED'", name="change_kind"),
        CheckConstraint("btrim(evidence) <> ''", name="evidence_nonblank"),
        Index("ix_technical_changes_process", "process_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    comparison_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    process_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    new_observation_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    action_key: Mapped[str] = mapped_column(String(64), nullable=False)
    change_kind: Mapped[str] = mapped_column(
        String(12), nullable=False, server_default=text("'ADDED'")
    )
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
