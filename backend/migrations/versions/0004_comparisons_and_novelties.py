"""Persist deterministic comparisons, contextual evaluations, and novelties.

Revision ID: 0004_comparisons_and_novelties
Revises: 0003_synthetic_acquisitions
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_comparisons_and_novelties"
down_revision: str | None = "0003_synthetic_acquisitions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comparisons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("old_observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("new_observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_version", sa.String(length=32), nullable=False),
        sa.Column("result", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "old_observation_id <> new_observation_id",
            name="ck_comparisons_different_observations",
        ),
        sa.CheckConstraint(
            "btrim(rule_version) <> ''", name="ck_comparisons_rule_version_nonblank"
        ),
        sa.CheckConstraint(
            "result IN ('CHANGES_FOUND', 'NO_CHANGES', 'NOT_COMPARABLE')",
            name="ck_comparisons_result",
        ),
        sa.ForeignKeyConstraint(
            ["old_observation_id", "process_id"],
            ["observations.id", "observations.process_id"],
            name="fk_comparisons_old_observation_process",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["new_observation_id", "process_id"],
            ["observations.id", "observations.process_id"],
            name="fk_comparisons_new_observation_process",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_comparisons"),
        sa.UniqueConstraint("id", "process_id", name="uq_comparisons_id_process_id"),
        sa.UniqueConstraint(
            "id",
            "process_id",
            "new_observation_id",
            name="uq_comparisons_id_process_new_observation",
        ),
        sa.UniqueConstraint(
            "old_observation_id",
            "new_observation_id",
            "rule_version",
            name="uq_comparisons_pair_rule",
        ),
    )
    op.create_index("ix_comparisons_process_created", "comparisons", ["process_id", "created_at"])

    op.create_table(
        "technical_changes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("comparison_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("new_observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_key", sa.String(length=64), nullable=False),
        sa.Column(
            "change_kind", sa.String(length=12), server_default=sa.text("'ADDED'"), nullable=False
        ),
        sa.Column("evidence", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("change_kind = 'ADDED'", name="ck_technical_changes_change_kind"),
        sa.CheckConstraint("btrim(evidence) <> ''", name="ck_technical_changes_evidence_nonblank"),
        sa.ForeignKeyConstraint(
            ["comparison_id", "process_id", "new_observation_id"],
            ["comparisons.id", "comparisons.process_id", "comparisons.new_observation_id"],
            name="fk_technical_changes_comparison_process_new_observation",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["new_observation_id", "action_key"],
            ["observed_actions.observation_id", "observed_actions.action_key"],
            name="fk_technical_changes_action_in_new_observation",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_technical_changes"),
        sa.UniqueConstraint(
            "comparison_id", "action_key", "change_kind", name="uq_technical_changes_logical"
        ),
        sa.UniqueConstraint("id", "process_id", name="uq_technical_changes_id_process_id"),
        sa.UniqueConstraint(
            "id",
            "comparison_id",
            "process_id",
            name="uq_technical_changes_id_comparison_process",
        ),
    )
    op.create_index("ix_technical_changes_process", "technical_changes", ["process_id"])

    op.create_table(
        "tracking_evaluations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("comparison_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.String(length=12), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "decision IN ('ELIGIBLE', 'SKIPPED')", name="ck_tracking_evaluations_decision"
        ),
        sa.CheckConstraint("btrim(reason) <> ''", name="ck_tracking_evaluations_reason_nonblank"),
        sa.ForeignKeyConstraint(
            ["tracking_id", "process_id"],
            ["trackings.id", "trackings.process_id"],
            name="fk_tracking_evaluations_tracking_process",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["comparison_id", "process_id"],
            ["comparisons.id", "comparisons.process_id"],
            name="fk_tracking_evaluations_comparison_process",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_tracking_evaluations"),
        sa.UniqueConstraint(
            "tracking_id", "comparison_id", name="uq_tracking_evaluations_tracking_comparison"
        ),
        sa.UniqueConstraint(
            "id",
            "tracking_id",
            "comparison_id",
            name="uq_tracking_evaluations_identity",
        ),
        sa.UniqueConstraint(
            "id",
            "tracking_id",
            "comparison_id",
            "decision",
            name="uq_tracking_evaluations_identity_decision",
        ),
    )
    op.create_index("ix_tracking_evaluations_comparison", "tracking_evaluations", ["comparison_id"])

    op.create_table(
        "novelties",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("novelty_code", sa.String(length=40), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("comparison_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("change_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evaluation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "evaluation_decision",
            sa.String(length=12),
            server_default=sa.text("'ELIGIBLE'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'PENDING_OPERATIVE'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "evaluation_decision = 'ELIGIBLE'", name="ck_novelties_evaluation_eligible"
        ),
        sa.CheckConstraint(
            "status IN ('PENDING_OPERATIVE', 'IN_OPERATIVE_REVIEW', 'PENDING_LEGAL', "
            "'TREATMENT_DEFINED', 'IN_FOLLOWUP', 'DISCARDED')",
            name="ck_novelties_status",
        ),
        sa.ForeignKeyConstraint(
            ["tracking_id", "client_id", "process_id"],
            ["trackings.id", "trackings.client_id", "trackings.process_id"],
            name="fk_novelties_tracking_client_process",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["change_id", "comparison_id", "process_id"],
            [
                "technical_changes.id",
                "technical_changes.comparison_id",
                "technical_changes.process_id",
            ],
            name="fk_novelties_change_comparison_process",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["evaluation_id", "tracking_id", "comparison_id", "evaluation_decision"],
            [
                "tracking_evaluations.id",
                "tracking_evaluations.tracking_id",
                "tracking_evaluations.comparison_id",
                "tracking_evaluations.decision",
            ],
            name="fk_novelties_eligible_evaluation",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_novelties"),
        sa.UniqueConstraint("id", "tracking_id", name="uq_novelties_id_tracking"),
        sa.UniqueConstraint("novelty_code", name="uq_novelties_code"),
        sa.UniqueConstraint("tracking_id", "change_id", name="uq_novelties_tracking_change"),
    )
    op.create_index(
        "ix_novelties_tracking_status_created",
        "novelties",
        ["tracking_id", "status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_novelties_tracking_status_created", table_name="novelties")
    op.drop_table("novelties")
    op.drop_index("ix_tracking_evaluations_comparison", table_name="tracking_evaluations")
    op.drop_table("tracking_evaluations")
    op.drop_index("ix_technical_changes_process", table_name="technical_changes")
    op.drop_table("technical_changes")
    op.drop_index("ix_comparisons_process_created", table_name="comparisons")
    op.drop_table("comparisons")
