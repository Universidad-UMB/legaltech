from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.acquisitions.models import AcquisitionRun, Observation
from app.identity.models import AccountRole
from app.novelties.models import Novelty, NoveltyReview
from app.publications.models import Publication, PublicationApproval, PublicationVersion
from app.trackings.models import InternalTrackingAssignment, Tracking
from tests.factories import create_account
from tests.test_novelties_api import INTERNAL_API, _login
from tests.test_portal_api import _add_scope, _create_tracking
from tests.test_publications_api import (
    CONTENT_V1,
    CONTENT_V2,
    PUBLICATIONS_API,
    VERSION_API,
    _create_publication,
    _create_publication_context,
    _decide,
    _publish,
    _submit,
)
from tests.traceability import trace_cases

PORTAL_API = "/api/v1/portal"
SUSPEND_REASON = "Synthetic demo suspension verification."
REACTIVATE_REASON = "Synthetic demo suspension check is complete."
FINISH_REASON = "Synthetic demo monitoring has finished."


@trace_cases(
    "PROTO-AT-01",
    "PROTO-AT-02",
    "PROTO-AT-03",
    "PROTO-AT-04",
    "PROTO-AT-05",
    "PROTO-AT-06",
    "PROTO-AT-07",
    "PROTO-AT-08",
    "PROTO-AT-09",
    "PROTO-AT-10",
    "PROTO-AT-11",
    "PROTO-AT-12",
    "PROTO-AT-13",
    "PROTO-AT-14",
    "PROTO-AT-15",
    "PROTO-AT-16",
    "PROTO-AT-17",
    "PROTO-AT-18",
)
def test_proto_at_01_through_18_full_synthetic_journey(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc07-e2e")
    tracking_a = db_session.get(Tracking, context.tracking_id)
    assert tracking_a is not None
    process_id = tracking_a.process_id
    client_a_id = tracking_a.client_id
    observations = list(
        db_session.scalars(
            select(Observation)
            .where(Observation.process_id == process_id)
            .order_by(Observation.observed_at)
        )
    )
    assert len(observations) == 2
    obs_001_id, obs_002_id = observations[0].id, observations[1].id
    assert tracking_a.baseline_observation_id == obs_001_id
    assert tracking_a.last_adopted_observation_id == obs_001_id
    external_reader_a = create_account(
        db_session,
        username="reader.inc07-alfa",
        password="Synthetic-Test-Passphrase-2026!",
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=client_a_id,
    )

    beta_response = client.post(
        f"{INTERNAL_API}/clients",
        headers=context.admin_headers,
        json={"client_code": "beta-inc07-e2e", "name": "Cliente sintético Beta"},
    )
    assert beta_response.status_code == 201, beta_response.text
    client_b_id = UUID(beta_response.json()["id"])
    external_reader_b = create_account(
        db_session,
        username="reader.inc07-beta",
        password="Synthetic-Test-Passphrase-2026!",
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=client_b_id,
    )
    tracking_b_response = client.post(
        f"{INTERNAL_API}/trackings",
        headers=context.admin_headers,
        json={"client_id": str(client_b_id), "process_id": str(process_id)},
    )
    assert tracking_b_response.status_code == 201, tracking_b_response.text
    tracking_b_id = UUID(tracking_b_response.json()["id"])
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
    activated_b = client.post(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/activate",
        headers=context.admin_headers,
    )
    assert activated_b.status_code == 200, activated_b.text

    tracking_a2_id = _create_tracking(
        client,
        db_session,
        admin=context.admin,
        admin_headers=context.admin_headers,
        client_id=client_a_id,
        radicado="00000000000000000000002",
        label="Proceso ficticio exclusivo para comprobar el ámbito A2",
    )
    _add_scope(db_session, external_reader_a, context.tracking_id)
    _add_scope(db_session, external_reader_b, tracking_b_id)
    db_session.commit()
    headers_a = _login(client, external_reader_a.username)
    headers_b = _login(client, external_reader_b.username)

    # AT-01 and AT-02: process identity, separate customer tracking, and activation.
    process_read = client.get(
        f"{INTERNAL_API}/processes/{process_id}", headers=context.admin_headers
    )
    assert process_read.status_code == 200, process_read.text
    assert process_read.json()["radicado"] == "00000000000000000000001"
    tracking_read_a = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}", headers=context.admin_headers
    )
    tracking_read_b = client.get(
        f"{INTERNAL_API}/trackings/{tracking_b_id}", headers=context.admin_headers
    )
    assert tracking_read_a.json()["status"] == tracking_read_b.json()["status"] == "ACTIVE"
    assert tracking_read_a.json()["process_id"] == tracking_read_b.json()["process_id"]
    assert tracking_read_a.json()["client_id"] != tracking_read_b.json()["client_id"]
    covered = {"PROTO-AT-01", "PROTO-AT-02"}

    # AT-03 through AT-06: independent baselines, comparison idempotency, and eligibility.
    tracking_read_a = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}", headers=context.admin_headers
    )
    assert tracking_read_a.json()["baseline_observation_id"] == str(obs_001_id)
    assert tracking_read_a.json()["last_adopted_observation_id"] == str(obs_001_id)
    covered.add("PROTO-AT-03")

    comparison_payload = {
        "old_observation_id": str(obs_001_id),
        "new_observation_id": str(obs_002_id),
        "rule_version": "demo-v1",
    }
    comparison_repeat = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=context.analyst_headers,
        json=comparison_payload,
    )
    assert comparison_repeat.status_code == 200, comparison_repeat.text
    assert comparison_repeat.json()["result"] == "CHANGES_FOUND"
    assert [change["action_key"] for change in comparison_repeat.json()["changes"]] == ["ACT-06"]
    adoption_a = client.post(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/adoptions",
        headers=context.analyst_headers,
        json={"observation_id": str(obs_002_id)},
    )
    assert adoption_a.status_code == 200, adoption_a.text
    assert adoption_a.json()["outcome"] == "ADVANCED"
    tracking_after_adoption = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}", headers=context.admin_headers
    )
    assert tracking_after_adoption.json()["last_adopted_observation_id"] == str(obs_002_id)
    covered.update({"PROTO-AT-04", "PROTO-AT-05"})

    novelty_a_read = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties",
        headers=context.analyst_headers,
    )
    assert novelty_a_read.status_code == 200, novelty_a_read.text
    assert len(novelty_a_read.json()["items"]) == 1
    assert novelty_a_read.json()["items"][0]["novelty_code"] == "NOV-A-001"
    baseline_b = client.post(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/adoptions",
        headers=context.analyst_headers,
        json={"observation_id": str(obs_002_id)},
    )
    assert baseline_b.status_code == 200, baseline_b.text
    assert baseline_b.json()["outcome"] == "BASELINE_SET"
    novelties_b = client.get(
        f"{INTERNAL_API}/trackings/{tracking_b_id}/novelties",
        headers=context.analyst_headers,
    )
    assert novelties_b.status_code == 200, novelties_b.text
    assert novelties_b.json()["items"] == []
    covered.add("PROTO-AT-06")

    # AT-07 and AT-08: the fixture helper executes the assigned analyst and lawyer reviews.
    db_session.expire_all()
    novelty = db_session.get(Novelty, context.novelty_id)
    assert novelty is not None and novelty.status == "TREATMENT_DEFINED"
    reviews = list(
        db_session.scalars(
            select(NoveltyReview).where(NoveltyReview.novelty_id == context.novelty_id)
        )
    )
    assert {review.review_kind for review in reviews} == {"OPERATIVE", "LEGAL"}
    operative_actor_id = next(
        review.actor_account_id for review in reviews if review.review_kind == "OPERATIVE"
    )
    legal_actor_id = next(
        review.actor_account_id for review in reviews if review.review_kind == "LEGAL"
    )
    assert operative_actor_id == context.analyst.id
    assert legal_actor_id != operative_actor_id
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AccountRole)
            .where(AccountRole.account_id == legal_actor_id, AccountRole.role_code == "LAWYER")
        )
        == 1
    )
    covered.update({"PROTO-AT-07", "PROTO-AT-08"})

    # AT-15: failed/incomplete fixture runs retain explicit coverage and do not move cursors.
    acquisition_url = f"{INTERNAL_API}/acquisition-runs"
    coverage_statuses = (("FAILED", "FAILED"), ("INCOMPLETE", "INCOMPLETE"))
    for index, (fixture_code, expected_status) in enumerate(coverage_statuses, start=1):
        acquisition = client.post(
            acquisition_url,
            headers=context.analyst_headers,
            json={
                "process_id": str(process_id),
                "fixture_code": fixture_code,
                "request_key": f"inc07-coverage-run-{index:02d}",
            },
        )
        assert acquisition.status_code == 201, acquisition.text
        assert acquisition.json()["status"] == expected_status
        assert acquisition.json()["observation_id"] is None
        assert acquisition.json()["coverage_note"] != "NO_CHANGES"
        portal_coverage = client.get(
            f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
            headers=headers_a,
        )
        assert portal_coverage.status_code == 200, portal_coverage.text
        assert portal_coverage.json()["coverage_status"] == expected_status
        assert portal_coverage.json()["available"] is False
    after_coverage = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}", headers=context.admin_headers
    )
    assert after_coverage.json()["baseline_observation_id"] == str(obs_001_id)
    assert after_coverage.json()["last_adopted_observation_id"] == str(obs_002_id)
    covered.add("PROTO-AT-15")

    # AT-16: health and authentication are available; seed and app-restart persistence are
    # exercised with the same synthetic identity bootstrap in test_acceptance_infrastructure.
    assert client.get("/healthz").status_code == 200
    assert client.get("/api/v1/auth/me", headers=context.admin_headers).status_code == 200
    covered.add("PROTO-AT-16")

    # AT-09 and AT-10: a draft stays private, then requires another natural person to approve.
    created = _create_publication(client, context, content_text=CONTENT_V1)
    assert created.status_code == 201, created.text
    publication_id = UUID(created.json()["id"])
    version_v1_id = created.json()["versions"][0]
    version_v1 = client.get(f"{VERSION_API}/{version_v1_id}", headers=context.preparer_headers)
    assert version_v1.status_code == 200, version_v1.text
    assert created.json()["current_version_id"] is None
    before_publish = client.get(
        f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
        headers=headers_a,
    )
    assert before_publish.status_code == 200, before_publish.text
    assert before_publish.json()["available"] is False
    assert before_publish.json()["publication"] is None
    covered.add("PROTO-AT-09")

    submitted_v1 = _submit(client, context, version_v1_id)
    assert submitted_v1.status_code == 200, submitted_v1.text
    same_person_approval = client.post(
        f"{VERSION_API}/{version_v1_id}/decision",
        headers=context.same_person_headers,
        json={"verdict": "APPROVE", "justification": "Synthetic same-person rejection."},
    )
    assert same_person_approval.status_code == 403
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(PublicationApproval)
            .where(PublicationApproval.version_id == UUID(version_v1_id))
        )
        == 0
    )
    approved_v1 = _decide(client, context, version_v1_id)
    assert approved_v1.status_code == 200, approved_v1.text
    covered.add("PROTO-AT-10")

    published_v1 = _publish(client, context, version_v1_id)
    assert published_v1.status_code == 200, published_v1.text
    publication_read = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers
    )
    assert publication_read.status_code == 200, publication_read.text
    assert publication_read.json()["current_version_id"] == version_v1_id
    portal_a_v1 = client.get(
        f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
        headers=headers_a,
    )
    assert portal_a_v1.status_code == 200, portal_a_v1.text
    assert portal_a_v1.json()["available"] is True
    assert portal_a_v1.json()["publication"]["content_text"] == CONTENT_V1
    covered.add("PROTO-AT-11")

    # AT-12 and AT-17: tenant UUID and same-client tracking without scope both return 404.
    portal_b_for_a = client.get(
        f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
        headers=headers_b,
    )
    portal_a_without_a2 = client.get(
        f"{PORTAL_API}/trackings/{tracking_a2_id}/current-publication",
        headers=headers_a,
    )
    assert portal_b_for_a.status_code == portal_a_without_a2.status_code == 404
    assert CONTENT_V1 not in portal_b_for_a.text
    assert portal_b_for_a.json()["detail"] == portal_a_without_a2.json()["detail"]
    covered.update({"PROTO-AT-12", "PROTO-AT-17"})

    # AT-18: a second immutable version needs a separate submit, approval, and publication.
    created_v2 = client.post(
        f"{PUBLICATIONS_API}/{publication_id}/versions",
        headers=context.preparer_headers,
        json={"novelty_ids": [str(context.novelty_id)], "content_text": CONTENT_V2},
    )
    assert created_v2.status_code == 201, created_v2.text
    version_v2_id = created_v2.json()["id"]
    assert created_v2.json()["version_number"] == 2
    assert created_v2.json()["status"] == "DRAFT"
    assert created_v2.json()["content_sha256"] != version_v1.json()["content_sha256"]
    assert (
        client.post(
            f"{VERSION_API}/{version_v2_id}/publish", headers=context.coordinator_headers
        ).status_code
        == 409
    )
    assert (
        client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers).json()[
            "current_version_id"
        ]
        == version_v1_id
    )
    assert _submit(client, context, version_v2_id).status_code == 200
    approved_v2 = _decide(client, context, version_v2_id)
    assert approved_v2.status_code == 200, approved_v2.text
    published_v2 = _publish(client, context, version_v2_id)
    assert published_v2.status_code == 200, published_v2.text
    current_v2 = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers
    )
    assert current_v2.json()["current_version_id"] == version_v2_id
    assert (
        client.get(
            f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
            headers=headers_a,
        ).json()["publication"]["content_text"]
        == CONTENT_V2
    )
    covered.add("PROTO-AT-18")

    # AT-13 and AT-14: current access is re-evaluated; published history remains intact.
    suspended = client.post(
        f"{INTERNAL_API}/clients/{client_a_id}/suspend",
        headers=context.admin_headers,
        json={"reason": SUSPEND_REASON},
    )
    assert suspended.status_code == 200, suspended.text
    assert (
        client.get(
            f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
            headers=headers_a,
        ).status_code
        == 404
    )
    reactivated = client.post(
        f"{INTERNAL_API}/clients/{client_a_id}/reactivate",
        headers=context.admin_headers,
        json={"reason": REACTIVATE_REASON},
    )
    assert reactivated.status_code == 200, reactivated.text
    finished = client.post(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/finish",
        headers=context.admin_headers,
        json={"reason": FINISH_REASON},
    )
    assert finished.status_code == 200, finished.text
    assert (
        client.get(
            f"{PORTAL_API}/trackings/{context.tracking_id}/current-publication",
            headers=headers_a,
        ).status_code
        == 404
    )
    db_session.expire_all()
    publication_row = db_session.get(Publication, publication_id)
    version_row = db_session.get(PublicationVersion, UUID(version_v2_id))
    assert publication_row is not None and publication_row.current_version_id == UUID(version_v2_id)
    assert version_row is not None and version_row.status == "PUBLISHED"
    covered.update({"PROTO-AT-13", "PROTO-AT-14"})

    assert covered == {f"PROTO-AT-{index:02d}" for index in range(1, 19)}
    assert (
        db_session.scalar(
            select(func.count()).select_from(Novelty).where(Novelty.tracking_id == tracking_b_id)
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AcquisitionRun)
            .where(AcquisitionRun.process_id == process_id)
        )
        == 4
    )
