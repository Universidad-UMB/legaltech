"""Add versioned publications, approvals, and atomic publication state.

Revision ID: 0006_versioned_publications
Revises: 0005_human_novelty_reviews
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_versioned_publications"
down_revision: str | None = "0005_human_novelty_reviews"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "publications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tracking_id", "client_id"],
            ["trackings.id", "trackings.client_id"],
            name="fk_publications_tracking_client",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_publications"),
        sa.UniqueConstraint("id", "tracking_id", "client_id", name="uq_publications_identity"),
    )
    op.create_index("ix_publications_tracking", "publications", ["tracking_id"])

    op.create_table(
        "publication_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("publication_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("recipient_tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient_client_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=24),
            server_default=sa.text("'DRAFT'"),
            nullable=False,
        ),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "version_number > 0", name="ck_publication_versions_version_number_positive"
        ),
        sa.CheckConstraint(
            "status IN ('DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'PUBLISHED')",
            name="ck_publication_versions_status",
        ),
        sa.CheckConstraint(
            "btrim(content_text) <> ''", name="ck_publication_versions_content_nonblank"
        ),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'", name="ck_publication_versions_content_hash"
        ),
        sa.CheckConstraint(
            "status = 'DRAFT' OR frozen_at IS NOT NULL",
            name="ck_publication_versions_frozen_after_submit",
        ),
        sa.CheckConstraint(
            "status NOT IN ('APPROVED', 'PUBLISHED') OR approved_at IS NOT NULL",
            name="ck_publication_versions_approved_timestamp",
        ),
        sa.CheckConstraint(
            "status <> 'PUBLISHED' OR published_at IS NOT NULL",
            name="ck_publication_versions_published_at",
        ),
        sa.CheckConstraint(
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
            name="ck_publication_versions_status_timestamps",
        ),
        sa.ForeignKeyConstraint(
            ["publication_id", "recipient_tracking_id", "recipient_client_id"],
            ["publications.id", "publications.tracking_id", "publications.client_id"],
            name="fk_publication_versions_publication_recipient",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_publication_versions"),
        sa.UniqueConstraint(
            "publication_id", "version_number", name="uq_publication_versions_publication_version"
        ),
        sa.UniqueConstraint("id", "publication_id", name="uq_publication_versions_identity"),
        sa.UniqueConstraint(
            "id", "recipient_tracking_id", name="uq_publication_versions_recipient_tracking"
        ),
    )
    op.create_index(
        "ix_publication_versions_publication",
        "publication_versions",
        ["publication_id", "version_number"],
    )
    op.create_foreign_key(
        "fk_publications_current_version",
        "publications",
        "publication_versions",
        ["current_version_id", "id"],
        ["id", "publication_id"],
        ondelete="RESTRICT",
    )

    op.create_table(
        "publication_preparers",
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id", "person_id"],
            ["accounts.id", "accounts.person_id"],
            name="fk_publication_preparers_account_person",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["version_id"],
            ["publication_versions.id"],
            name="fk_publication_preparers_version_id_publication_versions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("version_id", "person_id", name="pk_publication_preparers"),
    )

    op.create_table(
        "publication_version_novelties",
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("novelty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tracking_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["version_id", "tracking_id"],
            ["publication_versions.id", "publication_versions.recipient_tracking_id"],
            name="fk_publication_version_novelties_version_tracking",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["novelty_id", "tracking_id"],
            ["novelties.id", "novelties.tracking_id"],
            name="fk_publication_version_novelties_novelty_tracking",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "version_id", "novelty_id", name="pk_publication_version_novelties"
        ),
    )
    op.create_index(
        "ix_publication_version_novelties_tracking",
        "publication_version_novelties",
        ["tracking_id", "novelty_id"],
    )

    op.create_table(
        "publication_approvals",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("approver_person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("verdict", sa.String(length=8), nullable=False),
        sa.Column("snapshot_sha256", sa.String(length=64), nullable=False),
        sa.Column("justification", sa.Text(), nullable=False),
        sa.Column(
            "decided_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "verdict IN ('APPROVE', 'REJECT')", name="ck_publication_approvals_verdict"
        ),
        sa.CheckConstraint(
            "snapshot_sha256 ~ '^[0-9a-f]{64}$'", name="ck_publication_approvals_snapshot_hash"
        ),
        sa.CheckConstraint(
            "btrim(justification) <> ''", name="ck_publication_approvals_justification_nonblank"
        ),
        sa.ForeignKeyConstraint(
            ["approver_account_id", "approver_person_id"],
            ["accounts.id", "accounts.person_id"],
            name="fk_publication_approvals_approver_person",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["version_id"],
            ["publication_versions.id"],
            name="fk_publication_approvals_version_id_publication_versions",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_publication_approvals"),
        sa.UniqueConstraint("version_id", name="uq_publication_approvals_version_id"),
    )

    op.drop_constraint("ck_state_transitions_resource_type", "state_transitions", type_="check")
    op.create_check_constraint(
        "ck_state_transitions_resource_type",
        "state_transitions",
        "resource_type IN ('CLIENT', 'TRACKING', 'NOVELTY', 'PUBLICATION_VERSION')",
    )
    op.drop_constraint(
        "ck_state_transitions_resource_type_matches_id",
        "state_transitions",
        type_="check",
    )
    op.create_check_constraint(
        "ck_state_transitions_resource_type_matches_id",
        "state_transitions",
        "(resource_type = 'CLIENT' AND client_id IS NOT NULL) OR "
        "(resource_type = 'TRACKING' AND tracking_id IS NOT NULL) OR "
        "(resource_type = 'NOVELTY' AND novelty_id IS NOT NULL) OR "
        "(resource_type = 'PUBLICATION_VERSION' AND version_id IS NOT NULL)",
    )
    op.create_foreign_key(
        "fk_state_transitions_version",
        "state_transitions",
        "publication_versions",
        ["version_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_state_transitions_version_occurred",
        "state_transitions",
        ["version_id", "occurred_at"],
        postgresql_where=sa.text("version_id IS NOT NULL"),
    )

    op.execute(
        """
        CREATE FUNCTION f6_reject_append_only_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION '% is append-only', TG_TABLE_NAME USING ERRCODE = '55000';
        END $$;
        """
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_publication_version() RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
            v_verdict varchar(8);
        BEGIN
            IF TG_OP = 'INSERT' THEN
                IF NEW.status <> 'DRAFT' OR NEW.frozen_at IS NOT NULL OR
                   NEW.approved_at IS NOT NULL OR NEW.published_at IS NOT NULL THEN
                    RAISE EXCEPTION 'publication versions begin as drafts' USING ERRCODE = '23514';
                END IF;
                RETURN NEW;
            END IF;

            IF OLD.status <> 'DRAFT' AND
               ROW(NEW.content_text, NEW.content_sha256, NEW.recipient_client_id,
                   NEW.recipient_tracking_id, NEW.publication_id, NEW.version_number, NEW.frozen_at)
               IS DISTINCT FROM
               ROW(OLD.content_text, OLD.content_sha256, OLD.recipient_client_id,
                   OLD.recipient_tracking_id, OLD.publication_id, OLD.version_number, OLD.frozen_at)
               THEN
                RAISE EXCEPTION 'submitted publication snapshot is immutable'
                    USING ERRCODE = '23514';
            END IF;
            IF OLD.status <> 'DRAFT' AND NEW.status = OLD.status AND NEW IS DISTINCT FROM OLD THEN
                RAISE EXCEPTION 'submitted version only changes through valid transition'
                    USING ERRCODE = '23514';
            END IF;
            IF OLD.status <> NEW.status AND NOT (
                (OLD.status = 'DRAFT' AND NEW.status = 'PENDING_APPROVAL') OR
                (OLD.status = 'PENDING_APPROVAL' AND NEW.status IN ('APPROVED', 'REJECTED')) OR
                (OLD.status = 'APPROVED' AND NEW.status = 'PUBLISHED')) THEN
                RAISE EXCEPTION 'invalid publication status transition' USING ERRCODE = '23514';
            END IF;
            IF NEW.status = 'PENDING_APPROVAL' AND
               (NEW.frozen_at IS NULL OR
                NOT EXISTS (SELECT 1 FROM publication_preparers WHERE version_id = NEW.id) OR
                NOT EXISTS (
                    SELECT 1 FROM publication_version_novelties WHERE version_id = NEW.id
                ) OR
                EXISTS (
                    SELECT 1
                    FROM publication_version_novelties pvn
                    JOIN novelties n ON n.id = pvn.novelty_id
                    WHERE pvn.version_id = NEW.id
                      AND (n.status <> 'TREATMENT_DEFINED' OR NOT EXISTS (
                          SELECT 1 FROM novelty_reviews nr
                          WHERE nr.novelty_id = n.id AND nr.review_kind = 'LEGAL'))
                )) THEN
                RAISE EXCEPTION 'submission requires reviewed novelty and preparer'
                    USING ERRCODE = '23514';
            END IF;
            IF NEW.status IN ('APPROVED', 'REJECTED') THEN
                SELECT verdict INTO v_verdict
                FROM publication_approvals WHERE version_id = NEW.id;
                IF v_verdict IS DISTINCT FROM (
                   CASE WHEN NEW.status = 'APPROVED' THEN 'APPROVE' ELSE 'REJECT' END) THEN
                    RAISE EXCEPTION 'status does not match recorded decision'
                        USING ERRCODE = '23514';
                END IF;
            END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_version_guard BEFORE INSERT OR UPDATE "
        "ON publication_versions FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_version()"
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_publication_components() RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
            v_version_id uuid;
            v_status varchar(24);
        BEGIN
            IF TG_OP = 'UPDATE' THEN
                RAISE EXCEPTION 'publication components are replaced only in a draft'
                    USING ERRCODE = '23514';
            END IF;
            v_version_id := CASE WHEN TG_OP = 'DELETE' THEN OLD.version_id ELSE NEW.version_id END;
            SELECT status INTO v_status
            FROM publication_versions WHERE id = v_version_id FOR UPDATE;
            IF v_status IS DISTINCT FROM 'DRAFT' THEN
                RAISE EXCEPTION 'cannot change submitted publication components'
                    USING ERRCODE = '23514';
            END IF;
            IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_preparers_components BEFORE INSERT OR UPDATE OR DELETE "
        "ON publication_preparers FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_components()"
    )
    op.execute(
        "CREATE TRIGGER tr_publication_version_novelties_components "
        "BEFORE INSERT OR UPDATE OR DELETE ON publication_version_novelties "
        "FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_components()"
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_publication_preparer() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM publication_versions pv
                JOIN account_roles ar
                  ON ar.account_id = NEW.account_id AND ar.role_code = 'PREPARER'
                JOIN internal_tracking_assignments ita
                  ON ita.account_id = NEW.account_id AND ita.tracking_id = pv.recipient_tracking_id
                 AND ita.revoked_at IS NULL
                WHERE pv.id = NEW.version_id AND pv.status = 'DRAFT'
            ) THEN
                RAISE EXCEPTION 'preparer must have an active assignment and role'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_preparer_role BEFORE INSERT ON publication_preparers "
        "FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_preparer()"
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_publication_novelty() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM novelties n
                JOIN novelty_reviews nr ON nr.novelty_id = n.id AND nr.review_kind = 'LEGAL'
                WHERE n.id = NEW.novelty_id AND n.tracking_id = NEW.tracking_id
                  AND n.status = 'TREATMENT_DEFINED'
            ) THEN
                RAISE EXCEPTION 'publication novelty requires human legal treatment'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_novelty_review "
        "BEFORE INSERT ON publication_version_novelties "
        "FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_novelty()"
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_publication_approval() RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
            v_status varchar(24);
            v_digest varchar(64);
            v_tracking_id uuid;
        BEGIN
            SELECT pv.status, pv.content_sha256, pv.recipient_tracking_id
              INTO v_status, v_digest, v_tracking_id
            FROM publication_versions pv WHERE pv.id = NEW.version_id FOR UPDATE;
            IF v_status IS DISTINCT FROM 'PENDING_APPROVAL' OR
               v_digest IS DISTINCT FROM NEW.snapshot_sha256 THEN
                RAISE EXCEPTION 'approval must target the frozen pending snapshot'
                    USING ERRCODE = '23514';
            END IF;
            IF EXISTS (
                SELECT 1 FROM publication_preparers
                WHERE version_id = NEW.version_id AND person_id = NEW.approver_person_id
            ) THEN
                RAISE EXCEPTION 'preparer cannot decide own version' USING ERRCODE = '23514';
            END IF;
            IF NOT EXISTS (
                SELECT 1 FROM account_roles ar
                JOIN internal_tracking_assignments ita ON ita.account_id = ar.account_id
                  AND ita.tracking_id = v_tracking_id AND ita.revoked_at IS NULL
                WHERE ar.account_id = NEW.approver_account_id AND ar.role_code = 'COORDINATOR'
            ) THEN
                RAISE EXCEPTION 'approver requires coordinator role and active assignment'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_approval_guard BEFORE INSERT ON publication_approvals "
        "FOR EACH ROW EXECUTE FUNCTION f6_guard_publication_approval()"
    )
    op.execute(
        "CREATE TRIGGER tr_publication_approvals_append_only BEFORE UPDATE OR DELETE "
        "ON publication_approvals FOR EACH ROW EXECUTE FUNCTION f6_reject_append_only_mutation()"
    )
    op.execute(
        """
        CREATE FUNCTION f6_guard_current_publication() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.current_version_id IS NOT NULL AND NOT EXISTS (
                SELECT 1 FROM publication_versions
                WHERE id = NEW.current_version_id
                  AND publication_id = NEW.id AND status = 'PUBLISHED'
            ) THEN
                RAISE EXCEPTION 'current publication pointer requires its published version'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        """
    )
    op.execute(
        "CREATE TRIGGER tr_publication_current_version_guard "
        "BEFORE INSERT OR UPDATE ON publications "
        "FOR EACH ROW EXECUTE FUNCTION f6_guard_current_publication()"
    )

    op.execute("GRANT SELECT, INSERT, UPDATE ON publications TO legaltech_runtime")
    op.execute("GRANT SELECT, INSERT, UPDATE ON publication_versions TO legaltech_runtime")
    op.execute("GRANT SELECT, INSERT ON publication_preparers TO legaltech_runtime")
    op.execute("GRANT SELECT, INSERT ON publication_version_novelties TO legaltech_runtime")
    op.execute("GRANT SELECT, INSERT ON publication_approvals TO legaltech_runtime")
    op.execute("REVOKE UPDATE, DELETE ON publication_approvals FROM legaltech_runtime")
    op.execute("GRANT SELECT, INSERT ON state_transitions TO legaltech_runtime")
    op.execute("REVOKE UPDATE, DELETE ON state_transitions FROM legaltech_runtime")


def downgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM state_transitions WHERE version_id IS NOT NULL) THEN
                RAISE EXCEPTION 'cannot downgrade while publication version transitions exist';
            END IF;
        END $$;
        """
    )
    op.execute("REVOKE ALL ON publication_approvals FROM legaltech_runtime")
    op.execute("REVOKE ALL ON publication_version_novelties FROM legaltech_runtime")
    op.execute("REVOKE ALL ON publication_preparers FROM legaltech_runtime")
    op.execute("REVOKE ALL ON publication_versions FROM legaltech_runtime")
    op.execute("REVOKE ALL ON publications FROM legaltech_runtime")

    op.execute("DROP TRIGGER tr_publication_current_version_guard ON publications")
    op.execute("DROP FUNCTION f6_guard_current_publication()")
    op.execute("DROP TRIGGER tr_publication_approvals_append_only ON publication_approvals")
    op.execute("DROP TRIGGER tr_publication_approval_guard ON publication_approvals")
    op.execute("DROP FUNCTION f6_guard_publication_approval()")
    op.execute("DROP TRIGGER tr_publication_novelty_review ON publication_version_novelties")
    op.execute("DROP FUNCTION f6_guard_publication_novelty()")
    op.execute("DROP TRIGGER tr_publication_preparer_role ON publication_preparers")
    op.execute("DROP FUNCTION f6_guard_publication_preparer()")
    op.execute(
        "DROP TRIGGER tr_publication_version_novelties_components ON publication_version_novelties"
    )
    op.execute("DROP TRIGGER tr_publication_preparers_components ON publication_preparers")
    op.execute("DROP FUNCTION f6_guard_publication_components()")
    op.execute("DROP TRIGGER tr_publication_version_guard ON publication_versions")
    op.execute("DROP FUNCTION f6_guard_publication_version()")
    op.execute("DROP FUNCTION f6_reject_append_only_mutation()")

    op.drop_index("ix_state_transitions_version_occurred", table_name="state_transitions")
    op.drop_constraint("fk_state_transitions_version", "state_transitions", type_="foreignkey")
    op.drop_constraint(
        "ck_state_transitions_resource_type_matches_id",
        "state_transitions",
        type_="check",
    )
    op.create_check_constraint(
        "ck_state_transitions_resource_type_matches_id",
        "state_transitions",
        "(resource_type = 'CLIENT' AND client_id IS NOT NULL) OR "
        "(resource_type = 'TRACKING' AND tracking_id IS NOT NULL) OR "
        "(resource_type = 'NOVELTY' AND novelty_id IS NOT NULL)",
    )
    op.drop_constraint("ck_state_transitions_resource_type", "state_transitions", type_="check")
    op.create_check_constraint(
        "ck_state_transitions_resource_type",
        "state_transitions",
        "resource_type IN ('CLIENT', 'TRACKING', 'NOVELTY')",
    )

    op.drop_table("publication_approvals")
    op.drop_index(
        "ix_publication_version_novelties_tracking", table_name="publication_version_novelties"
    )
    op.drop_table("publication_version_novelties")
    op.drop_table("publication_preparers")
    op.drop_constraint("fk_publications_current_version", "publications", type_="foreignkey")
    op.drop_index("ix_publication_versions_publication", table_name="publication_versions")
    op.drop_table("publication_versions")
    op.drop_index("ix_publications_tracking", table_name="publications")
    op.drop_table("publications")
