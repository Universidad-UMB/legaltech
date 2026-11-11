from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.clients.models import Client
from app.config import Settings
from app.identity.models import Account, AccountRole, Person
from app.main import create_app
from app.trackings.models import InternalTrackingAssignment
from scripts.bootstrap_demo import (
    load_synthetic_identity_fixture,
    seed_demo,
    seed_fixture_identities,
)
from tests.conftest import TEST_SETTINGS
from tests.factories import create_account
from tests.test_clients_tracking_api import (
    PASSWORD,
    create_client,
    create_process,
    create_tracking,
    login,
)
from tests.traceability import trace_cases


@trace_cases("API-N31", "DT-34", "PROTO-AT-16")
def test_database_state_survives_fastapi_application_restart(
    db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    admin = create_account(db_session, username="admin.inc07-restart", password=PASSWORD)

    with TestClient(create_app(TEST_SETTINGS), raise_server_exceptions=False) as first_app:
        admin_headers = login(first_app, admin.username)
        client_record = create_client(
            first_app, admin_headers, "inc07-restart", "Cliente sintético de persistencia"
        )
        process_record = create_process(
            first_app,
            admin_headers,
            "00000000000000000000009",
            "Proceso sintético de persistencia",
        )
        tracking_record = create_tracking(
            first_app,
            admin_headers,
            client_id=UUID(client_record["id"]),
            process_id=UUID(process_record["id"]),
        )
        db_session.add(
            InternalTrackingAssignment(
                account_id=admin.id,
                account_kind="INTERNAL",
                tracking_id=UUID(tracking_record["id"]),
            )
        )
        db_session.commit()
        activated = first_app.post(
            f"/api/v1/internal/trackings/{tracking_record['id']}/activate",
            headers=admin_headers,
        )
        assert activated.status_code == 200, activated.text

    with TestClient(create_app(TEST_SETTINGS), raise_server_exceptions=False) as restarted_app:
        assert restarted_app.get("/api/v1/auth/me", headers=admin_headers).status_code == 200
        process_read = restarted_app.get(
            f"/api/v1/internal/processes/{process_record['id']}", headers=admin_headers
        )
        tracking_read = restarted_app.get(
            f"/api/v1/internal/trackings/{tracking_record['id']}", headers=admin_headers
        )
        assert process_read.status_code == 200, process_read.text
        assert tracking_read.status_code == 200, tracking_read.text
        assert tracking_read.json()["status"] == "ACTIVE"


@trace_cases("DT-35", "PROTO-AT-16")
def test_synthetic_identity_seed_is_idempotent_and_survives_app_restart(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    password = "Synthetic-Demo-Seed-Password-2026!"
    fixture = load_synthetic_identity_fixture()

    with db_session.begin():
        first_counts = seed_fixture_identities(db_session, fixture, password)

    first_login = client.post(
        "/api/v1/auth/sessions", json={"username": "admin.demo", "password": password}
    )
    assert first_login.status_code == 201, first_login.text
    first_headers = {"Authorization": f"Bearer {first_login.json()['access_token']}"}

    with db_session.begin():
        second_counts = seed_fixture_identities(db_session, fixture, password)

    assert second_counts == first_counts
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Person)) == first_counts[0]
    assert db_session.scalar(select(func.count()).select_from(Client)) == first_counts[1]
    assert db_session.scalar(select(func.count()).select_from(Account)) == first_counts[2]
    assert db_session.scalar(select(func.count()).select_from(AccountRole)) == first_counts[3]
    assert client.get("/api/v1/auth/me", headers=first_headers).status_code == 401

    second_login = client.post(
        "/api/v1/auth/sessions", json={"username": "admin.demo", "password": password}
    )
    assert second_login.status_code == 201, second_login.text
    second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
    with TestClient(create_app(TEST_SETTINGS), raise_server_exceptions=False) as restarted_app:
        principal = restarted_app.get("/api/v1/auth/me", headers=second_headers)
        assert principal.status_code == 200, principal.text
        assert principal.json()["account_kind"] == "INTERNAL"
        assert "ADMIN" in principal.json()["roles"]


def test_demo_bootstrap_rejects_the_test_database_without_mutating_it() -> None:
    settings = Settings(
        app_env="local",
        database_url=(
            "postgresql+psycopg://legaltech_runtime:local@127.0.0.1:55432/legaltech_test"
        ),
    )

    with pytest.raises(SystemExit, match="isolated local legaltech_demo"):
        seed_demo(settings, "Synthetic-Demo-Seed-Password-2026!")


@trace_cases("API-N30")
def test_disallowed_origin_receives_no_cors_permission(
    client: TestClient, _requirement_ids: tuple[str, ...]
) -> None:
    response = client.get("/healthz", headers={"Origin": "https://untrusted.example"})

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


@trace_cases("API-N26", "API-N32")
@pytest.mark.parametrize(
    "secret",
    (
        "synthetic-password-never-log",
        "synthetic-token-never-log",
        "synthetic-publication-content-never-log",
    ),
)
def test_unhandled_errors_do_not_log_or_return_exception_content(
    client: TestClient, caplog: Any, secret: str, _requirement_ids: tuple[str, ...]
) -> None:
    def raise_synthetic_error() -> None:
        raise RuntimeError(secret)

    client.app.add_api_route("/_test/sanitized-error", raise_synthetic_error, methods=["GET"])
    caplog.set_level(logging.ERROR, logger="legaltech.api")
    response = client.get("/_test/sanitized-error")

    assert response.status_code == 500
    assert secret not in response.text
    assert secret not in caplog.text
    assert "Unhandled request failure" in caplog.text
