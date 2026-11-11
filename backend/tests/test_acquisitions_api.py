from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.acquisitions.models import AcquisitionRun, Observation, ObservedAction
from app.acquisitions.service import AcquisitionService
from app.identity.domain import Principal
from app.identity.models import Account, AuditEvent
from app.trackings.models import (
    InternalTrackingAssignment,
    JudicialProcess,
    Tracking,
)
from tests.conftest import TEST_ENGINE, TEST_SESSION_FACTORY
from tests.factories import create_account

INTERNAL_API = "/api/v1/internal"
PASSWORD = "Synthetic-Test-Passphrase-2026!"


def _login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/sessions",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_context(
    client: TestClient,
    db_session: Session,
    *,
    suffix: str,
) -> tuple[UUID, UUID, UUID, dict[str, str], dict[str, str]]:
    admin_username = f"admin.{suffix}"
    analyst_username = f"analyst.{suffix}"
    admin = create_account(db_session, username=admin_username, password=PASSWORD)
    analyst = create_account(
        db_session,
        username=analyst_username,
        password=PASSWORD,
        roles=("ANALYST",),
    )
    admin_headers = _login(client, admin_username)
    analyst_headers = _login(client, analyst_username)

    client_response = client.post(
        f"{INTERNAL_API}/clients",
        headers=admin_headers,
        json={"client_code": f"alfa-{suffix}", "name": "Cliente sintético Alfa"},
    )
    assert client_response.status_code == 201, client_response.text
    client_id = UUID(client_response.json()["id"])
    process_response = client.post(
        f"{INTERNAL_API}/processes",
        headers=admin_headers,
        json={"radicado": "00000000000000000000001", "label": "Proceso fixture"},
    )
    assert process_response.status_code == 201, process_response.text
    process_id = UUID(process_response.json()["id"])
    tracking_response = client.post(
        f"{INTERNAL_API}/trackings",
        headers=admin_headers,
        json={"client_id": str(client_id), "process_id": str(process_id)},
    )
    assert tracking_response.status_code == 201, tracking_response.text
    tracking_id = UUID(tracking_response.json()["id"])

    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=admin.id,
                account_kind="INTERNAL",
                tracking_id=tracking_id,
            ),
            InternalTrackingAssignment(
                account_id=analyst.id,
                account_kind="INTERNAL",
                tracking_id=tracking_id,
            ),
        ]
    )
    db_session.commit()
    activated = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/activate",
        headers=admin_headers,
    )
    assert activated.status_code == 200, activated.text
    return tracking_id, process_id, analyst.id, admin_headers, analyst_headers


def test_acquisition_observation_baseline_idempotency_and_coverage(
    client: TestClient, db_session: Session
) -> None:
    tracking_id, process_id, _, admin_headers, analyst_headers = _create_context(
        client, db_session, suffix="inc02-flow"
    )
    create_url = f"{INTERNAL_API}/acquisition-runs"
    first_payload = {
        "process_id": str(process_id),
        "fixture_code": "OBS_001",
        "request_key": "inc02-obs001-run-001",
    }

    first = client.post(create_url, headers=analyst_headers, json=first_payload)
    assert first.status_code == 201, first.text
    assert first.headers["location"] == f"{create_url}/{first.json()['id']}"
    assert first.json()["status"] == "SUCCESS"
    assert first.json()["source_code"] == "DEMO-FIXTURE"
    observation_id = UUID(first.json()["observation_id"])

    replay = client.post(create_url, headers=analyst_headers, json=first_payload)
    assert replay.status_code == 200
    assert replay.json() == first.json()
    assert "location" not in replay.headers
    run_read = client.get(f"{create_url}/{first.json()['id']}", headers=analyst_headers)
    assert run_read.status_code == 200
    assert run_read.json() == first.json()

    observation_read = client.get(
        f"{INTERNAL_API}/observations/{observation_id}", headers=analyst_headers
    )
    assert observation_read.status_code == 200
    observation = observation_read.json()
    assert observation["process_id"] == str(process_id)
    assert observation["quality"] == "COMPARABLE"
    assert observation["sealed"] is True
    assert [action["action_key"] for action in observation["actions"]] == [
        "ACT-01",
        "ACT-02",
        "ACT-03",
        "ACT-04",
        "ACT-05",
    ]

    conflicting_replay = client.post(
        create_url,
        headers=analyst_headers,
        json={**first_payload, "fixture_code": "OBS_002"},
    )
    assert conflicting_replay.status_code == 409

    second = client.post(
        create_url,
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "OBS_002",
            "request_key": "inc02-obs002-run-001",
        },
    )
    assert second.status_code == 201, second.text
    assert second.json()["status"] == "SUCCESS"
    second_observation_id = UUID(second.json()["observation_id"])
    second_observation = client.get(
        f"{INTERNAL_API}/observations/{second_observation_id}", headers=analyst_headers
    )
    assert second_observation.status_code == 200
    assert len(second_observation.json()["actions"]) == 6

    beta = client.post(
        f"{INTERNAL_API}/clients",
        headers=admin_headers,
        json={"client_code": "beta-inc02-flow", "name": "Cliente sintético Beta"},
    )
    assert beta.status_code == 201
    beta_tracking = client.post(
        f"{INTERNAL_API}/trackings",
        headers=admin_headers,
        json={"client_id": beta.json()["id"], "process_id": str(process_id)},
    )
    assert beta_tracking.status_code == 201
    admin_id = UUID(client.get("/api/v1/auth/me", headers=admin_headers).json()["account_id"])
    analyst_id = UUID(client.get("/api/v1/auth/me", headers=analyst_headers).json()["account_id"])
    beta_tracking_id = UUID(beta_tracking.json()["id"])
    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=admin_id,
                account_kind="INTERNAL",
                tracking_id=beta_tracking_id,
            ),
            InternalTrackingAssignment(
                account_id=analyst_id,
                account_kind="INTERNAL",
                tracking_id=beta_tracking_id,
            ),
        ]
    )
    db_session.commit()
    beta_activated = client.post(
        f"{INTERNAL_API}/trackings/{beta_tracking_id}/activate",
        headers=admin_headers,
    )
    assert beta_activated.status_code == 200

    baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(observation_id)},
    )
    assert baseline.status_code == 200, baseline.text
    assert baseline.json()["outcome"] == "BASELINE_SET"
    assert baseline.json()["tracking"]["baseline_observation_id"] == str(observation_id)
    assert baseline.json()["tracking"]["last_adopted_observation_id"] == str(observation_id)

    baseline_replay = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(observation_id)},
    )
    assert baseline_replay.status_code == 200
    assert baseline_replay.json()["outcome"] == "ALREADY_ADOPTED"

    beta_baseline = client.post(
        f"{INTERNAL_API}/trackings/{beta_tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(second_observation_id)},
    )
    assert beta_baseline.status_code == 200, beta_baseline.text
    assert beta_baseline.json()["outcome"] == "BASELINE_SET"
    assert beta_baseline.json()["tracking"]["baseline_observation_id"] == str(second_observation_id)
    assert beta_baseline.json()["tracking"]["last_adopted_observation_id"] == str(
        second_observation_id
    )

    unevaluated_advance = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(second_observation_id)},
    )
    assert unevaluated_advance.status_code == 409
    tracking_read = client.get(f"{INTERNAL_API}/trackings/{tracking_id}", headers=admin_headers)
    assert tracking_read.json()["baseline_observation_id"] == str(observation_id)
    assert tracking_read.json()["last_adopted_observation_id"] == str(observation_id)

    failed = client.post(
        create_url,
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "FAILED",
            "request_key": "inc02-failed-run-001",
        },
    )
    assert failed.status_code == 201, failed.text
    assert failed.json()["status"] == "FAILED"
    assert failed.json()["observation_id"] is None
    assert failed.json()["error_code"] == "DEMO_SOURCE_UNAVAILABLE"
    assert failed.json()["coverage_note"] == "NOT_VERIFIED"
    failed_as_baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": failed.json()["observation_id"]},
    )
    assert failed_as_baseline.status_code == 422
    failed_read = client.get(f"{create_url}/{failed.json()['id']}", headers=analyst_headers)
    assert failed_read.status_code == 200
    assert failed_read.json()["coverage_note"] == "NOT_VERIFIED"

    incomplete = client.post(
        create_url,
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "INCOMPLETE",
            "request_key": "inc02-incomplete-run-001",
        },
    )
    assert incomplete.status_code == 201, incomplete.text
    assert incomplete.json()["status"] == "INCOMPLETE"
    assert incomplete.json()["observation_id"] is None
    assert incomplete.json()["coverage_note"]
    assert incomplete.json()["coverage_note"] != "NO_CHANGES"
    incomplete_read = client.get(f"{create_url}/{incomplete.json()['id']}", headers=analyst_headers)
    assert incomplete_read.status_code == 200
    assert incomplete_read.json()["coverage_note"] == incomplete.json()["coverage_note"]
    incomplete_as_baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": incomplete.json()["observation_id"]},
    )
    assert incomplete_as_baseline.status_code == 422
    after_failures = client.get(f"{INTERNAL_API}/trackings/{tracking_id}", headers=admin_headers)
    assert after_failures.json()["baseline_observation_id"] == str(observation_id)
    assert after_failures.json()["last_adopted_observation_id"] == str(observation_id)

    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(AcquisitionRun)) == 4
    assert db_session.scalar(select(func.count()).select_from(Observation)) == 2
    assert db_session.scalar(select(func.count()).select_from(ObservedAction)) == 11
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AuditEvent)
            .where(AuditEvent.event_code == "ACQUISITION_CREATE")
        )
        == 4
    )


def test_acquisition_requires_internal_assignment_and_matching_fixture_process(
    client: TestClient, db_session: Session
) -> None:
    _, process_id, _, admin_headers, analyst_headers = _create_context(
        client, db_session, suffix="inc02-scope"
    )
    other_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=admin_headers,
        json={"client_code": "beta-inc02", "name": "Cliente sintético Beta"},
    )
    assert other_client.status_code == 201
    other_process = client.post(
        f"{INTERNAL_API}/processes",
        headers=admin_headers,
        json={"radicado": "00000000000000000000002", "label": "Proceso scope"},
    )
    assert other_process.status_code == 201
    other_tracking = client.post(
        f"{INTERNAL_API}/trackings",
        headers=admin_headers,
        json={
            "client_id": other_client.json()["id"],
            "process_id": other_process.json()["id"],
        },
    )
    assert other_tracking.status_code == 201
    admin_account_id = UUID(
        client.get("/api/v1/auth/me", headers=admin_headers).json()["account_id"]
    )
    db_session.add(
        InternalTrackingAssignment(
            account_id=admin_account_id,
            account_kind="INTERNAL",
            tracking_id=UUID(other_tracking.json()["id"]),
        )
    )
    db_session.commit()

    unassigned = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=analyst_headers,
        json={
            "process_id": other_process.json()["id"],
            "fixture_code": "OBS_001",
            "request_key": "inc02-unassigned-key",
        },
    )
    assert unassigned.status_code == 404

    analyst = create_account(
        db_session,
        username="analyst.inc02-other-process",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    other_analyst_headers = _login(client, "analyst.inc02-other-process")
    db_session.add(
        InternalTrackingAssignment(
            account_id=analyst.id,
            account_kind="INTERNAL",
            tracking_id=UUID(other_tracking.json()["id"]),
        )
    )
    db_session.commit()
    other_activation = client.post(
        f"{INTERNAL_API}/trackings/{other_tracking.json()['id']}/activate",
        headers=admin_headers,
    )
    assert other_activation.status_code == 200

    wrong_fixture = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=other_analyst_headers,
        json={
            "process_id": other_process.json()["id"],
            "fixture_code": "OBS_001",
            "request_key": "inc02-wrong-fixture",
        },
    )
    assert wrong_fixture.status_code == 422

    source_acquisition = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "OBS_001",
            "request_key": "inc02-scoped-read-source",
        },
    )
    assert source_acquisition.status_code == 201
    inaccessible_run = client.get(
        f"{INTERNAL_API}/acquisition-runs/{source_acquisition.json()['id']}",
        headers=other_analyst_headers,
    )
    assert inaccessible_run.status_code == 404
    inaccessible_observation = client.get(
        f"{INTERNAL_API}/observations/{source_acquisition.json()['observation_id']}",
        headers=other_analyst_headers,
    )
    assert inaccessible_observation.status_code == 404

    external = create_account(
        db_session,
        username="external.inc02-reader",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=UUID(other_client.json()["id"]),
    )
    assert external.account_kind == "EXTERNAL"
    external_headers = _login(client, "external.inc02-reader")
    external_attempt = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=external_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "OBS_001",
            "request_key": "inc02-external-denied",
        },
    )
    assert external_attempt.status_code == 403


def test_postgres_rejects_mutation_of_sealed_observation_evidence(
    client: TestClient, db_session: Session
) -> None:
    tracking_id, process_id, _, _, analyst_headers = _create_context(
        client, db_session, suffix="inc02-seal"
    )
    created = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "OBS_001",
            "request_key": "inc02-seal-run-key",
        },
    )
    assert created.status_code == 201, created.text
    observation_id = UUID(created.json()["observation_id"])
    run_id = UUID(created.json()["id"])

    with pytest.raises(IntegrityError):
        db_session.execute(
            update(Observation)
            .where(Observation.id == observation_id)
            .values(coverage_note="mutated synthetic evidence")
        )
    db_session.rollback()

    with pytest.raises(IntegrityError):
        db_session.execute(
            update(AcquisitionRun)
            .where(AcquisitionRun.id == run_id)
            .values(coverage_note="mutated run")
        )
    db_session.rollback()

    with pytest.raises(IntegrityError):
        db_session.add(
            ObservedAction(
                observation_id=observation_id,
                action_key="ACT-99",
                content_sha256="0" * 64,
                description="Late append must be rejected",
            )
        )
        db_session.flush()
    db_session.rollback()

    with pytest.raises(IntegrityError):
        db_session.execute(
            update(ObservedAction)
            .where(
                ObservedAction.observation_id == observation_id,
                ObservedAction.action_key == "ACT-01",
            )
            .values(description="Changed after sealing")
        )
    db_session.rollback()

    with pytest.raises(IntegrityError):
        db_session.execute(delete(Observation).where(Observation.id == observation_id))
    db_session.rollback()

    second_process = JudicialProcess(
        id=uuid4(),
        radicado="00000000000000000000002",
        label="Segundo proceso sintético",
    )
    db_session.add(second_process)
    db_session.commit()
    with pytest.raises(IntegrityError):
        db_session.execute(
            update(Tracking)
            .where(Tracking.id == tracking_id)
            .values(
                process_id=second_process.id,
                baseline_observation_id=observation_id,
                last_adopted_observation_id=observation_id,
            )
        )
    db_session.rollback()


def test_incomplete_unsealed_observation_cannot_be_adopted(
    client: TestClient, db_session: Session
) -> None:
    tracking_id, process_id, _, admin_headers, analyst_headers = _create_context(
        client, db_session, suffix="inc02-incomplete-adoption"
    )
    created = client.post(
        f"{INTERNAL_API}/acquisition-runs",
        headers=analyst_headers,
        json={
            "process_id": str(process_id),
            "fixture_code": "INCOMPLETE",
            "request_key": "inc02-incomplete-baseline",
        },
    )
    assert created.status_code == 201
    incomplete_observation = Observation(
        id=uuid4(),
        process_id=process_id,
        acquisition_run_id=UUID(created.json()["id"]),
        quality="INCOMPLETE",
        observed_at=datetime(2026, 10, 16, 12, 0, tzinfo=UTC),
        payload_sha256="0" * 64,
        provenance="DEMO-FIXTURE",
        coverage_note="PARTIAL_NOT_COMPARABLE",
    )
    db_session.add(incomplete_observation)
    db_session.commit()

    rejected = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(incomplete_observation.id)},
    )
    assert rejected.status_code == 409
    tracking = client.get(f"{INTERNAL_API}/trackings/{tracking_id}", headers=admin_headers)
    assert tracking.status_code == 200
    assert tracking.json()["baseline_observation_id"] is None
    assert tracking.json()["last_adopted_observation_id"] is None


def test_failed_acquisition_cannot_create_comparable_observation(
    client: TestClient, db_session: Session
) -> None:
    _, process_id, _, _, _ = _create_context(client, db_session, suffix="inc02-failed-guard")
    failed_run = AcquisitionRun(
        id=uuid4(),
        process_id=process_id,
        source_code="DEMO-FIXTURE",
        fixture_code="FAILED",
        status="FAILED",
        request_key="inc02-direct-failed-run",
        request_payload_sha256="1" * 64,
        finished_at=datetime.now(UTC),
        error_code="DEMO_SOURCE_UNAVAILABLE",
        coverage_note="NOT_VERIFIED",
    )
    db_session.add(failed_run)
    db_session.flush()
    db_session.add(
        Observation(
            id=uuid4(),
            process_id=process_id,
            acquisition_run_id=failed_run.id,
            quality="COMPARABLE",
            observed_at=datetime(2026, 10, 15, 12, 0, tzinfo=UTC),
            payload_sha256="2" * 64,
            provenance="DEMO-FIXTURE",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


def test_request_key_and_baseline_retries_serialize_on_postgres_rows(
    client: TestClient, db_session: Session
) -> None:
    tracking_id, process_id, analyst_id, _, _ = _create_context(
        client, db_session, suffix="inc02-race"
    )
    analyst = db_session.get(Account, analyst_id)
    assert analyst is not None
    principal = Principal(
        account_id=analyst_id,
        person_id=analyst.person_id,
        account_kind="INTERNAL",
        client_id=None,
        roles=("ANALYST",),
    )
    payload_key = "inc02-concurrent-acquisition"
    barrier = Barrier(2)

    def acquire_once(_: int) -> tuple[UUID, bool, UUID]:
        with TEST_SESSION_FACTORY() as session:
            barrier.wait(timeout=5)
            result = AcquisitionService().create(
                session,
                principal=principal,
                request_id=uuid4(),
                process_id=process_id,
                fixture_code="OBS_001",
                request_key=payload_key,
            )
            observation_id = result.acquisition.observation_id
            assert observation_id is not None
            return result.acquisition.id, result.created, observation_id

    with ThreadPoolExecutor(max_workers=2) as pool:
        acquisition_results = list(pool.map(acquire_once, range(2)))
    assert len({run_id for run_id, _, _ in acquisition_results}) == 1
    assert sorted(created for _, created, _ in acquisition_results) == [False, True]
    observation_ids = {observation_id for _, _, observation_id in acquisition_results}
    assert len(observation_ids) == 1

    observation_id = next(iter(observation_ids))
    adoption_barrier = Barrier(2)

    def adopt_once(_: int) -> str:
        with TEST_SESSION_FACTORY() as session:
            adoption_barrier.wait(timeout=5)
            _, outcome = AcquisitionService().adopt_observation(
                session,
                principal=principal,
                request_id=uuid4(),
                tracking_id=tracking_id,
                observation_id=observation_id,
            )
            return outcome

    with ThreadPoolExecutor(max_workers=2) as pool:
        adoption_results = list(pool.map(adopt_once, range(2)))
    assert sorted(adoption_results) == ["ALREADY_ADOPTED", "BASELINE_SET"]

    with TEST_ENGINE.connect() as connection:
        run_count = connection.scalar(
            select(func.count())
            .select_from(AcquisitionRun)
            .where(AcquisitionRun.request_key == payload_key)
        )
        observation_count = connection.scalar(
            select(func.count()).select_from(Observation).where(Observation.id == observation_id)
        )
        stored_cursor = connection.scalar(
            select(Tracking.last_adopted_observation_id).where(Tracking.id == tracking_id)
        )
    assert run_count == 1
    assert observation_count == 1
    assert stored_cursor == observation_id
