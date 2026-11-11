from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings
from scripts.reset_demo import (
    DEMO_ALEMBIC_HEAD,
    reset_demo_database,
    truncate_demo_tables,
    validate_reset_request,
)
from tests.conftest import TEST_MIGRATION_ENGINE
from tests.traceability import trace_cases


@trace_cases("PROTO-AT-16")
def test_demo_reset_requires_local_environment_exact_database_and_confirmation(
    _requirement_ids: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="APP_ENV=local"):
        validate_reset_request(
            Settings(
                app_env="test",
                migration_database_url=(
                    "postgresql+psycopg://legaltech_migrator:local@127.0.0.1:55432/legaltech_demo"
                ),
            ),
            "legaltech_demo",
        )

    with pytest.raises(ValueError, match="legaltech_demo"):
        validate_reset_request(
            Settings(
                app_env="local",
                migration_database_url=(
                    "postgresql+psycopg://legaltech_migrator:local@127.0.0.1:55432/legaltech_test"
                ),
            ),
            "legaltech_demo",
        )

    with pytest.raises(ValueError, match="--confirm legaltech_demo"):
        validate_reset_request(
            Settings(
                app_env="local",
                migration_database_url=(
                    "postgresql+psycopg://legaltech_migrator:local@127.0.0.1:55432/legaltech_demo"
                ),
            ),
            "",
        )


@trace_cases("PROTO-AT-16")
def test_demo_reset_truncation_is_scoped_and_preserves_alembic_revision(
    db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    with TEST_MIGRATION_ENGINE.connect() as connection:
        transaction = connection.begin()
        try:
            before = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            assert before == DEMO_ALEMBIC_HEAD
            connection.execute(
                text(
                    "INSERT INTO clients (id, client_code, name, status) "
                    "VALUES (:id, 'reset-probe', 'Synthetic reset probe', 'ACTIVE')"
                ),
                {"id": uuid4()},
            )
            assert (
                connection.execute(
                    text("SELECT count(*) FROM clients WHERE client_code = 'reset-probe'")
                ).scalar_one()
                == 1
            )

            truncate_demo_tables(connection)

            assert (
                connection.execute(
                    text("SELECT count(*) FROM clients WHERE client_code = 'reset-probe'")
                ).scalar_one()
                == 0
            )
            after = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            assert after == before
        finally:
            transaction.rollback()

    # The fixture clears only legaltech_test before and after this rollback-only check.
    assert db_session.is_active


@trace_cases("PROTO-AT-16")
def test_reset_executor_refuses_the_test_database_without_mutating_it(
    db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    with pytest.raises(ValueError, match="legaltech_demo"):
        reset_demo_database(TEST_MIGRATION_ENGINE)
    assert db_session.is_active
