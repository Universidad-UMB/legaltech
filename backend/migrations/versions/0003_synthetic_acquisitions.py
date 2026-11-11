"""Persist synthetic acquisition runs and sealed observations.

Revision ID: 0003_synthetic_acquisitions
Revises: 0002_clients_processes_trackings
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_synthetic_acquisitions"
down_revision: str | None = "0002_clients_processes_trackings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "acquisition_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "source_code",
            sa.String(length=32),
            server_default=sa.text("'DEMO-FIXTURE'"),
            nullable=False,
        ),
        sa.Column("fixture_code", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=12), nullable=False),
        sa.Column("request_key", sa.String(length=100), nullable=False),
        sa.Column("request_payload_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "requested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("coverage_note", sa.Text(), nullable=True),
        sa.CheckConstraint("source_code = 'DEMO-FIXTURE'", name="ck_acquisition_runs_source_code"),
        sa.CheckConstraint(
            "fixture_code IN ('OBS_001', 'OBS_002', 'FAILED', 'INCOMPLETE')",
            name="ck_acquisition_runs_fixture_code",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'SUCCESS', 'INCOMPLETE', 'FAILED')",
            name="ck_acquisition_runs_status",
        ),
        sa.CheckConstraint(
            "(status = 'PENDING' AND finished_at IS NULL) "
            "OR (status <> 'PENDING' AND finished_at IS NOT NULL)",
            name="ck_acquisition_runs_finish_state",
        ),
        sa.CheckConstraint(
            "status <> 'FAILED' OR error_code IS NOT NULL",
            name="ck_acquisition_runs_failed_error",
        ),
        sa.CheckConstraint(
            "request_payload_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_acquisition_runs_payload_sha256",
        ),
        sa.ForeignKeyConstraint(
            ["process_id"],
            ["judicial_processes.id"],
            name="fk_acquisition_runs_process_id_judicial_processes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_acquisition_runs"),
        sa.UniqueConstraint("id", "process_id", name="uq_acquisition_runs_id_process_id"),
        sa.UniqueConstraint("request_key", name="uq_acquisition_runs_request_key"),
    )
    op.create_index(
        "ix_acquisition_process_requested",
        "acquisition_runs",
        ["process_id", sa.text("requested_at DESC")],
    )
    op.create_table(
        "observations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("acquisition_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quality", sa.String(length=16), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("sealed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("payload_sha256", sa.String(length=64), nullable=False),
        sa.Column(
            "provenance",
            sa.String(length=80),
            server_default=sa.text("'DEMO-FIXTURE'"),
            nullable=False,
        ),
        sa.Column("coverage_note", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "quality IN ('COMPARABLE', 'INCOMPLETE', 'INDETERMINATE')",
            name="ck_observations_quality",
        ),
        sa.CheckConstraint(
            "payload_sha256 ~ '^[0-9a-f]{64}$'", name="ck_observations_payload_sha256"
        ),
        sa.CheckConstraint("provenance = 'DEMO-FIXTURE'", name="ck_observations_provenance"),
        sa.CheckConstraint(
            "received_at >= observed_at", name="ck_observations_received_after_observed"
        ),
        sa.CheckConstraint(
            "sealed_at IS NULL OR sealed_at >= received_at",
            name="ck_observations_seal_after_received",
        ),
        sa.ForeignKeyConstraint(
            ["process_id"],
            ["judicial_processes.id"],
            name="fk_observations_process_id_judicial_processes",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["acquisition_run_id", "process_id"],
            ["acquisition_runs.id", "acquisition_runs.process_id"],
            name="fk_observations_acquisition_process",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_observations"),
        sa.UniqueConstraint("acquisition_run_id", name="uq_observations_acquisition_run_id"),
        sa.UniqueConstraint("id", "process_id", name="uq_observations_id_process_id"),
    )
    op.create_index(
        "ix_observations_process_observed",
        "observations",
        ["process_id", sa.text("observed_at DESC")],
    )
    op.create_table(
        "observed_actions",
        sa.Column("observation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_key", sa.String(length=64), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("occurred_on", sa.Date(), nullable=True),
        sa.CheckConstraint(
            "action_key ~ '^ACT-[0-9]{2,}$'", name="ck_observed_actions_action_key_format"
        ),
        sa.CheckConstraint(
            "btrim(description) <> ''", name="ck_observed_actions_description_nonblank"
        ),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'", name="ck_observed_actions_content_sha256"
        ),
        sa.ForeignKeyConstraint(
            ["observation_id"],
            ["observations.id"],
            name="fk_observed_actions_observation",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("observation_id", "action_key", name="pk_observed_actions"),
    )

    op.create_foreign_key(
        "fk_trackings_baseline_observation_process",
        "trackings",
        "observations",
        ["baseline_observation_id", "process_id"],
        ["id", "process_id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_trackings_last_adopted_observation_process",
        "trackings",
        "observations",
        ["last_adopted_observation_id", "process_id"],
        ["id", "process_id"],
        ondelete="RESTRICT",
    )

    op.execute(
        """
        CREATE FUNCTION legaltech_guard_acquisition_run() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'acquisition evidence cannot be deleted' USING ERRCODE = '23514';
            END IF;
            IF OLD.status <> 'PENDING' OR NEW.status = 'PENDING'
               OR ROW(NEW.id, NEW.process_id, NEW.source_code, NEW.fixture_code,
                      NEW.request_key, NEW.request_payload_sha256, NEW.requested_at)
                  IS DISTINCT FROM
                  ROW(OLD.id, OLD.process_id, OLD.source_code, OLD.fixture_code,
                      OLD.request_key, OLD.request_payload_sha256, OLD.requested_at) THEN
                RAISE EXCEPTION 'acquisition may only be finalized once' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_acquisition_run_finalize
            BEFORE UPDATE OR DELETE ON acquisition_runs
            FOR EACH ROW EXECUTE FUNCTION legaltech_guard_acquisition_run();

        CREATE FUNCTION legaltech_guard_observation_insert() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE v_status varchar(12);
        BEGIN
            SELECT status INTO v_status FROM acquisition_runs
            WHERE id = NEW.acquisition_run_id AND process_id = NEW.process_id FOR UPDATE;
            IF v_status IS NULL OR v_status NOT IN ('SUCCESS', 'INCOMPLETE')
               OR (v_status = 'INCOMPLETE' AND NEW.quality = 'COMPARABLE') THEN
                RAISE EXCEPTION 'observation requires a compatible finalized acquisition'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_observation_accept
            BEFORE INSERT ON observations
            FOR EACH ROW EXECUTE FUNCTION legaltech_guard_observation_insert();

        CREATE FUNCTION legaltech_guard_observation_seal() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                RAISE EXCEPTION 'observation snapshot cannot be deleted' USING ERRCODE = '23514';
            END IF;
            IF OLD.sealed_at IS NOT NULL OR NEW.sealed_at IS NULL
               OR ROW(NEW.id, NEW.process_id, NEW.acquisition_run_id, NEW.quality,
                      NEW.observed_at, NEW.received_at, NEW.payload_sha256,
                      NEW.provenance, NEW.coverage_note)
                  IS DISTINCT FROM
                  ROW(OLD.id, OLD.process_id, OLD.acquisition_run_id, OLD.quality,
                      OLD.observed_at, OLD.received_at, OLD.payload_sha256,
                      OLD.provenance, OLD.coverage_note) THEN
                RAISE EXCEPTION 'observation may only transition from unsealed to sealed'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_observations_seal
            BEFORE UPDATE OR DELETE ON observations
            FOR EACH ROW EXECUTE FUNCTION legaltech_guard_observation_seal();

        CREATE FUNCTION legaltech_guard_observed_action_insert() RETURNS trigger
            LANGUAGE plpgsql AS $$
        DECLARE v_sealed_at timestamptz;
        BEGIN
            SELECT sealed_at INTO v_sealed_at FROM observations
            WHERE id = NEW.observation_id FOR UPDATE;
            IF NOT FOUND OR v_sealed_at IS NOT NULL THEN
                RAISE EXCEPTION 'cannot append an action to a sealed snapshot'
                    USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_observed_action_insert
            BEFORE INSERT ON observed_actions
            FOR EACH ROW EXECUTE FUNCTION legaltech_guard_observed_action_insert();

        CREATE FUNCTION legaltech_reject_observed_action_mutation() RETURNS trigger
            LANGUAGE plpgsql AS $$
        BEGIN
            RAISE EXCEPTION 'observed actions are append-only' USING ERRCODE = '23514';
        END $$;
        CREATE TRIGGER tr_observed_actions_append_only
            BEFORE UPDATE OR DELETE ON observed_actions
            FOR EACH ROW EXECUTE FUNCTION legaltech_reject_observed_action_mutation();

        CREATE FUNCTION legaltech_guard_tracking_baseline() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE
            v_baseline_quality varchar(16);
            v_last_quality varchar(16);
            v_baseline_sealed timestamptz;
            v_last_sealed timestamptz;
            v_baseline_time timestamptz;
            v_last_time timestamptz;
        BEGIN
            IF TG_OP = 'UPDATE' AND OLD.baseline_observation_id IS NOT NULL
               AND NEW.baseline_observation_id IS DISTINCT FROM OLD.baseline_observation_id THEN
                RAISE EXCEPTION 'first baseline is immutable' USING ERRCODE = '23514';
            END IF;
            IF NEW.baseline_observation_id IS NOT NULL THEN
                SELECT quality, sealed_at, observed_at
                INTO v_baseline_quality, v_baseline_sealed, v_baseline_time
                FROM observations WHERE id = NEW.baseline_observation_id;
                SELECT quality, sealed_at, observed_at
                INTO v_last_quality, v_last_sealed, v_last_time
                FROM observations WHERE id = NEW.last_adopted_observation_id;
                IF v_baseline_quality IS DISTINCT FROM 'COMPARABLE'
                   OR v_last_quality IS DISTINCT FROM 'COMPARABLE'
                   OR v_baseline_sealed IS NULL OR v_last_sealed IS NULL
                   OR v_last_time < v_baseline_time THEN
                    RAISE EXCEPTION 'tracking baseline observations must be sealed, comparable'
                        USING ERRCODE = '23514';
                END IF;
                IF TG_OP = 'UPDATE' AND OLD.last_adopted_observation_id IS NOT NULL
                   AND NEW.last_adopted_observation_id
                       IS DISTINCT FROM OLD.last_adopted_observation_id
                   AND EXISTS (
                       SELECT 1 FROM observations old_ob
                       WHERE old_ob.id = OLD.last_adopted_observation_id
                         AND old_ob.observed_at >= v_last_time
                   ) THEN
                    RAISE EXCEPTION 'tracking observation cursor cannot move backwards'
                        USING ERRCODE = '23514';
                END IF;
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER tr_tracking_baseline_guard
            BEFORE INSERT OR UPDATE ON trackings
            FOR EACH ROW EXECUTE FUNCTION legaltech_guard_tracking_baseline();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER tr_tracking_baseline_guard ON trackings")
    op.execute("DROP FUNCTION legaltech_guard_tracking_baseline()")
    op.execute("DROP TRIGGER tr_observed_actions_append_only ON observed_actions")
    op.execute("DROP FUNCTION legaltech_reject_observed_action_mutation()")
    op.execute("DROP TRIGGER tr_observed_action_insert ON observed_actions")
    op.execute("DROP FUNCTION legaltech_guard_observed_action_insert()")
    op.execute("DROP TRIGGER tr_observations_seal ON observations")
    op.execute("DROP FUNCTION legaltech_guard_observation_seal()")
    op.execute("DROP TRIGGER tr_observation_accept ON observations")
    op.execute("DROP FUNCTION legaltech_guard_observation_insert()")
    op.execute("DROP TRIGGER tr_acquisition_run_finalize ON acquisition_runs")
    op.execute("DROP FUNCTION legaltech_guard_acquisition_run()")
    op.drop_constraint(
        "fk_trackings_last_adopted_observation_process", "trackings", type_="foreignkey"
    )
    op.drop_constraint("fk_trackings_baseline_observation_process", "trackings", type_="foreignkey")
    op.drop_table("observed_actions")
    op.drop_index("ix_observations_process_observed", table_name="observations")
    op.drop_table("observations")
    op.drop_index("ix_acquisition_process_requested", table_name="acquisition_runs")
    op.drop_table("acquisition_runs")
