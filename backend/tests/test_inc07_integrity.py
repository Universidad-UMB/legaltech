from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.acquisitions.models import Observation
from app.comparisons.models import Comparison, TechnicalChange
from app.novelties.models import Novelty, TrackingEvaluation
from app.publications.models import (
    PublicationApproval,
    PublicationVersion,
    PublicationVersionNovelty,
)
from app.trackings.models import InternalTrackingAssignment, Tracking
from tests.test_comparisons_api import _acquire_pair, _create_context
from tests.test_novelties_api import INTERNAL_API
from tests.test_publications_api import (
    CONTENT_V1,
    _create_publication,
    _create_publication_context,
    _submit,
)
from tests.traceability import trace_cases


@trace_cases("DT-18", "DT-38")
def test_database_rejects_linking_beta_novelty_to_alfa_publication(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc07-cross-tenant")
    tracking_a = db_session.get(Tracking, context.tracking_id)
    assert tracking_a is not None
    observations = list(
        db_session.scalars(
            select(Observation)
            .where(Observation.process_id == tracking_a.process_id)
            .order_by(Observation.observed_at)
        )
    )
    assert len(observations) == 2

    beta_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=context.admin_headers,
        json={"client_code": "beta-inc07-cross-tenant", "name": "Cliente sintético Beta"},
    )
    assert beta_client.status_code == 201, beta_client.text
    beta_tracking = client.post(
        f"{INTERNAL_API}/trackings",
        headers=context.admin_headers,
        json={
            "client_id": beta_client.json()["id"],
            "process_id": str(tracking_a.process_id),
        },
    )
    assert beta_tracking.status_code == 201, beta_tracking.text
    tracking_b_id = UUID(beta_tracking.json()["id"])
    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=account.id,
                account_kind="INTERNAL",
                tracking_id=tracking_b_id,
            )
            for account in (context.admin, context.analyst)
        ]
    )
    db_session.commit()
    activated = client.post(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/activate",
        headers=context.admin_headers,
    )
    assert activated.status_code == 200, activated.text

    baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/adoptions",
        headers=context.analyst_headers,
        json={"observation_id": str(observations[0].id)},
    )
    assert baseline.status_code == 200, baseline.text
    comparison = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=context.analyst_headers,
        json={
            "old_observation_id": str(observations[0].id),
            "new_observation_id": str(observations[1].id),
            "rule_version": "demo-v1",
        },
    )
    assert comparison.status_code == 200, comparison.text
    evaluation = client.post(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/evaluations",
        headers=context.analyst_headers,
        json={"comparison_id": comparison.json()["id"]},
    )
    assert evaluation.status_code == 201, evaluation.text
    novelty_b_id = UUID(evaluation.json()["novelty_ids"][0])
    novelty_b = db_session.get(Novelty, novelty_b_id)
    assert novelty_b is not None and novelty_b.tracking_id == tracking_b_id

    publication = _create_publication(client, context, content_text=CONTENT_V1)
    assert publication.status_code == 201, publication.text
    version_a_id = UUID(publication.json()["versions"][0])
    db_session.add(
        PublicationVersionNovelty(
            version_id=version_a_id,
            novelty_id=novelty_b_id,
            tracking_id=context.tracking_id,
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    assert (
        db_session.scalar(
            select(func.count())
            .select_from(PublicationVersionNovelty)
            .where(
                PublicationVersionNovelty.version_id == version_a_id,
                PublicationVersionNovelty.novelty_id == novelty_b_id,
            )
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.id == novelty_b_id)
        )
        == 1
    )


@trace_cases("DT-17")
def test_database_rejects_change_key_absent_from_new_observation(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    tracking_id, process_id, _, _, _, analyst_headers = _create_context(
        client, db_session, suffix="inc07-invalid-change"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="invalid-change"
    )
    comparison_response = client.post(
        "/api/v1/internal/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "inc07-invalid-change",
        },
    )
    assert comparison_response.status_code == 201, comparison_response.text
    comparison_id = UUID(comparison_response.json()["id"])

    db_session.add(
        TechnicalChange(
            id=uuid4(),
            comparison_id=comparison_id,
            process_id=process_id,
            new_observation_id=new_observation_id,
            action_key="ACT-99",
            change_kind="ADDED",
            evidence="Synthetic invalid key integrity probe.",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    assert (
        db_session.scalar(
            select(func.count())
            .select_from(TechnicalChange)
            .where(
                TechnicalChange.comparison_id == comparison_id,
                TechnicalChange.action_key == "ACT-99",
            )
        )
        == 0
    )
    assert db_session.get(Tracking, tracking_id) is not None


@trace_cases("DT-19")
def test_database_rejects_novelty_for_skipped_evaluation(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    tracking_id, process_id, _, _, _, analyst_headers = _create_context(
        client, db_session, suffix="inc07-skipped-novelty"
    )
    old_observation_id, new_observation_id = _acquire_pair(
        client, process_id=process_id, analyst_headers=analyst_headers, suffix="skipped-novelty"
    )
    comparison_response = client.post(
        "/api/v1/internal/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(old_observation_id),
            "new_observation_id": str(new_observation_id),
            "rule_version": "inc07-skipped-novelty",
        },
    )
    assert comparison_response.status_code == 201, comparison_response.text
    comparison_id = UUID(comparison_response.json()["id"])
    comparison = db_session.get(Comparison, comparison_id)
    tracking = db_session.get(Tracking, tracking_id)
    change = db_session.scalar(
        select(TechnicalChange).where(TechnicalChange.comparison_id == comparison_id)
    )
    assert comparison is not None and tracking is not None and change is not None

    skipped_evaluation = TrackingEvaluation(
        id=uuid4(),
        tracking_id=tracking_id,
        process_id=process_id,
        comparison_id=comparison_id,
        decision="SKIPPED",
        reason="Synthetic database check for a skipped evaluation.",
    )
    db_session.add(skipped_evaluation)
    db_session.flush()
    db_session.add(
        Novelty(
            id=uuid4(),
            novelty_code="NOV-INC07-SKIPPED",
            tracking_id=tracking_id,
            client_id=tracking.client_id,
            process_id=process_id,
            comparison_id=comparison_id,
            change_id=change.id,
            evaluation_id=skipped_evaluation.id,
            evaluation_decision="SKIPPED",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()


@trace_cases("API-N33", "DT-26")
def test_database_rejects_approval_by_second_account_of_preparer(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc07-same-person-db")
    created = _create_publication(client, context, content_text=CONTENT_V1)
    assert created.status_code == 201, created.text
    version_id = UUID(created.json()["versions"][0])
    submitted = _submit(client, context, str(version_id))
    assert submitted.status_code == 200, submitted.text

    db_session.expire_all()
    version = db_session.get(PublicationVersion, version_id)
    assert version is not None and version.status == "PENDING_APPROVAL"
    db_session.add(
        PublicationApproval(
            id=uuid4(),
            version_id=version_id,
            approver_account_id=context.same_person_coordinator.id,
            approver_person_id=context.same_person_coordinator.person_id,
            verdict="APPROVE",
            snapshot_sha256=version.content_sha256,
            justification="Synthetic trigger check for a second account of one person.",
        )
    )
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    assert (
        db_session.scalar(
            select(func.count())
            .select_from(PublicationApproval)
            .where(PublicationApproval.version_id == version_id)
        )
        == 0
    )
