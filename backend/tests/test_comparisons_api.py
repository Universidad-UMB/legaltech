from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.acquisitions.models import AcquisitionRun, Observation, ObservedAction
from app.acquisitions.service import AcquisitionService
from app.comparisons.models import Comparison as ComparisonModel
from app.comparisons.models import TechnicalChange
from app.comparisons.service import ComparisonService
from app.identity.domain import Principal
from app.novelties.models import Novelty, TrackingEvaluation
from app.novelties.service import EvaluationService
from app.trackings.models import InternalTrackingAssignment, Tracking
from tests.conftest import TEST_ENGINE, TEST_SESSION_FACTORY
from tests.factories import create_account
from tests.traceability import trace_cases

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
) -> tuple[UUID, UUID, object, object, dict[str, str], dict[str, str]]:
    admin = create_account(db_session, username=f"admin.{suffix}", password=PASSWORD)
    analyst = create_account(
        db_session,
        username=f"analyst.{suffix}",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    admin_headers = _login(client, f"admin.{suffix}")
    analyst_headers = _login(client, f"analyst.{suffix}")

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
    return tracking_id, process_id, admin, analyst, admin_headers, analyst_headers


def _acquire_pair(
    client: TestClient, *, process_id: UUID, analyst_headers: dict[str, str], suffix: str
) -> tuple[UUID, UUID]:
    observations: list[UUID] = []
    for fixture_code in ("OBS_001", "OBS_002"):
        response = client.post(
            f"{INTERNAL_API}/acquisition-runs",
            headers=analyst_headers,
            json={
                "process_id": str(process_id),
                "fixture_code": fixture_code,
                "request_key": f"inc03-{suffix}-{fixture_code.lower()}-key",
            },
        )
        assert response.status_code == 201, response.text
        observations.append(UUID(response.json()["observation_id"]))
    return observations[0], observations[1]


def _create_comparison(
    client: TestClient,
    *,
    analyst_headers: dict[str, str],
    old_observation_id: UUID,
    new_observation_id: UUID,
) -> dict[str, object]:
    response = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "demo-v1",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@trace_cases("DT-15", "DT-16", "API-N14")
def test_comparison_evaluation_novelty_and_adoption_are_idempotent_and_scoped(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    tracking_id, process_id, admin, analyst, admin_headers, analyst_headers = _create_context(
        client, db_session, suffix="inc03-flow"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="flow"
    )
    baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(old_observation_id)},
    )
    assert baseline.status_code == 200, baseline.text
    assert baseline.json()["outcome"] == "BASELINE_SET"

    comparison = _create_comparison(
        client,
        analyst_headers=analyst_headers,
        old_observation_id=old_observation_id,
        new_observation_id=new_observation_id,
    )
    assert comparison["result"] == "CHANGES_FOUND"
    assert [change["action_key"] for change in comparison["changes"]] == ["ACT-06"]
    assert comparison["changes"][0]["change_kind"] == "ADDED"
    assert comparison["changes"][0]["evidence"]
    comparison_id = UUID(comparison["id"])
    assert (
        client.get(f"{INTERNAL_API}/comparisons/{comparison_id}", headers=analyst_headers).json()
        == comparison
    )

    repeated_comparison = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "demo-v1",
        },
    )
    assert repeated_comparison.status_code == 200
    assert repeated_comparison.json() == comparison
    assert "location" not in repeated_comparison.headers

    outsider = create_account(
        db_session,
        username="analyst.inc03-outsider",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    outsider_headers = _login(client, "analyst.inc03-outsider")
    assert outsider.id != analyst.id
    out_of_scope_comparison = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=outsider_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "demo-v1",
        },
    )
    assert out_of_scope_comparison.status_code == 404
    assert (
        client.get(
            f"{INTERNAL_API}/comparisons/{comparison_id}", headers=outsider_headers
        ).status_code
        == 404
    )
    external_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=admin_headers,
        json={"client_code": "external-inc03", "name": "Cliente sintético externo"},
    )
    assert external_client.status_code == 201, external_client.text
    external = create_account(
        db_session,
        username="reader.inc03-external",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=UUID(external_client.json()["id"]),
    )
    assert external.account_kind == "EXTERNAL"
    external_headers = _login(client, "reader.inc03-external")
    assert (
        client.post(
            f"{INTERNAL_API}/comparisons",
            headers=external_headers,
            json={
                "old_observation_id": str(old_observation_id),
                "new_observation_id": str(new_observation_id),
                "rule_version": "demo-v1",
            },
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
            headers=outsider_headers,
            json={"comparison_id": str(comparison_id)},
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
            headers=external_headers,
            json={"comparison_id": str(comparison_id)},
        ).status_code
        == 403
    )

    evaluation_response = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": str(comparison_id)},
    )
    assert evaluation_response.status_code == 201, evaluation_response.text
    evaluation = evaluation_response.json()
    assert evaluation["decision"] == "ELIGIBLE"
    assert evaluation["novelty_ids"] and len(evaluation["novelty_ids"]) == 1
    assert "Location" in evaluation_response.headers
    evaluation_id = UUID(evaluation["id"])

    repeated_evaluation = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": str(comparison_id)},
    )
    assert repeated_evaluation.status_code == 200
    assert repeated_evaluation.json() == evaluation

    novelty = db_session.scalar(
        select(Novelty).where(Novelty.id == UUID(evaluation["novelty_ids"][0]))
    )
    assert novelty is not None
    assert novelty.novelty_code == "NOV-A-001"
    assert novelty.tracking_id == tracking_id
    assert novelty.comparison_id == comparison_id
    assert novelty.status == "PENDING_OPERATIVE"
    assert (
        db_session.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.tracking_id == tracking_id)
        )
        == 1
    )

    beta_response = client.post(
        f"{INTERNAL_API}/clients",
        headers=admin_headers,
        json={"client_code": "beta-inc03-flow", "name": "Cliente sintético Beta"},
    )
    assert beta_response.status_code == 201, beta_response.text
    beta_tracking_response = client.post(
        f"{INTERNAL_API}/trackings",
        headers=admin_headers,
        json={"client_id": beta_response.json()["id"], "process_id": str(process_id)},
    )
    assert beta_tracking_response.status_code == 201, beta_tracking_response.text
    beta_tracking_id = UUID(beta_tracking_response.json()["id"])
    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=admin.id,
                account_kind="INTERNAL",
                tracking_id=beta_tracking_id,
            ),
            InternalTrackingAssignment(
                account_id=analyst.id,
                account_kind="INTERNAL",
                tracking_id=beta_tracking_id,
            ),
        ]
    )
    db_session.commit()
    assert (
        client.post(
            f"{INTERNAL_API}/trackings/{beta_tracking_id}/activate", headers=admin_headers
        ).status_code
        == 200
    )
    beta_baseline = client.post(
        f"{INTERNAL_API}/trackings/{beta_tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(new_observation_id)},
    )
    assert beta_baseline.status_code == 200, beta_baseline.text
    assert beta_baseline.json()["outcome"] == "BASELINE_SET"
    assert beta_baseline.json()["tracking"]["baseline_observation_id"] == str(new_observation_id)
    beta_retroactive_evaluation = client.post(
        f"{INTERNAL_API}/trackings/{beta_tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": str(comparison_id)},
    )
    assert beta_retroactive_evaluation.status_code == 409
    assert (
        db_session.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.tracking_id == beta_tracking_id)
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(TrackingEvaluation)
            .where(TrackingEvaluation.tracking_id == beta_tracking_id)
        )
        == 0
    )

    advanced = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(new_observation_id)},
    )
    assert advanced.status_code == 200, advanced.text
    assert advanced.json()["outcome"] == "ADVANCED"
    assert advanced.json()["tracking"]["last_adopted_observation_id"] == str(new_observation_id)
    repeated_adoption = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(new_observation_id)},
    )
    assert repeated_adoption.status_code == 200
    assert repeated_adoption.json()["outcome"] == "ALREADY_ADOPTED"
    evaluation_after_advance = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": str(comparison_id)},
    )
    assert evaluation_after_advance.status_code == 200
    assert evaluation_after_advance.json() == evaluation
    assert db_session.get(TrackingEvaluation, evaluation_id) is not None

    stored_change = db_session.scalar(
        select(TechnicalChange).where(TechnicalChange.comparison_id == comparison_id)
    )
    assert stored_change is not None
    db_session.add(
        TechnicalChange(
            id=uuid4(),
            comparison_id=stored_change.comparison_id,
            process_id=stored_change.process_id,
            new_observation_id=stored_change.new_observation_id,
            action_key=stored_change.action_key,
            change_kind=stored_change.change_kind,
            evidence=stored_change.evidence,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


@trace_cases("DT-13", "DT-14")
def test_comparison_records_non_comparable_pairs_without_confirming_changes(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    _, process_id, _, _, admin_headers, analyst_headers = _create_context(
        client, db_session, suffix="inc03-order"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="order"
    )
    reversed_pair = _create_comparison(
        client,
        analyst_headers=analyst_headers,
        old_observation_id=new_observation_id,
        new_observation_id=old_observation_id,
    )
    assert reversed_pair["result"] == "NOT_COMPARABLE"
    assert reversed_pair["changes"] == []

    other_process_response = client.post(
        f"{INTERNAL_API}/processes",
        headers=admin_headers,
        json={"radicado": "00000000000000000000002", "label": "Otro proceso sintético"},
    )
    assert other_process_response.status_code == 201, other_process_response.text
    other_process_id = UUID(other_process_response.json()["id"])
    other_observation_id = _insert_synthetic_observation(db_session, process_id=other_process_id)
    assert db_session.get(Observation, other_observation_id) is not None
    mismatched_process = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(other_observation_id),
            "rule_version": "demo-v1",
        },
    )
    assert mismatched_process.status_code == 404
    assert db_session.scalar(select(func.count()).select_from(ComparisonModel)) == 1

    same_snapshot = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(old_observation_id),
            "rule_version": "demo-v1",
        },
    )
    assert same_snapshot.status_code == 422
    blank_rule = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "   ",
        },
    )
    assert blank_rule.status_code == 422
    assert (
        client.get(f"{INTERNAL_API}/comparisons/{UUID(int=0)}", headers=analyst_headers).status_code
        == 404
    )


@trace_cases("DT-19")
def test_evaluation_and_adoption_reject_skipping_a_comparable_snapshot(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    tracking_id, process_id, _, _, _, analyst_headers = _create_context(
        client, db_session, suffix="inc03-skip"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="skip"
    )
    assert (
        client.post(
            f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
            headers=analyst_headers,
            json={"observation_id": str(old_observation_id)},
        ).status_code
        == 200
    )
    comparison = _create_comparison(
        client,
        analyst_headers=analyst_headers,
        old_observation_id=old_observation_id,
        new_observation_id=new_observation_id,
    )
    _insert_synthetic_intermediate_observation(
        db_session, process_id=process_id, source_observation_id=old_observation_id
    )

    evaluation = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": comparison["id"]},
    )
    assert evaluation.status_code == 409
    skipped_adoption = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(new_observation_id)},
    )
    assert skipped_adoption.status_code == 409
    tracking = client.get(f"{INTERNAL_API}/trackings/{tracking_id}", headers=analyst_headers).json()
    assert tracking["last_adopted_observation_id"] == str(old_observation_id)
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(TrackingEvaluation)
            .where(TrackingEvaluation.tracking_id == tracking_id)
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.tracking_id == tracking_id)
        )
        == 0
    )


def _insert_synthetic_intermediate_observation(
    session: Session, *, process_id: UUID, source_observation_id: UUID
) -> None:
    source_actions = tuple(
        session.scalars(
            select(ObservedAction).where(ObservedAction.observation_id == source_observation_id)
        )
    )
    run_id = UUID("ffffffff-ffff-4fff-8fff-fffffffffff1")
    observation_id = UUID("ffffffff-ffff-4fff-8fff-fffffffffff2")
    session.add(
        AcquisitionRun(
            id=run_id,
            process_id=process_id,
            source_code="DEMO-FIXTURE",
            fixture_code="OBS_001",
            status="SUCCESS",
            request_key="inc03-synthetic-intermediate-run",
            request_payload_sha256="c" * 64,
            finished_at=datetime.now(UTC),
            error_code=None,
            coverage_note=None,
        )
    )
    session.flush()
    session.add(
        Observation(
            id=observation_id,
            process_id=process_id,
            acquisition_run_id=run_id,
            quality="COMPARABLE",
            observed_at=datetime(2026, 10, 15, 18, 0, tzinfo=UTC),
            payload_sha256="d" * 64,
            provenance="DEMO-FIXTURE",
        )
    )
    session.flush()
    session.add_all(
        [
            ObservedAction(
                observation_id=observation_id,
                action_key=action.action_key,
                content_sha256=action.content_sha256,
                description=action.description,
                occurred_on=action.occurred_on,
            )
            for action in source_actions
        ]
    )
    session.flush()
    session.execute(
        update(Observation).where(Observation.id == observation_id).values(sealed_at=func.now())
    )
    session.commit()


def _insert_synthetic_observation(session: Session, *, process_id: UUID) -> UUID:
    run_id = uuid4()
    observation_id = uuid4()
    session.add(
        AcquisitionRun(
            id=run_id,
            process_id=process_id,
            source_code="DEMO-FIXTURE",
            fixture_code="OBS_001",
            status="SUCCESS",
            request_key=f"inc03-synthetic-run-{run_id.hex}",
            request_payload_sha256="e" * 64,
            finished_at=datetime.now(UTC),
            error_code=None,
            coverage_note=None,
        )
    )
    session.flush()
    session.add(
        Observation(
            id=observation_id,
            process_id=process_id,
            acquisition_run_id=run_id,
            quality="COMPARABLE",
            observed_at=datetime(2026, 10, 20, 12, 0, tzinfo=UTC),
            payload_sha256="f" * 64,
            provenance="DEMO-FIXTURE",
        )
    )
    session.commit()
    return observation_id


@trace_cases("DT-20", "API-N15")
def test_concurrent_comparison_evaluation_and_adoption_use_independent_sessions(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    tracking_id, process_id, _, analyst, _, analyst_headers = _create_context(
        client, db_session, suffix="inc03-race"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="race"
    )
    assert (
        client.post(
            f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
            headers=analyst_headers,
            json={"observation_id": str(old_observation_id)},
        ).status_code
        == 200
    )
    principal = Principal(
        account_id=analyst.id,
        person_id=analyst.person_id,
        account_kind="INTERNAL",
        client_id=None,
        roles=("ANALYST",),
    )
    comparison_barrier = Barrier(2)

    def compare_once(_: int) -> tuple[UUID, bool, tuple[UUID, ...]]:
        with TEST_SESSION_FACTORY() as session:
            comparison_barrier.wait(timeout=5)
            result, created = ComparisonService().compare(
                session,
                principal=principal,
                request_id=uuid4(),
                old_observation_id=old_observation_id,
                new_observation_id=new_observation_id,
                rule_version="demo-v1",
            )
            return result.id, created, tuple(change.id for change in result.changes)

    with ThreadPoolExecutor(max_workers=2) as pool:
        comparisons = list(pool.map(compare_once, range(2)))
    assert len({comparison_id for comparison_id, _, _ in comparisons}) == 1
    assert sorted(created for _, created, _ in comparisons) == [False, True]
    change_sets = {change_ids for _, _, change_ids in comparisons}
    assert len(change_sets) == 1
    assert len(next(iter(change_sets))) == 1
    comparison_id = comparisons[0][0]
    comparison_read = client.get(
        f"{INTERNAL_API}/comparisons/{comparison_id}", headers=analyst_headers
    )
    assert comparison_read.status_code == 200
    assert comparison_read.json()["result"] == "CHANGES_FOUND"
    assert [change["action_key"] for change in comparison_read.json()["changes"]] == ["ACT-06"]
    evaluation_barrier = Barrier(2)

    def evaluate_once(_: int) -> tuple[UUID, bool, tuple[UUID, ...]]:
        with TEST_SESSION_FACTORY() as session:
            evaluation_barrier.wait(timeout=5)
            result, created = EvaluationService().evaluate(
                session,
                principal=principal,
                request_id=uuid4(),
                tracking_id=tracking_id,
                comparison_id=comparison_id,
            )
            return result.id, created, result.novelty_ids

    with ThreadPoolExecutor(max_workers=2) as pool:
        evaluations = list(pool.map(evaluate_once, range(2)))
    assert len({evaluation_id for evaluation_id, _, _ in evaluations}) == 1
    assert sorted(created for _, created, _ in evaluations) == [False, True]
    novelty_sets = {novelty_ids for _, _, novelty_ids in evaluations}
    assert len(novelty_sets) == 1
    assert len(next(iter(novelty_sets))) == 1

    adoption_barrier = Barrier(2)

    def adopt_once(_: int) -> str:
        with TEST_SESSION_FACTORY() as session:
            adoption_barrier.wait(timeout=5)
            _, outcome = AcquisitionService().adopt_observation(
                session,
                principal=principal,
                request_id=uuid4(),
                tracking_id=tracking_id,
                observation_id=new_observation_id,
            )
            return outcome

    with ThreadPoolExecutor(max_workers=2) as pool:
        adoption_results = list(pool.map(adopt_once, range(2)))
    assert sorted(adoption_results) == ["ADVANCED", "ALREADY_ADOPTED"]

    with TEST_ENGINE.connect() as connection:
        evaluation_count = connection.scalar(
            select(func.count())
            .select_from(TrackingEvaluation)
            .where(TrackingEvaluation.tracking_id == tracking_id)
        )
        novelty_count = connection.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.tracking_id == tracking_id)
        )
        cursor = connection.scalar(
            select(Tracking.last_adopted_observation_id).where(Tracking.id == tracking_id)
        )
    assert evaluation_count == 1
    assert novelty_count == 1
    assert cursor == new_observation_id
