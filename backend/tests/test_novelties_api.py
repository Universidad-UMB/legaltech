from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.identity.models import Account, AuditEvent
from app.novelties import repository as novelty_repository
from app.novelties.models import Novelty, NoveltyReview, StateTransition
from app.trackings.models import InternalTrackingAssignment
from tests.conftest import TEST_MIGRATION_SESSION_FACTORY
from tests.factories import create_account

INTERNAL_API = "/api/v1/internal"
PASSWORD = "Synthetic-Test-Passphrase-2026!"


@dataclass(frozen=True)
class NoveltyContext:
    tracking_id: UUID
    process_id: UUID
    old_observation_id: UUID
    new_observation_id: UUID
    novelty_id: UUID
    admin: Account
    analyst: Account
    lawyer: Account
    admin_headers: dict[str, str]
    analyst_headers: dict[str, str]
    lawyer_headers: dict[str, str]


def _login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/sessions",
        json={"username": username, "password": PASSWORD},
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_novelty_context(
    client: TestClient, db_session: Session, *, suffix: str
) -> NoveltyContext:
    admin = create_account(db_session, username=f"admin.{suffix}", password=PASSWORD)
    analyst = create_account(
        db_session,
        username=f"analyst.{suffix}",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    lawyer = create_account(
        db_session,
        username=f"lawyer.{suffix}",
        password=PASSWORD,
        roles=("LAWYER",),
    )
    admin_headers = _login(client, f"admin.{suffix}")
    analyst_headers = _login(client, f"analyst.{suffix}")
    lawyer_headers = _login(client, f"lawyer.{suffix}")

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
                account_id=account.id,
                account_kind="INTERNAL",
                tracking_id=tracking_id,
            )
            for account in (admin, analyst, lawyer)
        ]
    )
    db_session.commit()
    activated = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/activate", headers=admin_headers
    )
    assert activated.status_code == 200, activated.text

    observation_ids: list[UUID] = []
    for fixture_code in ("OBS_001", "OBS_002"):
        acquisition = client.post(
            f"{INTERNAL_API}/acquisition-runs",
            headers=analyst_headers,
            json={
                "process_id": str(process_id),
                "fixture_code": fixture_code,
                "request_key": f"inc04-{suffix}-{fixture_code.lower()}-key",
            },
        )
        assert acquisition.status_code == 201, acquisition.text
        observation_ids.append(UUID(acquisition.json()["observation_id"]))

    baseline = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/adoptions",
        headers=analyst_headers,
        json={"observation_id": str(observation_ids[0])},
    )
    assert baseline.status_code == 200, baseline.text
    comparison = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=analyst_headers,
        json={
            "old_observation_id": str(observation_ids[0]),
            "new_observation_id": str(observation_ids[1]),
            "rule_version": "demo-v1",
        },
    )
    assert comparison.status_code == 201, comparison.text
    evaluation = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/evaluations",
        headers=analyst_headers,
        json={"comparison_id": comparison.json()["id"]},
    )
    assert evaluation.status_code == 201, evaluation.text
    assert len(evaluation.json()["novelty_ids"]) == 1
    return NoveltyContext(
        tracking_id=tracking_id,
        process_id=process_id,
        old_observation_id=observation_ids[0],
        new_observation_id=observation_ids[1],
        novelty_id=UUID(evaluation.json()["novelty_ids"][0]),
        admin=admin,
        analyst=analyst,
        lawyer=lawyer,
        admin_headers=admin_headers,
        analyst_headers=analyst_headers,
        lawyer_headers=lawyer_headers,
    )


def test_assigned_analyst_and_distinct_lawyer_create_audited_reviews(
    client: TestClient, db_session: Session
) -> None:
    context = _create_novelty_context(client, db_session, suffix="inc04-flow")
    novelty_path = f"{INTERNAL_API}/novelties/{context.novelty_id}"
    initial = client.get(novelty_path, headers=context.analyst_headers)
    assert initial.status_code == 200
    assert initial.json()["status"] == "PENDING_OPERATIVE"
    assert set(initial.json()) == {"id", "novelty_code", "tracking_id", "status", "change_id"}

    initial_list = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties",
        headers=context.analyst_headers,
    )
    assert initial_list.status_code == 200
    assert initial_list.json()["items"] == [initial.json()]
    assert initial_list.json()["next_cursor"] is None
    list_audit = db_session.scalar(
        select(AuditEvent).where(
            AuditEvent.request_id == UUID(initial_list.headers["x-request-id"])
        )
    )
    assert list_audit is not None
    assert list_audit.event_code == "NOVELTY_LIST"
    assert list_audit.resource_kind == "TRACKING"
    assert list_audit.resource_id == context.tracking_id
    assert list_audit.actor_account_id == context.analyst.id

    wrong_role_start = client.post(
        f"{novelty_path}/start-operative-review", headers=context.lawyer_headers
    )
    assert wrong_role_start.status_code == 403
    assert wrong_role_start.headers["content-type"].startswith("application/problem+json")

    started = client.post(f"{novelty_path}/start-operative-review", headers=context.analyst_headers)
    assert started.status_code == 200, started.text
    assert started.json()["status"] == "IN_OPERATIVE_REVIEW"
    started_request_id = UUID(started.headers["x-request-id"])

    decision = "The synthetic entry matches the observed process record."
    evidence = "Fixture ACT-06 was checked against the prior snapshot."
    escalated = client.post(
        f"{novelty_path}/escalate",
        headers=context.analyst_headers,
        json={"decision": decision, "evidence_note": evidence},
    )
    assert escalated.status_code == 200, escalated.text
    assert escalated.json()["status"] == "PENDING_LEGAL"
    operative_request_id = UUID(escalated.headers["x-request-id"])

    wrong_role_legal = client.post(
        f"{novelty_path}/legal-review",
        headers=context.analyst_headers,
        json={
            "decision": "A synthetic legal review was completed.",
            "evidence_note": "The fixture contains no real legal records.",
        },
    )
    assert wrong_role_legal.status_code == 403
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(NoveltyReview)
            .where(
                NoveltyReview.novelty_id == context.novelty_id,
                NoveltyReview.review_kind == "LEGAL",
            )
        )
        == 0
    )

    legal_decision = "The synthetic notice is suitable for internal treatment."
    legal_evidence = "Human review of fixture content completed for the demo."
    legal_review = client.post(
        f"{novelty_path}/legal-review",
        headers=context.lawyer_headers,
        json={"decision": legal_decision, "evidence_note": legal_evidence},
    )
    assert legal_review.status_code == 200, legal_review.text
    assert legal_review.json()["status"] == "TREATMENT_DEFINED"
    legal_request_id = UUID(legal_review.headers["x-request-id"])

    reviews = tuple(
        db_session.scalars(
            select(NoveltyReview)
            .where(NoveltyReview.novelty_id == context.novelty_id)
            .order_by(NoveltyReview.review_kind)
        )
    )
    operative = next(review for review in reviews if review.review_kind == "OPERATIVE")
    legal = next(review for review in reviews if review.review_kind == "LEGAL")
    assert operative.actor_account_id == context.analyst.id
    assert operative.actor_person_id == context.analyst.person_id
    assert operative.decision == decision
    assert operative.evidence_note == evidence
    assert legal.actor_account_id == context.lawyer.id
    assert legal.actor_person_id == context.lawyer.person_id
    assert legal.actor_person_id != operative.actor_person_id
    assert legal.decision == legal_decision
    assert legal.evidence_note == legal_evidence

    transitions = tuple(
        db_session.scalars(
            select(StateTransition)
            .where(StateTransition.novelty_id == context.novelty_id)
            .order_by(StateTransition.occurred_at, StateTransition.id)
        )
    )
    assert [(item.from_state, item.to_state) for item in transitions] == [
        ("PENDING_OPERATIVE", "IN_OPERATIVE_REVIEW"),
        ("IN_OPERATIVE_REVIEW", "PENDING_LEGAL"),
        ("PENDING_LEGAL", "TREATMENT_DEFINED"),
    ]
    assert [item.actor_person_id for item in transitions] == [
        context.analyst.person_id,
        context.analyst.person_id,
        context.lawyer.person_id,
    ]
    assert transitions[0].request_id == started_request_id
    assert transitions[1].request_id == operative_request_id
    assert transitions[2].request_id == legal_request_id

    events = tuple(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.resource_id == context.novelty_id,
                AuditEvent.result == "SUCCESS",
            )
        )
    )
    assert {event.event_code for event in events} == {
        "NOVELTY_GET",
        "NOVELTY_START_OPERATIVE_REVIEW",
        "NOVELTY_ESCALATE",
        "NOVELTY_LEGAL_REVIEW",
    }
    assert all(decision not in (event.sanitized_reason or "") for event in events)
    assert all(evidence not in (event.sanitized_reason or "") for event in events)

    illegal_repeat = client.post(
        f"{novelty_path}/legal-review",
        headers=context.lawyer_headers,
        json={"decision": legal_decision, "evidence_note": legal_evidence},
    )
    assert illegal_repeat.status_code == 409
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(NoveltyReview)
            .where(NoveltyReview.novelty_id == context.novelty_id)
        )
        == 2
    )
    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text("UPDATE novelty_reviews SET decision = 'changed' WHERE id = :review_id"),
                {"review_id": legal.id},
            )
            owner_session.flush()
        owner_session.rollback()


def test_wrong_role_scope_states_and_request_validation_are_enforced(
    client: TestClient, db_session: Session
) -> None:
    context = _create_novelty_context(client, db_session, suffix="inc04-guards")
    novelty_path = f"{INTERNAL_API}/novelties/{context.novelty_id}"
    outsider = create_account(
        db_session,
        username="analyst.inc04-unassigned",
        password=PASSWORD,
        roles=("ANALYST",),
    )
    outsider_headers = _login(client, "analyst.inc04-unassigned")

    for response in (
        client.get(novelty_path, headers=outsider_headers),
        client.get(
            f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties",
            headers=outsider_headers,
        ),
        client.post(f"{novelty_path}/start-operative-review", headers=outsider_headers),
    ):
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("application/problem+json")

    escalation_body = {
        "decision": "Synthetic review decision recorded.",
        "evidence_note": "Synthetic evidence was checked manually.",
    }
    legal_body = {
        "decision": "Synthetic legal review recorded.",
        "evidence_note": "No real legal documents were used.",
    }
    early_escalation = client.post(
        f"{novelty_path}/escalate",
        headers=context.analyst_headers,
        json=escalation_body,
    )
    early_legal_review = client.post(
        f"{novelty_path}/legal-review",
        headers=context.lawyer_headers,
        json=legal_body,
    )
    assert early_escalation.status_code == 409
    assert early_legal_review.status_code == 409
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(StateTransition)
            .where(StateTransition.novelty_id == context.novelty_id)
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(NoveltyReview)
            .where(NoveltyReview.novelty_id == context.novelty_id)
        )
        == 0
    )

    extra_field = client.post(
        f"{novelty_path}/escalate",
        headers=context.analyst_headers,
        json={**escalation_body, "actor_account_id": str(outsider.id)},
    )
    too_short = client.post(
        f"{novelty_path}/legal-review",
        headers=context.lawyer_headers,
        json={"decision": "short", "evidence_note": "This evidence is long enough."},
    )
    assert extra_field.status_code == 422
    assert too_short.status_code == 422
    assert extra_field.headers["content-type"].startswith("application/problem+json")
    assert (
        client.get(
            f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties?limit=0",
            headers=context.analyst_headers,
        ).status_code
        == 422
    )
    assert (
        client.get(
            f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties?cursor=not-a-cursor",
            headers=context.analyst_headers,
        ).status_code
        == 422
    )

    started = client.post(f"{novelty_path}/start-operative-review", headers=context.analyst_headers)
    assert started.status_code == 200
    repeated_start = client.post(
        f"{novelty_path}/start-operative-review", headers=context.analyst_headers
    )
    assert repeated_start.status_code == 409
    assert db_session.get(Novelty, context.novelty_id).status == "IN_OPERATIVE_REVIEW"

    denial_events = tuple(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.actor_account_id == outsider.id,
                AuditEvent.result == "DENIED",
            )
        )
    )
    assert len(denial_events) == 3
    assert all(event.resource_id is None for event in denial_events)
    assert all(event.sanitized_reason == "resource_not_in_scope" for event in denial_events)


def test_novelty_list_uses_stable_keyset_cursors_and_transition_rollback(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    context = _create_novelty_context(client, db_session, suffix="inc04-pages")
    second_comparison = client.post(
        f"{INTERNAL_API}/comparisons",
        headers=context.analyst_headers,
        json={
            "old_observation_id": str(context.old_observation_id),
            "new_observation_id": str(context.new_observation_id),
            "rule_version": "demo-v2",
        },
    )
    assert second_comparison.status_code == 201, second_comparison.text
    second_evaluation = client.post(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/evaluations",
        headers=context.analyst_headers,
        json={"comparison_id": second_comparison.json()["id"]},
    )
    assert second_evaluation.status_code == 201, second_evaluation.text
    assert len(second_evaluation.json()["novelty_ids"]) == 1

    first_page = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties?limit=1",
        headers=context.analyst_headers,
    )
    assert first_page.status_code == 200, first_page.text
    assert len(first_page.json()["items"]) == 1
    cursor = first_page.json()["next_cursor"]
    assert isinstance(cursor, str) and cursor
    second_page = client.get(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/novelties",
        headers=context.analyst_headers,
        params={"limit": 1, "cursor": cursor},
    )
    assert second_page.status_code == 200, second_page.text
    assert len(second_page.json()["items"]) == 1
    assert second_page.json()["next_cursor"] is None
    assert first_page.json()["items"][0]["id"] != second_page.json()["items"][0]["id"]

    def fail_review_insert(*args: object, **kwargs: object) -> NoveltyReview:
        raise IntegrityError("synthetic failure", {}, RuntimeError("injected rollback test"))

    monkeypatch.setattr(novelty_repository, "add_review", fail_review_insert)
    novelty_path = f"{INTERNAL_API}/novelties/{context.novelty_id}"
    started = client.post(f"{novelty_path}/start-operative-review", headers=context.analyst_headers)
    assert started.status_code == 200
    escalation = client.post(
        f"{novelty_path}/escalate",
        headers=context.analyst_headers,
        json={
            "decision": "Synthetic rollback decision.",
            "evidence_note": "Synthetic rollback evidence.",
        },
    )
    assert escalation.status_code == 409
    db_session.expire_all()
    novelty = db_session.get(Novelty, context.novelty_id)
    assert novelty is not None and novelty.status == "IN_OPERATIVE_REVIEW"
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(StateTransition)
            .where(StateTransition.novelty_id == context.novelty_id)
        )
        == 1
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(NoveltyReview)
            .where(NoveltyReview.novelty_id == context.novelty_id)
        )
        == 0
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AuditEvent)
            .where(
                AuditEvent.resource_id == context.novelty_id,
                AuditEvent.event_code == "NOVELTY_ESCALATE",
                AuditEvent.result == "SUCCESS",
            )
        )
        == 0
    )

    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text("UPDATE state_transitions SET reason = 'changed' WHERE novelty_id = :id"),
                {"id": context.novelty_id},
            )
            owner_session.flush()
        owner_session.rollback()
