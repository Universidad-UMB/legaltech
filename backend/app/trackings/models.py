from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class JudicialProcess(Base):
    __tablename__ = "judicial_processes"
    __table_args__ = (
        CheckConstraint("radicado ~ '^[0-9]{23}$'", name="radicado_format"),
        CheckConstraint("label IS NULL OR btrim(label) <> ''", name="label_nonblank"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    radicado: Mapped[str] = mapped_column(String(23), nullable=False, unique=True)
    label: Mapped[str | None] = mapped_column(String(180), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Tracking(Base):
    __tablename__ = "trackings"
    __table_args__ = (
        UniqueConstraint("id", "client_id", name="uq_trackings_id_client_id"),
        UniqueConstraint("id", "process_id", name="uq_trackings_id_process_id"),
        UniqueConstraint("id", "client_id", "process_id", name="uq_trackings_id_client_process"),
        CheckConstraint("status IN ('PENDING', 'ACTIVE', 'FINISHED')", name="status"),
        CheckConstraint(
            "(baseline_observation_id IS NULL) = (last_adopted_observation_id IS NULL)",
            name="baseline_pair",
        ),
        Index(
            "ux_trackings_open_per_client_process",
            "client_id",
            "process_id",
            unique=True,
            postgresql_where=text("status IN ('PENDING', 'ACTIVE')"),
        ),
        Index("ix_trackings_client_status", "client_id", "status"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    client_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False
    )
    process_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("judicial_processes.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(12), nullable=False, server_default="PENDING")
    baseline_observation_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    last_adopted_observation_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ExternalTrackingScope(Base):
    __tablename__ = "external_tracking_scopes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "client_id", "account_kind"],
            ["accounts.id", "accounts.client_id", "accounts.account_kind"],
            ondelete="RESTRICT",
            name="fk_external_tracking_scopes_account_client_kind",
        ),
        ForeignKeyConstraint(
            ["tracking_id", "client_id"],
            ["trackings.id", "trackings.client_id"],
            ondelete="RESTRICT",
            name="fk_external_tracking_scopes_tracking_client",
        ),
        CheckConstraint("account_kind = 'EXTERNAL'", name="account_kind"),
        CheckConstraint("permission_code = 'READ_PUBLICATIONS'", name="permission_code"),
        CheckConstraint("revoked_at IS NULL OR revoked_at >= granted_at", name="revocation_order"),
        Index(
            "ix_scopes_active_tracking",
            "client_id",
            "tracking_id",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    permission_code: Mapped[str] = mapped_column(
        String(32), primary_key=True, server_default="READ_PUBLICATIONS"
    )
    account_kind: Mapped[str] = mapped_column(String(10), nullable=False, server_default="EXTERNAL")
    client_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InternalTrackingAssignment(Base):
    __tablename__ = "internal_tracking_assignments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "account_kind"],
            ["accounts.id", "accounts.account_kind"],
            ondelete="RESTRICT",
            name="fk_internal_tracking_assignments_account_kind",
        ),
        ForeignKeyConstraint(["tracking_id"], ["trackings.id"], ondelete="RESTRICT"),
        CheckConstraint("account_kind = 'INTERNAL'", name="account_kind"),
        CheckConstraint("revoked_at IS NULL OR revoked_at >= assigned_at", name="revocation_order"),
        Index(
            "ix_internal_assignments_tracking_active",
            "tracking_id",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_kind: Mapped[str] = mapped_column(String(10), nullable=False, server_default="INTERNAL")
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
