from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.identity.models import Account, AccountRole, Person
from app.trackings.models import JudicialProcess
from tests.conftest import TEST_ENGINE


def test_migration_is_current_and_identity_tables_exist() -> None:
    inspector = inspect(TEST_ENGINE)
    expected_tables = {
        "persons",
        "clients",
        "judicial_processes",
        "acquisition_runs",
        "observations",
        "observed_actions",
        "comparisons",
        "technical_changes",
        "tracking_evaluations",
        "novelties",
        "trackings",
        "external_tracking_scopes",
        "internal_tracking_assignments",
        "accounts",
        "account_roles",
        "auth_sessions",
        "audit_events",
    }
    table_names = set(inspector.get_table_names())
    assert expected_tables.issubset(table_names)
    with TEST_ENGINE.connect() as connection:
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
    assert revision == "0004_comparisons_and_novelties"


def test_comparison_and_novelty_constraints_exist() -> None:
    inspector = inspect(TEST_ENGINE)
    expected_unique_constraints = {
        "comparisons": {"uq_comparisons_pair_rule"},
        "technical_changes": {"uq_technical_changes_logical"},
        "tracking_evaluations": {"uq_tracking_evaluations_tracking_comparison"},
        "novelties": {"uq_novelties_tracking_change"},
    }
    for table, expected_names in expected_unique_constraints.items():
        actual_names = {
            constraint["name"] for constraint in inspector.get_unique_constraints(table)
        }
        assert expected_names.issubset(actual_names)


def test_acquisition_tables_and_sealing_triggers_exist() -> None:
    with TEST_ENGINE.connect() as connection:
        trigger_names = set(
            connection.scalars(
                text("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal AND tgname LIKE 'tr_%'")
            )
        )
    assert {
        "tr_acquisition_run_finalize",
        "tr_observation_accept",
        "tr_observations_seal",
        "tr_observed_action_insert",
        "tr_observed_actions_append_only",
        "tr_tracking_baseline_guard",
    }.issubset(trigger_names)


def test_runtime_database_role_has_dml_without_ddl_privileges() -> None:
    with TEST_ENGINE.connect() as connection:
        row = connection.execute(
            text(
                "SELECT current_user, "
                "has_schema_privilege(current_user, 'public', 'CREATE') AS can_create_schema, "
                "has_table_privilege(current_user, "
                "'public.accounts', 'SELECT') AS can_read_accounts, "
                "has_table_privilege(current_user, "
                "'public.audit_events', 'UPDATE') AS can_update_audit, "
                "has_table_privilege(current_user, "
                "'public.audit_events', 'DELETE') AS can_delete_audit"
            )
        ).one()
    assert row.current_user == "legaltech_runtime"
    assert row.can_create_schema is False
    assert row.can_read_accounts is True
    assert row.can_update_audit is False
    assert row.can_delete_audit is False


def test_database_rejects_external_account_without_client(db_session: Session) -> None:
    person = Person(id=uuid4(), display_name="Synthetic constraint person")
    db_session.add(person)
    db_session.flush()
    db_session.add(
        Account(
            id=uuid4(),
            person_id=person.id,
            username="reader.invalid",
            password_hash="$argon2id$synthetic-placeholder",
            account_kind="EXTERNAL",
            client_id=None,
            status="ACTIVE",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_database_rejects_role_that_does_not_match_account_kind(db_session: Session) -> None:
    person = Person(id=uuid4(), display_name="Synthetic role person")
    client = Client(
        id=uuid4(),
        client_code="synthetic-role-client",
        name="Synthetic role client",
        status="ACTIVE",
    )
    db_session.add_all([person, client])
    db_session.flush()
    account_id = uuid4()
    db_session.add(
        Account(
            id=account_id,
            person_id=person.id,
            username="internal.invalid",
            password_hash="$argon2id$synthetic-placeholder",
            account_kind="INTERNAL",
            client_id=None,
            status="ACTIVE",
        )
    )
    db_session.flush()
    db_session.add(
        AccountRole(
            account_id=account_id,
            account_kind="INTERNAL",
            role_code="EXTERNAL_READER",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_database_rejects_invalid_process_radicado(db_session: Session) -> None:
    db_session.add(JudicialProcess(id=uuid4(), radicado="1234567890123456789012", label=None))
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
