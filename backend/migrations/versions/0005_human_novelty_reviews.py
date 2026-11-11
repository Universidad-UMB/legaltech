"""Persist human novelty reviews and actor-attributed state history.

Revision ID: 0005_human_novelty_reviews
Revises: 0004_comparisons_and_novelties
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_human_novelty_reviews"
down_revision: str | None = "0004_comparisons_and_novelties"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint("uq_accounts_id_person_id", "accounts", ["id", "person_id"])

    op.create_table(
        "novelty_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("novelty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("review_kind", sa.String(length=16), nullable=False),
        sa.Column("review_sequence", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("actor_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("evidence_note", sa.Text(), nullable=False),
        sa.Column(
            "reviewed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "review_kind IN ('OPERATIVE', 'LEGAL')", name="ck_novelty_reviews_review_kind"
        ),
        sa.CheckConstraint(
            "review_sequence > 0", name="ck_novelty_reviews_review_sequence_positive"
        ),
        sa.CheckConstraint("btrim(decision) <> ''", name="ck_novelty_reviews_decision_nonblank"),
        sa.CheckConstraint(
            "btrim(evidence_note) <> ''", name="ck_novelty_reviews_evidence_note_nonblank"
        ),
        sa.ForeignKeyConstraint(
            ["novelty_id"],
            ["novelties.id"],
            name="fk_novelty_reviews_novelty",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_account_id", "actor_person_id"],
            ["accounts.id", "accounts.person_id"],
            name="fk_novelty_reviews_actor_person",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_novelty_reviews"),
        sa.UniqueConstraint(
            "novelty_id",
            "review_kind",
            "review_sequence",
            name="uq_novelty_reviews_sequence",
        ),
    )
    op.create_index(
        "ix_novelty_reviews_novelty_kind", "novelty_reviews", ["novelty_id", "review_kind"]
    )

    op.create_table(
        "state_transitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_type", sa.String(length=24), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("novelty_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("from_state", sa.String(length=40), nullable=True),
        sa.Column("to_state", sa.String(length=40), nullable=False),
        sa.Column("actor_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_person_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_kind", sa.String(length=8), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "resource_type IN ('CLIENT', 'TRACKING', 'NOVELTY')",
            name="ck_state_transitions_resource_type",
        ),
        sa.CheckConstraint(
            "actor_kind IN ('USER', 'SYSTEM')", name="ck_state_transitions_actor_kind"
        ),
        sa.CheckConstraint(
            "((client_id IS NOT NULL)::int + (tracking_id IS NOT NULL)::int + "
            "(novelty_id IS NOT NULL)::int + (version_id IS NOT NULL)::int) = 1",
            name="ck_state_transitions_exactly_one_resource",
        ),
        sa.CheckConstraint(
            "(resource_type = 'CLIENT' AND client_id IS NOT NULL) OR "
            "(resource_type = 'TRACKING' AND tracking_id IS NOT NULL) OR "
            "(resource_type = 'NOVELTY' AND novelty_id IS NOT NULL)",
            name="ck_state_transitions_resource_type_matches_id",
        ),
        sa.CheckConstraint(
            "(actor_kind = 'USER' AND actor_account_id IS NOT NULL "
            "AND actor_person_id IS NOT NULL) "
            "OR (actor_kind = 'SYSTEM' AND actor_account_id IS NULL AND actor_person_id IS NULL)",
            name="ck_state_transitions_actor_identity",
        ),
        sa.CheckConstraint("btrim(reason) <> ''", name="ck_state_transitions_reason_nonblank"),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name="fk_state_transitions_client",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tracking_id"],
            ["trackings.id"],
            name="fk_state_transitions_tracking",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["novelty_id"],
            ["novelties.id"],
            name="fk_state_transitions_novelty",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["actor_account_id", "actor_person_id"],
            ["accounts.id", "accounts.person_id"],
            name="fk_state_transitions_actor_person",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_state_transitions"),
    )
    op.create_index(
        "ix_state_transitions_tracking_occurred",
        "state_transitions",
        ["tracking_id", "occurred_at"],
        postgresql_where=sa.text("tracking_id IS NOT NULL"),
    )
    op.create_index(
        "ix_state_transitions_novelty_occurred",
        "state_transitions",
        ["novelty_id", "occurred_at"],
        postgresql_where=sa.text("novelty_id IS NOT NULL"),
    )

    op.execute(
        """
        CREATE FUNCTION f5_reject_append_only_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION '% is append-only', TG_TABLE_NAME USING ERRCODE = '55000';
        END $$;
        """
    )
    op.execute(
        """
        CREATE TRIGGER tr_novelty_reviews_append_only
        BEFORE UPDATE OR DELETE ON novelty_reviews
        FOR EACH ROW EXECUTE FUNCTION f5_reject_append_only_mutation();
        """
    )
    op.execute(
        """
        CREATE TRIGGER tr_state_transitions_append_only
        BEFORE UPDATE OR DELETE ON state_transitions
        FOR EACH ROW EXECUTE FUNCTION f5_reject_append_only_mutation();
        """
    )
    op.execute("REVOKE UPDATE, DELETE ON TABLE novelty_reviews FROM legaltech_runtime")
    op.execute("REVOKE UPDATE, DELETE ON TABLE state_transitions FROM legaltech_runtime")


def downgrade() -> None:
    op.execute("DROP TRIGGER tr_state_transitions_append_only ON state_transitions")
    op.execute("DROP TRIGGER tr_novelty_reviews_append_only ON novelty_reviews")
    op.execute("DROP FUNCTION f5_reject_append_only_mutation()")
    op.drop_index("ix_state_transitions_novelty_occurred", table_name="state_transitions")
    op.drop_index("ix_state_transitions_tracking_occurred", table_name="state_transitions")
    op.drop_table("state_transitions")
    op.drop_index("ix_novelty_reviews_novelty_kind", table_name="novelty_reviews")
    op.drop_table("novelty_reviews")
    op.drop_constraint("uq_accounts_id_person_id", "accounts", type_="unique")
