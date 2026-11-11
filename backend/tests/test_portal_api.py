from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from typing import Any
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.acquisitions.models import AcquisitionRun
from app.audit import repository as audit_repository
from app.clients.models import Client
from app.identity.models import Account, AuditEvent
from app.novelties.models import StateTransition
from app.publications.models import Publication, PublicationVersion
from app.trackings.models import ExternalTrackingScope, InternalTrackingAssignment, Tracking
from tests.factories import create_account
from tests.test_novelties_api import INTERNAL_API, PASSWORD, _create_novelty_context, _login
from tests.test_publications_api import (
    CONTENT_V1,
    _create_and_publish,
    _create_publication_context,
)
from tests.traceability import trace_cases

REASON = "Synthetic operator requested this state change."


def _create_tracking(
    client: TestClient,
    db_session: Session,
    *,
    admin: Account,
    admin_headers: dict[str, str],
    client_id: UUID,
    radicado: str,
    label: str,
) -> UUID:
    process = client.post(
        f"{INTERNAL_API}/processes",
        headers=admin_headers,
        json={"radicado": radicado, "label": label},
    )
    assert process.status_code == 201, process.text
    created = client.post(
        f"{INTERNAL_API}/trackings",
        headers=admin_headers,
        json={"client_id": str(client_id), "process_id": process.json()["id"]},
    )
    assert created.status_code == 201, created.text
    tracking_id = UUID(created.json()["id"])
    db_session.add(
        InternalTrackingAssignment(
            account_id=admin.id,
            account_kind="INTERNAL",
            tracking_id=tracking_id,
        )
    )
    db_session.commit()
    activated = client.post(
        f"{INTERNAL_API}/trackings/{tracking_id}/activate",
        headers=admin_headers,
    )
    assert activated.status_code == 200, activated.text
    return tracking_id


def _add_scope(db_session: Session, reader: Account, tracking_id: UUID) -> None:
    assert reader.client_id is not None
    db_session.add(
        ExternalTrackingScope(
            account_id=reader.id,
            account_kind="EXTERNAL",
            client_id=reader.client_id,
            tracking_id=tracking_id,
            permission_code="READ_PUBLICATIONS",
        )
    )


def _problem_identity(response: Any) -> tuple[object, ...]:
    body = response.json()
    return (
        response.status_code,
        response.headers["content-type"].split(";")[0],
        body["type"],
        body["title"],
        body["status"],
        body["detail"],
        body["instance"],
    )


@trace_cases(
    "API-N07",
    "API-N08",
    "API-N11",
    "API-N27",
    "API-N28",
    "API-N36",
    "DT-21",
    "DT-31",
)
def test_portal_filters_tenant_scope_and_reports_current_coverage(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_novelty_context(client, db_session, suffix="inc06-portal-scope")
    tracking_a1 = db_session.get(Tracking, context.tracking_id)
    assert tracking_a1 is not None
    client_a_id = tracking_a1.client_id
    reader_a = create_account(
        db_session,
        username="reader.inc06-alfa",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=client_a_id,
    )
    reader_b = create_account(
        db_session,
        username="reader.inc06-beta",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
    )
    assert reader_b.client_id is not None

    tracking_a2 = _create_tracking(
        client,
        db_session,
        admin=context.admin,
        admin_headers=context.admin_headers,
        client_id=client_a_id,
        radicado="00000000000000000000002",
        label="Synthetic Alfa tracking without external scope",
    )
    tracking_a3 = _create_tracking(
        client,
        db_session,
        admin=context.admin,
        admin_headers=context.admin_headers,
        client_id=client_a_id,
        radicado="00000000000000000000003",
        label="Synthetic second scoped Alfa tracking",
    )
    tracking_b1 = _create_tracking(
        client,
        db_session,
        admin=context.admin,
        admin_headers=context.admin_headers,
        client_id=reader_b.client_id,
        radicado="00000000000000000000004",
        label="Synthetic Beta tracking",
    )
    _add_scope(db_session, reader_a, context.tracking_id)
    _add_scope(db_session, reader_a, tracking_a3)
    _add_scope(db_session, reader_b, tracking_b1)
    db_session.commit()
    headers_a = _login(client, reader_a.username)
    headers_b = _login(client, reader_b.username)

    first_page = client.get("/api/v1/portal/trackings?limit=1", headers=headers_a)
    assert first_page.status_code == 200, first_page.text
    assert len(first_page.json()["items"]) == 1
    assert first_page.json()["next_cursor"]
    second_page = client.get(
        "/api/v1/portal/trackings?limit=1",
        headers=headers_a,
        params={"cursor": first_page.json()["next_cursor"]},
    )
    assert second_page.status_code == 200, second_page.text
    assert second_page.json()["next_cursor"] is None
    listed_ids = {
        UUID(item["id"]) for item in first_page.json()["items"] + second_page.json()["items"]
    }
    assert listed_ids == {context.tracking_id, tracking_a3}
    coverage_by_id = {
        UUID(item["id"]): item["coverage_status"]
        for item in first_page.json()["items"] + second_page.json()["items"]
    }
    assert coverage_by_id[context.tracking_id] == "COMPARABLE"
    assert coverage_by_id[tracking_a3] == "NOT_OBSERVED"

    no_scope = client.get(
        f"/api/v1/portal/trackings/{tracking_a2}/current-publication", headers=headers_a
    )
    nonexistent = client.get(
        f"/api/v1/portal/trackings/{uuid4()}/current-publication", headers=headers_a
    )
    assert no_scope.status_code == nonexistent.status_code == 404
    assert _problem_identity(no_scope) == _problem_identity(nonexistent)
    foreign = client.get(
        f"/api/v1/portal/trackings/{context.tracking_id}/current-publication", headers=headers_b
    )
    missing_for_beta = client.get(
        f"/api/v1/portal/trackings/{uuid4()}/current-publication", headers=headers_b
    )
    assert _problem_identity(foreign) == _problem_identity(missing_for_beta)
    assert foreign.headers["content-type"].startswith("application/problem+json")
    assert (
        client.get(
            "/api/v1/portal/trackings", headers=headers_b, params={"client_id": str(client_a_id)}
        ).status_code
        == 422
    )

    unavailable = client.get(
        f"/api/v1/portal/trackings/{context.tracking_id}/current-publication", headers=headers_a
    )
    assert unavailable.status_code == 200
    assert unavailable.json() == {
        "available": False,
        "coverage_status": "COMPARABLE",
        "publication": None,
    }

    for fixture_code, expected_coverage in (("INCOMPLETE", "INCOMPLETE"), ("FAILED", "FAILED")):
        acquired = client.post(
            f"{INTERNAL_API}/acquisition-runs",
            headers=context.analyst_headers,
            json={
                "process_id": str(context.process_id),
                "fixture_code": fixture_code,
                "request_key": f"inc06-{fixture_code.lower()}-coverage",
            },
        )
        assert acquired.status_code == 201, acquired.text
        coverage = client.get(
            f"/api/v1/portal/trackings/{context.tracking_id}/current-publication",
            headers=headers_a,
        )
        assert coverage.status_code == 200, coverage.text
        assert coverage.json()["coverage_status"] == expected_coverage
        listed = client.get("/api/v1/portal/trackings", headers=headers_a)
        assert expected_coverage in {item["coverage_status"] for item in listed.json()["items"]}

    denial = db_session.scalar(
        select(AuditEvent).where(AuditEvent.request_id == UUID(foreign.headers["x-request-id"]))
    )
    assert denial is not None
    assert denial.result == "DENIED"
    assert denial.resource_id is None
    assert denial.sanitized_reason == "resource_not_in_scope"
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(AcquisitionRun)
            .where(AcquisitionRun.status == "FAILED")
        )
        == 1
    )


@trace_cases("API-N09", "API-N10", "DT-32", "DT-33")
def test_suspension_reactivation_and_finish_gate_portal_without_removing_publication(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc06-state-flow")
    publication, version = _create_and_publish(client, context)
    tracking = db_session.get(Tracking, context.tracking_id)
    assert tracking is not None
    reader = create_account(
        db_session,
        username="reader.inc06-state-flow",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=tracking.client_id,
    )
    _add_scope(db_session, reader, context.tracking_id)
    beta_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=context.admin_headers,
        json={"client_code": "beta-inc06-state-flow", "name": "Synthetic client Beta"},
    )
    assert beta_client.status_code == 201, beta_client.text
    beta_client_id = UUID(beta_client.json()["id"])
    context.external_reader.client_id = beta_client_id
    db_session.commit()
    external_headers = _login(client, reader.username)
    portal_url = f"/api/v1/portal/trackings/{context.tracking_id}/current-publication"
    beta_tracking = _create_tracking(
        client,
        db_session,
        admin=context.admin,
        admin_headers=context.admin_headers,
        client_id=beta_client_id,
        radicado="00000000000000000000002",
        label="Synthetic Beta scope for publication isolation",
    )
    _add_scope(db_session, context.external_reader, beta_tracking)
    db_session.commit()

    before_suspend = client.get(portal_url, headers=external_headers)
    assert before_suspend.status_code == 200
    assert before_suspend.json()["available"] is True
    assert before_suspend.json()["publication"]["version_id"] == version["id"]
    assert before_suspend.json()["publication"]["content_text"] == CONTENT_V1
    portal_list = client.get("/api/v1/portal/trackings", headers=external_headers)
    assert portal_list.status_code == 200
    assert portal_list.json()["items"] == [
        {
            "id": str(context.tracking_id),
            "tracking_code": "SEG-A-001",
            "has_publication": True,
            "coverage_status": "COMPARABLE",
            "radicado": "00000000000000000000001",
        }
    ]
    foreign = client.get(
        f"/api/v1/portal/trackings/{context.tracking_id}/current-publication",
        headers=context.external_headers,
    )
    missing_for_beta = client.get(
        f"/api/v1/portal/trackings/{uuid4()}/current-publication",
        headers=context.external_headers,
    )
    assert _problem_identity(foreign) == _problem_identity(missing_for_beta)
    assert CONTENT_V1 not in foreign.text

    suspend_url = f"{INTERNAL_API}/clients/{reader.client_id}/suspend"
    invalid_role = client.post(
        suspend_url, headers=context.analyst_headers, json={"reason": REASON}
    )
    assert invalid_role.status_code == 403
    assert (
        client.post(suspend_url, headers=external_headers, json={"reason": REASON}).status_code
        == 403
    )
    assert client.post(suspend_url, headers=context.admin_headers, json={}).status_code == 422
    assert (
        client.post(
            suspend_url, headers=context.admin_headers, json={"reason": "        "}
        ).status_code
        == 422
    )

    suspended = client.post(suspend_url, headers=context.admin_headers, json={"reason": REASON})
    assert suspended.status_code == 200, suspended.text
    assert suspended.json()["status"] == "SUSPENDED"
    suspended_request_id = UUID(suspended.headers["x-request-id"])
    after_suspend = client.get(portal_url, headers=external_headers)
    assert after_suspend.status_code == 404
    assert client.get("/api/v1/portal/trackings", headers=external_headers).json()["items"] == []
    assert (
        client.post(suspend_url, headers=context.admin_headers, json={"reason": REASON}).status_code
        == 409
    )

    version_id = UUID(str(version["id"]))
    publication_id = UUID(str(publication["id"]))
    db_session.expire_all()
    published_row = db_session.get(PublicationVersion, version_id)
    publication_row = db_session.get(Publication, publication_id)
    assert published_row is not None and published_row.status == "PUBLISHED"
    assert publication_row is not None and publication_row.current_version_id == version_id

    reactivated = client.post(
        f"{INTERNAL_API}/clients/{reader.client_id}/reactivate",
        headers=context.admin_headers,
        json={"reason": "Synthetic verification completed; restore client access."},
    )
    assert reactivated.status_code == 200, reactivated.text
    assert reactivated.json()["status"] == "ACTIVE"
    reactivated_request_id = UUID(reactivated.headers["x-request-id"])
    assert client.get(portal_url, headers=external_headers).json()["available"] is True

    finished = client.post(
        f"{INTERNAL_API}/trackings/{context.tracking_id}/finish",
        headers=context.admin_headers,
        json={"reason": "Synthetic monitoring scope has been completed."},
    )
    assert finished.status_code == 200, finished.text
    assert finished.json()["status"] == "FINISHED"
    finished_request_id = UUID(finished.headers["x-request-id"])
    after_finish = client.get(portal_url, headers=external_headers)
    assert after_finish.status_code == 404
    assert client.get("/api/v1/portal/trackings", headers=external_headers).json()["items"] == []

    db_session.expire_all()
    assert db_session.get(PublicationVersion, version_id).status == "PUBLISHED"
    assert db_session.get(Publication, publication_id).current_version_id == version_id
    transitions = tuple(
        db_session.scalars(
            select(StateTransition)
            .where(
                StateTransition.request_id.in_(
                    (suspended_request_id, reactivated_request_id, finished_request_id)
                )
            )
            .order_by(StateTransition.occurred_at, StateTransition.id)
        )
    )
    assert {(item.from_state, item.to_state) for item in transitions} == {
        ("ACTIVE", "SUSPENDED"),
        ("SUSPENDED", "ACTIVE"),
        ("ACTIVE", "FINISHED"),
    }
    assert all(item.actor_account_id == context.admin.id for item in transitions)
    assert all(item.reason for item in transitions)
    assert {item.reason for item in transitions} == {
        REASON,
        "Synthetic verification completed; restore client access.",
        "Synthetic monitoring scope has been completed.",
    }
    audit_events = tuple(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.request_id.in_(
                    (suspended_request_id, reactivated_request_id, finished_request_id)
                ),
                AuditEvent.result == "SUCCESS",
            )
        )
    )
    assert {item.event_code for item in audit_events} == {
        "CLIENT_SUSPEND",
        "CLIENT_REACTIVATE",
        "TRACKING_FINISH",
    }
    assert {item.resource_id for item in audit_events} == {reader.client_id, context.tracking_id}


@trace_cases("DT-36")
def test_state_transition_and_audit_roll_back_together(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    _requirement_ids: tuple[str, ...],
) -> None:
    context = _create_novelty_context(client, db_session, suffix="inc06-rollback")
    tracking = db_session.get(Tracking, context.tracking_id)
    assert tracking is not None
    client_id = tracking.client_id

    def fail_transition(*args: object, **kwargs: object) -> None:
        raise IntegrityError("injected transition write failure", {}, RuntimeError("synthetic"))

    monkeypatch.setattr(audit_repository, "add_state_transition", fail_transition)
    failed = client.post(
        f"{INTERNAL_API}/clients/{client_id}/suspend",
        headers=context.admin_headers,
        json={"reason": REASON},
    )
    assert failed.status_code == 409
    db_session.expire_all()
    assert db_session.get(Client, client_id).status == "ACTIVE"
    assert (
        db_session.scalar(
            select(func.count()).where(
                AuditEvent.request_id == UUID(failed.headers["x-request-id"]),
                AuditEvent.event_code == "CLIENT_SUSPEND",
                AuditEvent.result == "SUCCESS",
            )
        )
        == 0
    )
    assert (
        db_session.scalar(select(func.count()).where(StateTransition.client_id == client_id)) == 0
    )


@trace_cases("API-N35")
def test_parallel_publish_and_suspend_cannot_restore_portal_access(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc06-race")
    created = client.post(
        f"{INTERNAL_API}/publications",
        headers=context.preparer_headers,
        json={
            "tracking_id": str(context.tracking_id),
            "novelty_ids": [str(context.novelty_id)],
            "content_text": CONTENT_V1,
        },
    )
    assert created.status_code == 201, created.text
    version_id = created.json()["versions"][0]
    assert (
        client.post(
            f"{INTERNAL_API}/publication-versions/{version_id}/submit",
            headers=context.preparer_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"{INTERNAL_API}/publication-versions/{version_id}/decision",
            headers=context.coordinator_headers,
            json={"verdict": "APPROVE", "justification": "Synthetic concurrent status test."},
        ).status_code
        == 200
    )

    tracking = db_session.get(Tracking, context.tracking_id)
    assert tracking is not None
    reader = create_account(
        db_session,
        username="reader.inc06-race",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
        client_id=tracking.client_id,
    )
    _add_scope(db_session, reader, context.tracking_id)
    db_session.commit()
    external_headers = _login(client, reader.username)
    draft_absence = client.get(
        f"/api/v1/portal/trackings/{context.tracking_id}/current-publication",
        headers=external_headers,
    )
    assert draft_absence.status_code == 200, draft_absence.text
    assert draft_absence.json() == {
        "available": False,
        "coverage_status": "COMPARABLE",
        "publication": None,
    }
    barrier = Barrier(2)

    def publish() -> Any:
        barrier.wait()
        return client.post(
            f"{INTERNAL_API}/publication-versions/{version_id}/publish",
            headers=context.coordinator_headers,
        )

    def suspend() -> Any:
        barrier.wait()
        return client.post(
            f"{INTERNAL_API}/clients/{reader.client_id}/suspend",
            headers=context.admin_headers,
            json={"reason": "Synthetic concurrent suspension check."},
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        publication_future = executor.submit(publish)
        suspension_future = executor.submit(suspend)
        publication_result = publication_future.result(timeout=20)
        suspension_result = suspension_future.result(timeout=20)

    assert publication_result.status_code in {200, 409}, publication_result.text
    assert suspension_result.status_code == 200, suspension_result.text
    denied_after_commit = client.get(
        f"/api/v1/portal/trackings/{context.tracking_id}/current-publication",
        headers=external_headers,
    )
    assert denied_after_commit.status_code == 404
