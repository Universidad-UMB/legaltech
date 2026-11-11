from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.clients.models import Client as Client
from app.db import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("id", "account_kind", name="uq_accounts_id_account_kind"),
        UniqueConstraint("id", "person_id", name="uq_accounts_id_person_id"),
        UniqueConstraint("id", "client_id", "account_kind", name="uq_accounts_id_client_kind"),
        CheckConstraint("account_kind IN ('INTERNAL', 'EXTERNAL')", name="account_kind"),
        CheckConstraint("status IN ('ACTIVE', 'DISABLED')", name="status"),
        CheckConstraint(
            "(account_kind = 'EXTERNAL' AND client_id IS NOT NULL) "
            "OR (account_kind = 'INTERNAL' AND client_id IS NULL)",
            name="kind_client",
        ),
        CheckConstraint(
            "length(username) > 0 AND username = lower(btrim(username))",
            name="username_normalized",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    person_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("persons.id", ondelete="RESTRICT"), nullable=False
    )
    username: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    account_kind: Mapped[str] = mapped_column(String(10), nullable=False)
    client_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class AccountRole(Base):
    __tablename__ = "account_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "account_kind"],
            ["accounts.id", "accounts.account_kind"],
            ondelete="CASCADE",
            name="fk_account_roles_account_kind",
        ),
        CheckConstraint(
            "(account_kind = 'EXTERNAL' AND role_code = 'EXTERNAL_READER') OR "
            "(account_kind = 'INTERNAL' AND role_code IN "
            "('ADMIN', 'ANALYST', 'LAWYER', 'PREPARER', 'COORDINATOR'))",
            name="kind_role",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_kind: Mapped[str] = mapped_column(String(10), primary_key=True)
    role_code: Mapped[str] = mapped_column(String(24), primary_key=True)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint("octet_length(token_digest) = 32", name="token_digest_length"),
        CheckConstraint("expires_at > issued_at", name="expiry_after_issue"),
        Index("ix_auth_sessions_account_expires_at", "account_id", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False
    )
    token_digest: Mapped[bytes] = mapped_column(LargeBinary, nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("result IN ('SUCCESS', 'DENIED', 'ERROR')", name="result"),
        Index("ix_audit_events_request_id", "request_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    request_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    event_code: Mapped[str] = mapped_column(String(64), nullable=False)
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    actor_account_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=True
    )
    resource_kind: Mapped[str | None] = mapped_column(String(32), nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    sanitized_reason: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
