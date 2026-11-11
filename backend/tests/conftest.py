from __future__ import annotations

import os
import secrets
from collections.abc import Generator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.config import Settings
from app.db import create_database_engine, session_factory

_settings_from_env_file = Settings()
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = _settings_from_env_file.test_database()
os.environ["MIGRATION_DATABASE_URL"] = _settings_from_env_file.test_database(migration=True)
TEST_SETTINGS = Settings()
TEST_PASSWORD = secrets.token_urlsafe(24)
TEST_ENGINE = create_database_engine(TEST_SETTINGS)
TEST_MIGRATION_ENGINE = create_database_engine(TEST_SETTINGS, migration=True)
TEST_SESSION_FACTORY = session_factory(TEST_ENGINE)
TEST_MIGRATION_SESSION_FACTORY = session_factory(TEST_MIGRATION_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def apply_test_migrations() -> Generator[None, None, None]:
    command.upgrade(Config("alembic.ini"), "head")
    yield
    TEST_ENGINE.dispose()
    TEST_MIGRATION_ENGINE.dispose()


@pytest.fixture
def db_session(apply_test_migrations: None) -> Generator[Session, None, None]:
    with TEST_SESSION_FACTORY() as session:
        _clear_identity_data()
        yield session
        session.rollback()
        _clear_identity_data()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    from app.main import create_app

    app = create_app(TEST_SETTINGS)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


def _clear_identity_data() -> None:
    with TEST_MIGRATION_SESSION_FACTORY() as cleanup_session:
        cleanup_session.execute(
            text(
                "TRUNCATE TABLE observed_actions, observations, acquisition_runs, "
                "external_tracking_scopes, internal_tracking_assignments, trackings, "
                "judicial_processes, account_roles, auth_sessions, audit_events, "
                "accounts, clients, persons"
            )
        )
        cleanup_session.commit()
