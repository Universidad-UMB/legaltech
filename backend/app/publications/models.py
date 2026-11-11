from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Publication(Base):
    __tablename__ = "publications"
    __table_args__ = (
        UniqueConstraint("id", "tracking_id", "client_id", name="uq_publications_identity"),
        ForeignKeyConstraint(
            ["tracking_id", "client_id"],
            ["trackings.id", "trackings.client_id"],
            ondelete="RESTRICT",
            name="fk_publications_tracking_client",
        ),
        ForeignKeyConstraint(
            ["current_version_id", "id"],
            ["publication_versions.id", "publication_versions.publication_id"],
            ondelete="RESTRICT",
            name="fk_publications_current_version",
            use_alter=True,
        ),
        Index("ix_publications_tracking", "tracking_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    client_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    current_version_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class PublicationVersion(Base):
    __tablename__ = "publication_versions"
    __table_args__ = (
        UniqueConstraint(
            "publication_id", "version_number", name="uq_publication_versions_publication_version"
        ),
        UniqueConstraint("id", "publication_id", name="uq_publication_versions_identity"),
        UniqueConstraint(
            "id", "recipient_tracking_id", name="uq_publication_versions_recipient_tracking"
        ),
        ForeignKeyConstraint(
            ["publication_id", "recipient_tracking_id", "recipient_client_id"],
            ["publications.id", "publications.tracking_id", "publications.client_id"],
            ondelete="RESTRICT",
            name="fk_publication_versions_publication_recipient",
        ),
        CheckConstraint("version_number > 0", name="version_number_positive"),
        CheckConstraint(
            "status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'PUBLISHED')",
            name="status",
        ),
        CheckConstraint("btrim(content_text) <> ''", name="content_nonblank"),
        CheckConstraint("content_sha256 ~ '^[0-9a-f]{64}$'", name="content_hash"),
        CheckConstraint("status = 'DRAFT' OR frozen_at IS NOT NULL", name="frozen_after_submit"),
        CheckConstraint(
            "status NOT IN ('APPROVED', 'PUBLISHED') OR approved_at IS NOT NULL",
            name="approved_timestamp",
        ),
        CheckConstraint("status <> 'PUBLISHED' OR published_at IS NOT NULL", name="published_at"),
        CheckConstraint(
            "(status = 'DRAFT' AND frozen_at IS NULL AND approved_at IS NULL "
            "AND published_at IS NULL) "
            "OR (status = 'PENDING_APPROVAL' AND frozen_at IS NOT NULL AND approved_at IS NULL "
            "AND published_at IS NULL) "
            "OR (status = 'APPROVED' AND frozen_at IS NOT NULL AND approved_at IS NOT NULL "
            "AND published_at IS NULL) "
            "OR (status = 'REJECTED' AND frozen_at IS NOT NULL AND approved_at IS NULL "
            "AND published_at IS NULL) "
            "OR (status = 'PUBLISHED' AND frozen_at IS NOT NULL AND approved_at IS NOT NULL "
            "AND published_at IS NOT NULL)",
            name="status_timestamps",
        ),
        Index("ix_publication_versions_publication", "publication_id", "version_number"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    publication_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient_tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    recipient_client_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'DRAFT'"))
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PublicationPreparer(Base):
    __tablename__ = "publication_preparers"
    __table_args__ = (
        ForeignKeyConstraint(
            ["account_id", "person_id"],
            ["accounts.id", "accounts.person_id"],
            ondelete="RESTRICT",
            name="account_person",
        ),
        ForeignKeyConstraint(["version_id"], ["publication_versions.id"], ondelete="RESTRICT"),
    )

    version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    person_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class PublicationVersionNovelty(Base):
    __tablename__ = "publication_version_novelties"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version_id", "tracking_id"],
            ["publication_versions.id", "publication_versions.recipient_tracking_id"],
            ondelete="RESTRICT",
            name="fk_publication_version_novelties_version_tracking",
        ),
        ForeignKeyConstraint(
            ["novelty_id", "tracking_id"],
            ["novelties.id", "novelties.tracking_id"],
            ondelete="RESTRICT",
            name="fk_publication_version_novelties_novelty_tracking",
        ),
        Index("ix_publication_version_novelties_tracking", "tracking_id", "novelty_id"),
    )

    version_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    novelty_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tracking_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)


class PublicationApproval(Base):
    __tablename__ = "publication_approvals"
    __table_args__ = (
        ForeignKeyConstraint(
            ["approver_account_id", "approver_person_id"],
            ["accounts.id", "accounts.person_id"],
            ondelete="RESTRICT",
            name="fk_publication_approvals_approver_person",
        ),
        CheckConstraint("verdict IN ('APPROVE', 'REJECT')", name="verdict"),
        CheckConstraint("snapshot_sha256 ~ '^[0-9a-f]{64}$'", name="snapshot_hash"),
        CheckConstraint("btrim(justification) <> ''", name="justification_nonblank"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    version_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("publication_versions.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
    )
    approver_account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    approver_person_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    verdict: Mapped[str] = mapped_column(String(8), nullable=False)
    snapshot_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
