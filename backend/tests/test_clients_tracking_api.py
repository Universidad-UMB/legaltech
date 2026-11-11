from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier
from typing import cast
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.clients.models import Client
from app.core.errors import ResourceConflict
from app.identity.domain import Principal
from app.identity.models import Account, AuditEvent
from app.trackings.models import (
    ExternalTrackingScope,
    InternalTrackingAssignment,
    JudicialProcess,
    Tracking,
)
from app.trackings.service import TrackingService
from scripts.seed_authorization_context import load_fixture, seed_authorization_context
from tests.conftest import TEST_ENGINE, TEST_SESSION_FACTORY
from tests.factories import create_account

INTERNAL_API = "/api/v1/internal"
PASSWORD = "Synthetic-test-password-01!"


def login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/sessions",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_client(client: TestClient, headers: dict[str, str], code: str, name: str) -> dict:
    response = client.post(
        f"{INTERNAL_API}/clients",
        headers=headers,
        json={"client_code": code, "name": name},
    )
    assert response.status_code == 201, response.text
    assert response.headers["location"] == f"{INTERNAL_API}/clients/{response.json()['id']}"
    assert response.headers["content-type"].startswith("application/json")
    return response.json()


def create_process(
    client: TestClient, headers: dict[str, str], radicado: str, label: str | None = None
) -> dict:
    payload: dict[str, str] = {"radicado": radicado}
    if label is not None:
        payload["label"] = label
    response = client.post(f"{INTERNAL_API}/processes", headers=headers, json=payload)
    assert response.status_code == 201, response.text
    assert response.headers["location"] == f"{INTERNAL_API}/processes/{response.json()['id']}"
    return response.json()


def create_tracking(
    client: TestClient,
    headers: dict[str, str],
    client_id: UUID,
    process_id: UUID,
) -> dict:
    response = client.post(
        f"{INTERNAL_API}/trackings",
        headers=headers,
        json={"client_id": str(client_id), "process_id": str(process_id)},
    )
    assert response.status_code == 201, response.text
    assert response.headers["location"] == f"{INTERNAL_API}/trackings/{response.json()['id']}"
    return response.json()


def fixture_records(fixture: dict[str, object], field: str) -> list[dict[str, object]]:
    value = fixture[field]
    assert isinstance(value, list)
    return cast(list[dict[str, object]], value)


def fixture_string(record: dict[str, object], field: str) -> str:
    value = record[field]
    assert isinstance(value, str)
    return value


def test_inc01_acceptance_process_tracking_scope_and_activation(
    client: TestClient, db_session: Session
) -> None:
    admin = create_account(db_session, username="admin.inc01", password=PASSWORD)
    headers = login(client, "admin.inc01")

    alfa = create_client(client, headers, "alfa", "Cliente ficticio Alfa")
    beta = create_client(client, headers, "beta", "Cliente ficticio Beta")
    duplicate_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=headers,
        json={"client_code": "alfa", "name": "Second synthetic Alfa"},
    )
    assert duplicate_client.status_code == 409
    process_1 = create_process(client, headers, "00000000000000000000001", "Proceso ficticio 1")
    process_2 = create_process(client, headers, "00000000000000000000002", "Proceso ficticio 2")

    tracking_a1 = create_tracking(client, headers, UUID(alfa["id"]), UUID(process_1["id"]))
    tracking_b1 = create_tracking(client, headers, UUID(beta["id"]), UUID(process_1["id"]))
    tracking_a2 = create_tracking(client, headers, UUID(alfa["id"]), UUID(process_2["id"]))

    assert tracking_a1["tracking_code"] == "SEG-A-001"
    assert tracking_b1["tracking_code"] == "SEG-B-001"
    assert tracking_a2["tracking_code"] == "SEG-A-002"
    assert tracking_a1["process_id"] == tracking_b1["process_id"] == process_1["id"]
    assert tracking_a1["client_id"] == alfa["id"]
    assert tracking_b1["client_id"] == beta["id"]
    assert tracking_a2["process_id"] == process_2["id"]
    assert tracking_a1["status"] == "PENDING"
    assert tracking_a1["baseline_observation_id"] is None
    assert tracking_a1["last_adopted_observation_id"] is None

    extra_tracking_field = client.post(
        f"{INTERNAL_API}/trackings",
        headers=headers,
        json={
            "client_id": alfa["id"],
            "process_id": process_2["id"],
            "actor_id": str(admin.id),
        },
    )
    assert extra_tracking_field.status_code == 422

    duplicate = client.post(
        f"{INTERNAL_API}/trackings",
        headers=headers,
        json={"client_id": alfa["id"], "process_id": process_1["id"]},
    )
    assert duplicate.status_code == 409
    assert duplicate.headers["content-type"].startswith("application/problem+json")
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(Tracking)
            .where(
                Tracking.client_id == UUID(alfa["id"]),
                Tracking.process_id == UUID(process_1["id"]),
            )
        )
        == 1
    )

    tracking_a1_url = f"{INTERNAL_API}/trackings/{tracking_a1['id']}"
    client_a_url = f"{INTERNAL_API}/clients/{alfa['id']}"
    process_1_url = f"{INTERNAL_API}/processes/{process_1['id']}"
    assert client.get(tracking_a1_url, headers=headers).status_code == 404
    assert client.get(client_a_url, headers=headers).status_code == 404
    assert client.get(process_1_url, headers=headers).status_code == 404
    assert client.post(f"{tracking_a1_url}/activate", headers=headers).status_code == 404

    db_session.add(
        InternalTrackingAssignment(
            account_id=admin.id,
            account_kind="INTERNAL",
            tracking_id=UUID(tracking_a1["id"]),
        )
    )
    db_session.commit()

    assert client.get(tracking_a1_url, headers=headers).json()["tracking_code"] == "SEG-A-001"
    assert client.get(client_a_url, headers=headers).json()["client_code"] == "alfa"
    assert client.get(process_1_url, headers=headers).json()["radicado"] == process_1["radicado"]
    assert (
        client.get(f"{INTERNAL_API}/trackings/{tracking_b1['id']}", headers=headers).status_code
        == 404
    )
    assert client.get(f"{INTERNAL_API}/clients/{beta['id']}", headers=headers).status_code == 404
    assert (
        client.get(f"{INTERNAL_API}/processes/{process_2['id']}", headers=headers).status_code
        == 404
    )

    activated = client.post(f"{tracking_a1_url}/activate", headers=headers)
    assert activated.status_code == 200
    assert activated.json()["status"] == "ACTIVE"
    assert client.post(f"{tracking_a1_url}/activate", headers=headers).status_code == 409

    db_session.execute(
        update(Tracking).where(Tracking.id == UUID(tracking_a2["id"])).values(status="FINISHED")
    )
    db_session.commit()
    reopened = create_tracking(client, headers, UUID(alfa["id"]), UUID(process_2["id"]))
    assert reopened["tracking_code"] == "SEG-A-003"

    with TEST_ENGINE.connect() as connection:
        audit_codes = set(
            connection.scalars(
                select(AuditEvent.event_code).where(
                    AuditEvent.actor_account_id == admin.id,
                    AuditEvent.event_code.in_(
                        {
                            "CLIENT_CREATE",
                            "PROCESS_CREATE",
                            "TRACKING_CREATE",
                            "TRACKING_ACTIVATE",
                        }
                    ),
                )
            )
        )
        denied_access_events = connection.execute(
            select(
                AuditEvent.event_code,
                AuditEvent.resource_id,
                AuditEvent.sanitized_reason,
            ).where(
                AuditEvent.actor_account_id == admin.id,
                AuditEvent.result == "DENIED",
            )
        ).all()
    assert audit_codes == {
        "CLIENT_CREATE",
        "PROCESS_CREATE",
        "TRACKING_CREATE",
        "TRACKING_ACTIVATE",
    }
    assert any(event.event_code == "TRACKING_READ" for event in denied_access_events)
    assert all(event.resource_id is None for event in denied_access_events)
    assert all(event.sanitized_reason == "resource_not_in_scope" for event in denied_access_events)


@pytest.mark.parametrize("radicado", ["1" * 22, "1" * 24, "1" * 22 + "A"])
def test_create_process_rejects_invalid_radicado(
    client: TestClient, db_session: Session, radicado: str
) -> None:
    create_account(db_session, username="admin.invalid-radicado", password=PASSWORD)
    headers = login(client, "admin.invalid-radicado")
    response = client.post(
        f"{INTERNAL_API}/processes",
        headers=headers,
        json={"radicado": radicado},
    )
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "radicado" not in response.text


def test_create_process_duplicate_is_conflict_and_extra_fields_are_rejected(
    client: TestClient, db_session: Session
) -> None:
    create_account(db_session, username="admin.process-conflict", password=PASSWORD)
    headers = login(client, "admin.process-conflict")
    create_process(client, headers, "00000000000000000000001")

    duplicate = client.post(
        f"{INTERNAL_API}/processes",
        headers=headers,
        json={"radicado": "00000000000000000000001"},
    )
    assert duplicate.status_code == 409
    extra_field = client.post(
        f"{INTERNAL_API}/processes",
        headers=headers,
        json={"radicado": "00000000000000000000002", "client_id": str(uuid4())},
    )
    assert extra_field.status_code == 422


def test_internal_writes_require_admin_and_external_accounts_cannot_use_internal_api(
    client: TestClient, db_session: Session
) -> None:
    create_account(
        db_session,
        username="analyst.inc01",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    analyst_headers = login(client, "analyst.inc01")
    external = create_account(
        db_session,
        username="reader.inc01",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
    )
    external_headers = login(client, "reader.inc01")

    client_body = {"client_code": "new-client", "name": "Synthetic client"}
    process_body = {"radicado": "00000000000000000000001"}
    tracking_body = {"client_id": str(uuid4()), "process_id": str(uuid4())}
    for headers in (analyst_headers, external_headers):
        client_response = client.post(f"{INTERNAL_API}/clients", headers=headers, json=client_body)
        process_response = client.post(
            f"{INTERNAL_API}/processes", headers=headers, json=process_body
        )
        tracking_response = client.post(
            f"{INTERNAL_API}/trackings", headers=headers, json=tracking_body
        )
        assert client_response.status_code == 403
        assert process_response.status_code == 403
        assert tracking_response.status_code == 403

    external_read = client.get(f"{INTERNAL_API}/clients/{uuid4()}", headers=external_headers)
    assert external_read.status_code == 403
    assert external_read.headers["content-type"].startswith("application/problem+json")
    with TEST_ENGINE.connect() as connection:
        denied_writes = connection.execute(
            select(AuditEvent.event_code).where(
                AuditEvent.actor_account_id == external.id,
                AuditEvent.result == "DENIED",
            )
        ).scalars()
    assert set(denied_writes) == {
        "CLIENT_CREATE",
        "PROCESS_CREATE",
        "TRACKING_CREATE",
        "CLIENT_READ",
    }


def test_composite_foreign_keys_reject_cross_client_scopes_and_external_assignments(
    db_session: Session,
) -> None:
    alfa = Client(
        id=uuid4(),
        client_code="scope-alfa",
        name="Synthetic Alfa",
        status="ACTIVE",
    )
    beta = Client(
        id=uuid4(),
        client_code="scope-beta",
        name="Synthetic Beta",
        status="ACTIVE",
    )
    process = JudicialProcess(
        id=uuid4(),
        radicado="00000000000000000000001",
        label="Synthetic process",
    )
    tracking_a = Tracking(
        id=uuid4(),
        tracking_code="SEG-SCOPE-A-001",
        client_id=alfa.id,
        process_id=process.id,
        status="PENDING",
    )
    tracking_b = Tracking(
        id=uuid4(),
        tracking_code="SEG-SCOPE-B-001",
        client_id=beta.id,
        process_id=process.id,
        status="PENDING",
    )
    db_session.add_all([alfa, beta, process, tracking_a, tracking_b])
    db_session.commit()
    external = create_account(
        db_session,
        username="scope.reader",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=alfa.id,
    )
    internal = create_account(
        db_session,
        username="scope.admin",
        password=PASSWORD,
        roles=("ADMIN",),
    )

    db_session.add(
        ExternalTrackingScope(
            account_id=external.id,
            account_kind="EXTERNAL",
            client_id=alfa.id,
            tracking_id=tracking_b.id,
            permission_code="READ_PUBLICATIONS",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    db_session.add(
        ExternalTrackingScope(
            account_id=external.id,
            account_kind="EXTERNAL",
            client_id=beta.id,
            tracking_id=tracking_b.id,
            permission_code="READ_PUBLICATIONS",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    db_session.add(
        ExternalTrackingScope(
            account_id=internal.id,
            account_kind="INTERNAL",
            client_id=alfa.id,
            tracking_id=tracking_a.id,
            permission_code="READ_PUBLICATIONS",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    valid_scope = ExternalTrackingScope(
        account_id=external.id,
        account_kind="EXTERNAL",
        client_id=alfa.id,
        tracking_id=tracking_a.id,
        permission_code="READ_PUBLICATIONS",
    )
    db_session.add(valid_scope)
    db_session.commit()
    with pytest.raises(IntegrityError):
        db_session.execute(
            insert(ExternalTrackingScope).values(
                account_id=external.id,
                account_kind="EXTERNAL",
                client_id=alfa.id,
                tracking_id=tracking_a.id,
                permission_code="READ_PUBLICATIONS",
            )
        )
    db_session.rollback()

    db_session.add(
        InternalTrackingAssignment(
            account_id=external.id,
            account_kind="EXTERNAL",
            tracking_id=tracking_a.id,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_local_fixture_seeding_is_idempotent_and_preserves_revoked_assignments(
    db_session: Session,
) -> None:
    fixture = load_fixture()
    client_rows = fixture_records(fixture, "clients")
    process_rows = fixture_records(fixture, "processes")
    tracking_rows = fixture_records(fixture, "trackings")
    account_rows = fixture_records(fixture, "accounts")

    clients: dict[str, Client] = {}
    for row in client_rows:
        alias = fixture_string(row, "alias")
        client = Client(
            id=uuid4(),
            client_code=fixture_string(row, "client_code"),
            name=fixture_string(row, "name"),
            status=fixture_string(row, "status"),
        )
        clients[alias] = client
        db_session.add(client)

    processes: dict[str, JudicialProcess] = {}
    for row in process_rows:
        alias = fixture_string(row, "alias")
        process = JudicialProcess(
            id=uuid4(),
            radicado=fixture_string(row, "radicado"),
            label=None,
        )
        processes[alias] = process
        db_session.add(process)

    trackings: dict[str, Tracking] = {}
    for row in tracking_rows:
        alias = fixture_string(row, "alias")
        tracking = Tracking(
            id=uuid4(),
            tracking_code=alias,
            client_id=clients[fixture_string(row, "client")].id,
            process_id=processes[fixture_string(row, "process")].id,
            status="PENDING",
        )
        trackings[alias] = tracking
        db_session.add(tracking)
    db_session.commit()

    accounts: dict[str, Account] = {}
    for row in account_rows:
        username = fixture_string(row, "username")
        kind = fixture_string(row, "kind")
        client_ref = row.get("client_ref")
        roles_value = row["roles"]
        assert isinstance(roles_value, list)
        roles = tuple(cast(list[str], roles_value))
        account = create_account(
            db_session,
            username=username,
            password=PASSWORD,
            roles=roles,
            account_kind=kind,
            client_id=clients[cast(str, client_ref)].id if client_ref is not None else None,
        )
        accounts[username] = account

    db_session.rollback()
    with db_session.begin():
        first_counts = seed_authorization_context(db_session, fixture)
    with db_session.begin():
        repeated_counts = seed_authorization_context(db_session, fixture)

    assert first_counts == (9, 2)
    assert repeated_counts == (0, 0)
    assignment = db_session.get(
        InternalTrackingAssignment,
        (accounts["admin.demo"].id, trackings["SEG-A-001"].id),
    )
    assert assignment is not None
    assignment.revoked_at = datetime.now(UTC)
    db_session.commit()

    with db_session.begin():
        after_revocation_counts = seed_authorization_context(db_session, fixture)
    preserved = db_session.get(
        InternalTrackingAssignment,
        (accounts["admin.demo"].id, trackings["SEG-A-001"].id),
    )
    assert after_revocation_counts == (0, 0)
    assert preserved is not None and preserved.revoked_at is not None


def test_revoked_internal_assignment_no_longer_authorizes_tracking_read(
    client: TestClient, db_session: Session
) -> None:
    admin = create_account(db_session, username="admin.revoke-assignment", password=PASSWORD)
    headers = login(client, "admin.revoke-assignment")
    alfa = create_client(client, headers, "assign-alfa", "Synthetic Alfa")
    process = create_process(client, headers, "00000000000000000000001")
    tracking = create_tracking(client, headers, UUID(alfa["id"]), UUID(process["id"]))
    db_session.add(
        InternalTrackingAssignment(
            account_id=admin.id,
            account_kind="INTERNAL",
            tracking_id=UUID(tracking["id"]),
            revoked_at=datetime.now(UTC),
        )
    )
    db_session.commit()

    response = client.get(f"{INTERNAL_API}/trackings/{tracking['id']}", headers=headers)
    assert response.status_code == 404


def test_concurrent_activation_serializes_on_the_postgres_tracking_row(
    client: TestClient, db_session: Session
) -> None:
    admin = create_account(db_session, username="admin.concurrent", password=PASSWORD)
    headers = login(client, "admin.concurrent")
    alfa = create_client(client, headers, "concurrent-alfa", "Synthetic Alfa")
    process = create_process(client, headers, "00000000000000000000001")
    tracking = create_tracking(client, headers, UUID(alfa["id"]), UUID(process["id"]))
    tracking_id = UUID(tracking["id"])
    db_session.add(
        InternalTrackingAssignment(
            account_id=admin.id,
            account_kind="INTERNAL",
            tracking_id=tracking_id,
        )
    )
    db_session.commit()

    principal = Principal(
        account_id=admin.id,
        person_id=admin.person_id,
        account_kind="INTERNAL",
        client_id=None,
        roles=("ADMIN",),
    )
    barrier = Barrier(2)

    def activate_once(_: int) -> str:
        with TEST_SESSION_FACTORY() as session:
            barrier.wait(timeout=5)
            try:
                result = TrackingService().activate_tracking(
                    session,
                    principal=principal,
                    request_id=uuid4(),
                    tracking_id=tracking_id,
                )
            except ResourceConflict:
                return "CONFLICT"
            return result.status

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(activate_once, range(2)))

    assert sorted(outcomes) == ["ACTIVE", "CONFLICT"]
    with TEST_ENGINE.connect() as connection:
        stored_status = connection.scalar(select(Tracking.status).where(Tracking.id == tracking_id))
        activation_events = connection.scalar(
            select(func.count())
            .select_from(AuditEvent)
            .where(
                AuditEvent.resource_id == tracking_id,
                AuditEvent.event_code == "TRACKING_ACTIVATE",
            )
        )
    assert stored_status == "ACTIVE"
    assert activation_events == 1
