"""Create process and tracking persistence and scoped assignments.

Revision ID: 0002_clients_processes_trackings
Revises: 0001_identity_clients_audit
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_clients_processes_trackings"
down_revision: str | None = "0001_identity_clients_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_clients_nonblank",
        "clients",
        "btrim(client_code) <> '' AND btrim(name) <> ''",
    )
    op.create_unique_constraint(
        "uq_accounts_id_client_kind",
        "accounts",
        ["id", "client_id", "account_kind"],
    )
    op.create_table(
        "judicial_processes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("radicado", sa.String(length=23), nullable=False),
        sa.Column("label", sa.String(length=180), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "radicado ~ '^[0-9]{23}$'", name="ck_judicial_processes_radicado_format"
        ),
        sa.CheckConstraint(
            "label IS NULL OR btrim(label) <> ''",
            name="ck_judicial_processes_label_nonblank",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_judicial_processes"),
        sa.UniqueConstraint("radicado", name="uq_judicial_processes_radicado"),
    )
    op.create_table(
        "trackings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracking_code", sa.String(length=40), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=12),
            server_default=sa.text("'PENDING'"),
            nullable=False,
        ),
        sa.Column("baseline_observation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("last_adopted_observation_id", postgresql.UUID(as_uuid=True), nullable=True),
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
            "status IN ('PENDING', 'ACTIVE', 'FINISHED')", name="ck_trackings_status"
        ),
        sa.CheckConstraint(
            "(baseline_observation_id IS NULL) = (last_adopted_observation_id IS NULL)",
            name="ck_trackings_baseline_pair",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["clients.id"],
            name="fk_trackings_client_id_clients",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["process_id"],
            ["judicial_processes.id"],
            name="fk_trackings_process_id_judicial_processes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_trackings"),
        sa.UniqueConstraint("tracking_code", name="uq_trackings_tracking_code"),
        sa.UniqueConstraint("id", "client_id", name="uq_trackings_id_client_id"),
        sa.UniqueConstraint("id", "process_id", name="uq_trackings_id_process_id"),
        sa.UniqueConstraint("id", "client_id", "process_id", name="uq_trackings_id_client_process"),
    )
    op.create_index(
        "ux_trackings_open_per_client_process",
        "trackings",
        ["client_id", "process_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('PENDING', 'ACTIVE')"),
    )
    op.create_index("ix_trackings_client_status", "trackings", ["client_id", "status"])
    op.create_table(
        "external_tracking_scopes",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_kind",
            sa.String(length=10),
            server_default=sa.text("'EXTERNAL'"),
            nullable=False,
        ),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "permission_code",
            sa.String(length=32),
            server_default=sa.text("'READ_PUBLICATIONS'"),
            nullable=False,
        ),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "account_kind = 'EXTERNAL'", name="ck_external_tracking_scopes_account_kind"
        ),
        sa.CheckConstraint(
            "permission_code = 'READ_PUBLICATIONS'",
            name="ck_external_tracking_scopes_permission_code",
        ),
        sa.CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= granted_at",
            name="ck_external_tracking_scopes_revocation_order",
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "client_id", "account_kind"],
            ["accounts.id", "accounts.client_id", "accounts.account_kind"],
            name="fk_external_tracking_scopes_account_client_kind",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tracking_id", "client_id"],
            ["trackings.id", "trackings.client_id"],
            name="fk_external_tracking_scopes_tracking_client",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "account_id", "tracking_id", "permission_code", name="pk_external_tracking_scopes"
        ),
    )
    op.create_index(
        "ix_scopes_active_tracking",
        "external_tracking_scopes",
        ["client_id", "tracking_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )
    op.create_table(
        "internal_tracking_assignments",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "account_kind",
            sa.String(length=10),
            server_default=sa.text("'INTERNAL'"),
            nullable=False,
        ),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "account_kind = 'INTERNAL'", name="ck_internal_tracking_assignments_account_kind"
        ),
        sa.CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= assigned_at",
            name="ck_internal_tracking_assignments_revocation_order",
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "account_kind"],
            ["accounts.id", "accounts.account_kind"],
            name="fk_internal_tracking_assignments_account_kind",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tracking_id"],
            ["trackings.id"],
            name="fk_internal_tracking_assignments_tracking_id_trackings",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "account_id", "tracking_id", name="pk_internal_tracking_assignments"
        ),
    )
    op.create_index(
        "ix_internal_assignments_tracking_active",
        "internal_tracking_assignments",
        ["tracking_id"],
        postgresql_where=sa.text("revoked_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_internal_assignments_tracking_active", table_name="internal_tracking_assignments"
    )
    op.drop_table("internal_tracking_assignments")
    op.drop_index("ix_scopes_active_tracking", table_name="external_tracking_scopes")
    op.drop_table("external_tracking_scopes")
    op.drop_index("ix_trackings_client_status", table_name="trackings")
    op.drop_index("ux_trackings_open_per_client_process", table_name="trackings")
    op.drop_table("trackings")
    op.drop_table("judicial_processes")
    op.drop_constraint("uq_accounts_id_client_kind", "accounts", type_="unique")
    op.drop_constraint("ck_clients_nonblank", "clients", type_="check")
