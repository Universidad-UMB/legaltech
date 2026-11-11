"""Create INC-00 identity, client, session, and auth audit tables.

Revision ID: 0001_identity_clients_audit
Revises:
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_identity_clients_audit"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_persons"),
    )
    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
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
        sa.CheckConstraint("status IN ('ACTIVE', 'SUSPENDED')", name="ck_clients_status"),
        sa.PrimaryKeyConstraint("id", name="pk_clients"),
        sa.UniqueConstraint("client_code", name="uq_clients_client_code"),
    )
    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("account_kind", sa.String(length=10), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(account_kind = 'EXTERNAL' AND client_id IS NOT NULL) "
            "OR (account_kind = 'INTERNAL' AND client_id IS NULL)",
            name="ck_accounts_kind_client",
        ),
        sa.CheckConstraint(
            "account_kind IN ('INTERNAL', 'EXTERNAL')", name="ck_accounts_account_kind"
        ),
        sa.CheckConstraint("status IN ('ACTIVE', 'DISABLED')", name="ck_accounts_status"),
        sa.CheckConstraint(
            "length(username) > 0 AND username = lower(btrim(username))",
            name="ck_accounts_username_normalized",
        ),
        sa.ForeignKeyConstraint(
            ["client_id"], ["clients.id"], name="fk_accounts_client_id_clients", ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["person_id"], ["persons.id"], name="fk_accounts_person_id_persons", ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_accounts"),
        sa.UniqueConstraint("id", "account_kind", name="uq_accounts_id_account_kind"),
        sa.UniqueConstraint("username", name="uq_accounts_username"),
    )
    op.create_table(
        "account_roles",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_kind", sa.String(length=10), nullable=False),
        sa.Column("role_code", sa.String(length=24), nullable=False),
        sa.CheckConstraint(
            "(account_kind = 'EXTERNAL' AND role_code = 'EXTERNAL_READER') OR "
            "(account_kind = 'INTERNAL' AND role_code IN "
            "('ADMIN', 'ANALYST', 'LAWYER', 'PREPARER', 'COORDINATOR'))",
            name="ck_account_roles_kind_role",
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "account_kind"],
            ["accounts.id", "accounts.account_kind"],
            name="fk_account_roles_account_kind",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("account_id", "account_kind", "role_code", name="pk_account_roles"),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_digest", postgresql.BYTEA(), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("expires_at > issued_at", name="ck_auth_sessions_expiry_after_issue"),
        sa.CheckConstraint(
            "octet_length(token_digest) = 32", name="ck_auth_sessions_token_digest_length"
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
            name="fk_auth_sessions_account_id_accounts",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_auth_sessions"),
        sa.UniqueConstraint("token_digest", name="uq_auth_sessions_token_digest"),
    )
    op.create_index(
        "ix_auth_sessions_account_expires_at", "auth_sessions", ["account_id", "expires_at"]
    )
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_code", sa.String(length=64), nullable=False),
        sa.Column("result", sa.String(length=10), nullable=False),
        sa.Column("actor_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resource_kind", sa.String(length=32), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sanitized_reason", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "result IN ('SUCCESS', 'DENIED', 'ERROR')", name="ck_audit_events_result"
        ),
        sa.ForeignKeyConstraint(
            ["actor_account_id"],
            ["accounts.id"],
            name="fk_audit_events_actor_account_id_accounts",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_audit_events"),
    )
    op.create_index("ix_audit_events_request_id", "audit_events", ["request_id"])
    op.execute("REVOKE UPDATE, DELETE ON TABLE audit_events FROM legaltech_runtime")


def downgrade() -> None:
    op.drop_index("ix_audit_events_request_id", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_index("ix_auth_sessions_account_expires_at", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_table("account_roles")
    op.drop_table("accounts")
    op.drop_table("clients")
    op.drop_table("persons")
