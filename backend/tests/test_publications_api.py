from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.identity.models import Account, AccountRole, AuditEvent
from app.identity.service import IdentityService
from app.novelties.models import Novelty, StateTransition
from app.publications import repository as publication_repository
from app.publications.domain import content_sha256
from app.publications.models import (
    Publication,
    PublicationApproval,
    PublicationPreparer,
    PublicationVersion,
    PublicationVersionNovelty,
)
from app.trackings.models import InternalTrackingAssignment
from tests.conftest import TEST_MIGRATION_SESSION_FACTORY, TEST_SESSION_FACTORY
from tests.factories import create_account
from tests.test_novelties_api import INTERNAL_API, PASSWORD, _create_novelty_context, _login
from tests.traceability import trace_cases

PUBLICATIONS_API = f"{INTERNAL_API}/publications"
VERSION_API = f"{INTERNAL_API}/publication-versions"
CONTENT_V1 = "Synthetic notice for the reviewed fixture ACT-06."
CONTENT_V2 = "Synthetic corrected notice for the same reviewed fixture."
JUSTIFICATION = "Independent coordinator reviewed the exact synthetic snapshot."


@dataclass(frozen=True)
class PublicationContext:
    tracking_id: UUID
    novelty_id: UUID
    admin: Account
    analyst: Account
    preparer: Account
    same_person_coordinator: Account
    coordinator: Account
    secondary_preparer: Account
    secondary_coordinator: Account
    outsider_preparer: Account
    external_reader: Account
    admin_headers: dict[str, str]
    analyst_headers: dict[str, str]
    preparer_headers: dict[str, str]
    same_person_headers: dict[str, str]
    coordinator_headers: dict[str, str]
    secondary_preparer_headers: dict[str, str]
    secondary_coordinator_headers: dict[str, str]
    outsider_headers: dict[str, str]
    external_headers: dict[str, str]


def _same_person_account(session: Session, *, username: str, person_id: UUID, role: str) -> Account:
    account = Account(
        id=uuid4(),
        person_id=person_id,
        username=username,
        password_hash=IdentityService().hash_password(PASSWORD),
        account_kind="INTERNAL",
        client_id=None,
        status="ACTIVE",
    )
    session.add(account)
    session.flush()
    session.add(AccountRole(account_id=account.id, account_kind="INTERNAL", role_code=role))
    session.commit()
    session.refresh(account)
    return account


def _create_publication_context(
    client: TestClient,
    db_session: Session,
    *,
    suffix: str,
    finish_legal_review: bool = True,
) -> PublicationContext:
    novelty_context = _create_novelty_context(client, db_session, suffix=suffix)
    preparer = create_account(
        db_session,
        username=f"preparer.{suffix}",
        password=PASSWORD,
        roles=("PREPARER",),
    )
    same_person_coordinator = _same_person_account(
        db_session,
        username=f"preparer.alt.{suffix}",
        person_id=preparer.person_id,
        role="COORDINATOR",
    )
    coordinator = create_account(
        db_session,
        username=f"coordinator.{suffix}",
        password=PASSWORD,
        roles=("COORDINATOR",),
    )
    secondary_preparer = create_account(
        db_session,
        username=f"preparer.secondary.{suffix}",
        password=PASSWORD,
        roles=("PREPARER",),
    )
    secondary_coordinator = _same_person_account(
        db_session,
        username=f"coordinator.secondary.{suffix}",
        person_id=secondary_preparer.person_id,
        role="COORDINATOR",
    )
    outsider_preparer = create_account(
        db_session,
        username=f"preparer.outsider.{suffix}",
        password=PASSWORD,
        roles=("PREPARER",),
    )
    external_reader = create_account(
        db_session,
        username=f"reader.external.{suffix}",
        password=PASSWORD,
        roles=("EXTERNAL_READER",),
        account_kind="EXTERNAL",
    )
    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=account.id,
                account_kind="INTERNAL",
                tracking_id=novelty_context.tracking_id,
            )
            for account in (
                preparer,
                same_person_coordinator,
                coordinator,
                secondary_preparer,
                secondary_coordinator,
            )
        ]
    )
    db_session.commit()

    if finish_legal_review:
        novelty_path = f"{INTERNAL_API}/novelties/{novelty_context.novelty_id}"
        started = client.post(
            f"{novelty_path}/start-operative-review", headers=novelty_context.analyst_headers
        )
        assert started.status_code == 200, started.text
        escalated = client.post(
            f"{novelty_path}/escalate",
            headers=novelty_context.analyst_headers,
            json={
                "decision": "Synthetic fixture review was completed by the assigned analyst.",
                "evidence_note": "The observed ACT-06 key was checked against the fixture.",
            },
        )
        assert escalated.status_code == 200, escalated.text
        reviewed = client.post(
            f"{novelty_path}/legal-review",
            headers=novelty_context.lawyer_headers,
            json={
                "decision": "Human review recorded for the synthetic notice.",
                "evidence_note": "No real judicial record or personal data was used.",
            },
        )
        assert reviewed.status_code == 200, reviewed.text

    return PublicationContext(
        tracking_id=novelty_context.tracking_id,
        novelty_id=novelty_context.novelty_id,
        admin=novelty_context.admin,
        analyst=novelty_context.analyst,
        preparer=preparer,
        same_person_coordinator=same_person_coordinator,
        coordinator=coordinator,
        secondary_preparer=secondary_preparer,
        secondary_coordinator=secondary_coordinator,
        outsider_preparer=outsider_preparer,
        external_reader=external_reader,
        admin_headers=novelty_context.admin_headers,
        analyst_headers=novelty_context.analyst_headers,
        preparer_headers=_login(client, f"preparer.{suffix}"),
        same_person_headers=_login(client, f"preparer.alt.{suffix}"),
        coordinator_headers=_login(client, f"coordinator.{suffix}"),
        secondary_preparer_headers=_login(client, f"preparer.secondary.{suffix}"),
        secondary_coordinator_headers=_login(client, f"coordinator.secondary.{suffix}"),
        outsider_headers=_login(client, f"preparer.outsider.{suffix}"),
        external_headers=_login(client, f"reader.external.{suffix}"),
    )


def _assign_beta_tracking(
    client: TestClient, db_session: Session, context: PublicationContext, *, suffix: str
) -> UUID:
    beta_client = client.post(
        f"{INTERNAL_API}/clients",
        headers=context.admin_headers,
        json={"client_code": f"beta-{suffix}", "name": "Synthetic client Beta"},
    )
    assert beta_client.status_code == 201, beta_client.text
    beta_client_id = beta_client.json()["id"]
    beta_process = client.post(
        f"{INTERNAL_API}/processes",
        headers=context.admin_headers,
        json={"radicado": "00000000000000000000002", "label": "Beta fixture process"},
    )
    assert beta_process.status_code == 201, beta_process.text
    beta_tracking = client.post(
        f"{INTERNAL_API}/trackings",
        headers=context.admin_headers,
        json={"client_id": beta_client_id, "process_id": beta_process.json()["id"]},
    )
    assert beta_tracking.status_code == 201, beta_tracking.text
    beta_tracking_id = UUID(beta_tracking.json()["id"])
    db_session.add_all(
        [
            InternalTrackingAssignment(
                account_id=account_id,
                account_kind="INTERNAL",
                tracking_id=beta_tracking_id,
            )
            for account_id in (context.admin.id, context.outsider_preparer.id)
        ]
    )
    db_session.commit()
    activated = client.post(
        f"{INTERNAL_API}/trackings/{beta_tracking_id}/activate",
        headers=context.admin_headers,
    )
    assert activated.status_code == 200, activated.text
    return beta_tracking_id


def _create_publication(
    client: TestClient,
    context: PublicationContext,
    *,
    content_text: str = CONTENT_V1,
    headers: dict[str, str] | None = None,
):
    return client.post(
        PUBLICATIONS_API,
        headers=headers or context.preparer_headers,
        json={
            "tracking_id": str(context.tracking_id),
            "novelty_ids": [str(context.novelty_id)],
            "content_text": content_text,
        },
    )


def _submit(client: TestClient, context: PublicationContext, version_id: str):
    return client.post(f"{VERSION_API}/{version_id}/submit", headers=context.preparer_headers)


def _decide(client: TestClient, context: PublicationContext, version_id: str):
    return client.post(
        f"{VERSION_API}/{version_id}/decision",
        headers=context.coordinator_headers,
        json={"verdict": "APPROVE", "justification": JUSTIFICATION},
    )


def _publish(client: TestClient, context: PublicationContext, version_id: str):
    return client.post(f"{VERSION_API}/{version_id}/publish", headers=context.coordinator_headers)


def _create_and_publish(
    client: TestClient, context: PublicationContext, *, content_text: str = CONTENT_V1
) -> tuple[dict[str, object], dict[str, object]]:
    created = _create_publication(client, context, content_text=content_text)
    assert created.status_code == 201, created.text
    publication = created.json()
    version_id = publication["versions"][0]
    submitted = _submit(client, context, version_id)
    assert submitted.status_code == 200, submitted.text
    approved = _decide(client, context, version_id)
    assert approved.status_code == 200, approved.text
    published = _publish(client, context, version_id)
    assert published.status_code == 200, published.text
    return publication, published.json()


@trace_cases(
    "API-N18",
    "API-N19",
    "API-N20",
    "API-N21",
    "DT-25",
    "DT-26",
    "DT-27",
    "DT-28",
    "DT-29",
    "DT-37",
)
def test_publication_flow_freezes_versions_separates_people_and_selects_current_atomically(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc05-flow")
    created = _create_publication(client, context, headers=context.analyst_headers)
    assert created.status_code == 403

    created = _create_publication(client, context)
    assert created.status_code == 201, created.text
    publication_id = created.json()["id"]
    version_id = created.json()["versions"][0]
    assert created.headers["location"] == f"{PUBLICATIONS_API}/{publication_id}"
    assert created.json()["current_version_id"] is None
    assert set(created.json()) == {
        "id",
        "tracking_id",
        "client_id",
        "current_version_id",
        "versions",
    }

    publication = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.coordinator_headers
    )
    version = client.get(f"{VERSION_API}/{version_id}", headers=context.coordinator_headers)
    assert publication.status_code == 200
    assert version.status_code == 200
    assert version.json()["content_sha256"] == content_sha256(CONTENT_V1)
    assert version.json()["status"] == "DRAFT"
    assert version.json()["frozen_at"] is None

    unassigned = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.outsider_headers
    )
    external = client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.external_headers)
    assert unassigned.status_code == 404
    assert external.status_code == 403
    beta_tracking_id = _assign_beta_tracking(client, db_session, context, suffix="inc05-flow")
    beta_scoped_account = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.outsider_headers
    )
    assert beta_tracking_id != context.tracking_id
    assert beta_scoped_account.status_code == 404
    assert (
        client.post(
            f"{VERSION_API}/{version_id}/publish", headers=context.coordinator_headers
        ).status_code
        == 409
    )

    wrong_submitter = client.post(
        f"{VERSION_API}/{version_id}/submit", headers=context.coordinator_headers
    )
    assert wrong_submitter.status_code == 403
    # A second preparer is recorded on this draft to cover segregation for every person.
    db_session.add(
        PublicationPreparer(
            version_id=UUID(version_id),
            person_id=context.secondary_preparer.person_id,
            account_id=context.secondary_preparer.id,
        )
    )
    db_session.commit()
    submitted = _submit(client, context, version_id)
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["status"] == "PENDING_APPROVAL"
    assert submitted.json()["frozen_at"] is not None
    assert _submit(client, context, version_id).status_code == 409
    for headers in (context.same_person_headers, context.secondary_coordinator_headers):
        forbidden = client.post(
            f"{VERSION_API}/{version_id}/decision",
            headers=headers,
            json={"verdict": "APPROVE", "justification": JUSTIFICATION},
        )
        assert forbidden.status_code == 403
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(PublicationApproval)
            .where(PublicationApproval.version_id == UUID(version_id))
        )
        == 0
    )

    wrong_digest = "0" * 64
    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text(
                    "INSERT INTO publication_approvals "
                    "(id, version_id, approver_account_id, approver_person_id, verdict, "
                    "snapshot_sha256, justification) "
                    "VALUES (:id, :version, :account, :person, 'APPROVE', :digest, :justification)"
                ),
                {
                    "id": uuid4(),
                    "version": UUID(version_id),
                    "account": context.coordinator.id,
                    "person": context.coordinator.person_id,
                    "digest": wrong_digest,
                    "justification": JUSTIFICATION,
                },
            )
        owner_session.rollback()

    approved = _decide(client, context, version_id)
    assert approved.status_code == 200, approved.text
    assert approved.json()["status"] == "APPROVED"
    assert approved.json()["approved_at"] is not None
    assert (
        client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers).json()[
            "current_version_id"
        ]
        is None
    )

    patch_attempt = client.patch(
        f"{VERSION_API}/{version_id}",
        headers=context.preparer_headers,
        json={"content_text": "Changed submitted text."},
    )
    assert patch_attempt.status_code == 405
    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text(
                    "UPDATE publication_versions SET content_text = 'forced change' WHERE id = :id"
                ),
                {"id": UUID(version_id)},
            )
        owner_session.rollback()

    published_v1 = _publish(client, context, version_id)
    assert published_v1.status_code == 200, published_v1.text
    assert published_v1.json()["status"] == "PUBLISHED"
    assert published_v1.json()["published_at"] is not None
    current_v1 = client.get(
        f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers
    ).json()["current_version_id"]
    assert current_v1 == version_id

    version2_response = client.post(
        f"{PUBLICATIONS_API}/{publication_id}/versions",
        headers=context.preparer_headers,
        json={"novelty_ids": [str(context.novelty_id)], "content_text": CONTENT_V2},
    )
    assert version2_response.status_code == 201, version2_response.text
    version2_id = version2_response.json()["id"]
    assert version2_response.headers["location"] == f"{VERSION_API}/{version2_id}"
    assert version2_response.json()["version_number"] == 2
    assert version2_response.json()["status"] == "DRAFT"
    assert version2_response.json()["content_sha256"] == content_sha256(CONTENT_V2)
    assert (
        client.post(
            f"{VERSION_API}/{version2_id}/publish", headers=context.coordinator_headers
        ).status_code
        == 409
    )
    assert (
        client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers).json()[
            "current_version_id"
        ]
        == version_id
    )
    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text(
                    "UPDATE publications SET current_version_id = :version WHERE id = :publication"
                ),
                {"version": UUID(version2_id), "publication": UUID(publication_id)},
            )
        owner_session.rollback()
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(PublicationApproval)
            .where(PublicationApproval.version_id == UUID(version2_id))
        )
        == 0
    )

    assert _submit(client, context, version2_id).status_code == 200
    assert _decide(client, context, version2_id).status_code == 200
    published_v2 = _publish(client, context, version2_id)
    assert published_v2.status_code == 200, published_v2.text
    assert (
        client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers).json()[
            "current_version_id"
        ]
        == version2_id
    )

    other_publication, other_published = _create_and_publish(
        client, context, content_text="A separate synthetic local publication for pointer checks."
    )
    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text(
                    "UPDATE publications SET current_version_id = :version WHERE id = :publication"
                ),
                {
                    "version": UUID(str(other_published["id"])),
                    "publication": UUID(publication_id),
                },
            )
        owner_session.rollback()
    assert (
        client.get(f"{PUBLICATIONS_API}/{publication_id}", headers=context.preparer_headers).json()[
            "current_version_id"
        ]
        == version2_id
    )
    assert other_publication["id"] != publication_id

    db_session.expire_all()
    transitions = tuple(
        db_session.scalars(
            select(StateTransition)
            .where(StateTransition.version_id.in_((UUID(version_id), UUID(version2_id))))
            .order_by(StateTransition.occurred_at, StateTransition.id)
        )
    )
    assert {transition.resource_type for transition in transitions} == {"PUBLICATION_VERSION"}
    assert [item.to_state for item in transitions if item.version_id == UUID(version_id)] == [
        "DRAFT",
        "PENDING_APPROVAL",
        "APPROVED",
        "PUBLISHED",
    ]
    assert all(item.actor_person_id is not None for item in transitions)
    approvals = tuple(
        db_session.scalars(
            select(PublicationApproval).where(
                PublicationApproval.version_id.in_((UUID(version_id), UUID(version2_id)))
            )
        )
    )
    assert len(approvals) == 2
    assert all(item.approver_person_id == context.coordinator.person_id for item in approvals)
    audits = tuple(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.resource_id.in_((UUID(publication_id), UUID(version_id)))
            )
        )
    )
    assert "PUBLICATION_CREATE" in {item.event_code for item in audits}
    assert "PUBLICATION_VERSION_PUBLISH" in {item.event_code for item in audits}
    assert all(CONTENT_V1 not in (item.sanitized_reason or "") for item in audits)


def test_publication_requires_assigned_preparer_and_human_legal_treatment(
    client: TestClient, db_session: Session
) -> None:
    context = _create_publication_context(
        client, db_session, suffix="inc05-guards", finish_legal_review=False
    )
    request_body = {
        "tracking_id": str(context.tracking_id),
        "novelty_ids": [str(context.novelty_id)],
        "content_text": CONTENT_V1,
    }
    assert _create_publication(client, context, headers=context.outsider_headers).status_code == 404
    assert client.post(PUBLICATIONS_API, json=request_body).status_code == 401
    assert _create_publication(client, context, headers=context.external_headers).status_code == 403
    assert (
        client.post(
            PUBLICATIONS_API,
            headers=context.preparer_headers,
            json={**request_body, "actor_account_id": str(context.preparer.id)},
        ).status_code
        == 422
    )
    assert (
        client.post(
            PUBLICATIONS_API,
            headers=context.preparer_headers,
            json={**request_body, "novelty_ids": []},
        ).status_code
        == 422
    )
    assert (
        client.post(
            PUBLICATIONS_API,
            headers=context.preparer_headers,
            json={**request_body, "content_text": "short"},
        ).status_code
        == 422
    )
    not_reviewed = _create_publication(client, context)
    assert not_reviewed.status_code == 409
    assert db_session.scalar(select(func.count()).select_from(Publication)) == 0

    novelty = db_session.get(Novelty, context.novelty_id)
    assert novelty is not None
    novelty.status = "TREATMENT_DEFINED"
    db_session.commit()
    missing_review = _create_publication(client, context)
    assert missing_review.status_code == 409
    assert db_session.scalar(select(func.count()).select_from(Publication)) == 0


@trace_cases("DT-30", "API-N22")
def test_publish_failure_rolls_back_state_and_keeps_previous_current_version(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    _requirement_ids: tuple[str, ...],
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc05-rollback")
    publication, published_v1 = _create_and_publish(client, context)
    publication_id = UUID(str(publication["id"]))
    version1_id = UUID(str(published_v1["id"]))

    created_v2 = client.post(
        f"{PUBLICATIONS_API}/{publication_id}/versions",
        headers=context.preparer_headers,
        json={"novelty_ids": [str(context.novelty_id)], "content_text": CONTENT_V2},
    )
    assert created_v2.status_code == 201, created_v2.text
    version2_id = UUID(created_v2.json()["id"])
    assert _submit(client, context, str(version2_id)).status_code == 200
    assert _decide(client, context, str(version2_id)).status_code == 200

    def fail_before_pointer(*args: object, **kwargs: object) -> None:
        raise IntegrityError(
            "injected pointer write failure", {}, RuntimeError("synthetic failure")
        )

    monkeypatch.setattr(publication_repository, "update_current_version", fail_before_pointer)
    failed = _publish(client, context, str(version2_id))
    assert failed.status_code == 409
    request_id = UUID(failed.headers["x-request-id"])

    with TEST_SESSION_FACTORY() as verify_session:
        publication_row = verify_session.get(Publication, publication_id)
        version1 = verify_session.get(PublicationVersion, version1_id)
        version2 = verify_session.get(PublicationVersion, version2_id)
        assert publication_row is not None and publication_row.current_version_id == version1_id
        assert version1 is not None and version1.status == "PUBLISHED"
        assert version2 is not None and version2.status == "APPROVED"
        assert (
            verify_session.scalar(
                select(func.count()).where(
                    StateTransition.version_id == version2_id,
                    StateTransition.to_state == "PUBLISHED",
                )
            )
            == 0
        )
        assert (
            verify_session.scalar(
                select(func.count()).where(
                    AuditEvent.request_id == request_id,
                    AuditEvent.event_code == "PUBLICATION_VERSION_PUBLISH",
                    AuditEvent.result == "SUCCESS",
                )
            )
            == 0
        )


@trace_cases("DT-23", "DT-24")
def test_postgres_publication_guards_reject_bad_preparer_and_incomplete_submission(
    client: TestClient, db_session: Session, _requirement_ids: tuple[str, ...]
) -> None:
    context = _create_publication_context(client, db_session, suffix="inc05-database")
    created = _create_publication(client, context)
    assert created.status_code == 201, created.text
    version_id = UUID(created.json()["versions"][0])

    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text(
                    "INSERT INTO publication_preparers (version_id, person_id, account_id) "
                    "VALUES (:version, :person, :account)"
                ),
                {
                    "version": version_id,
                    "person": context.secondary_preparer.person_id,
                    "account": context.preparer.id,
                },
            )
        owner_session.rollback()

    with TEST_MIGRATION_SESSION_FACTORY() as owner_session:
        with pytest.raises(DBAPIError):
            owner_session.execute(
                text("DELETE FROM publication_preparers WHERE version_id = :version"),
                {"version": version_id},
            )
            owner_session.execute(
                text("DELETE FROM publication_version_novelties WHERE version_id = :version"),
                {"version": version_id},
            )
            owner_session.execute(
                text(
                    "UPDATE publication_versions "
                    "SET status = 'PENDING_APPROVAL', frozen_at = now() WHERE id = :version"
                ),
                {"version": version_id},
            )
        owner_session.rollback()

    with TEST_SESSION_FACTORY() as verify_session:
        assert verify_session.get(PublicationVersion, version_id).status == "DRAFT"
        assert (
            verify_session.scalar(
                select(func.count()).where(PublicationPreparer.version_id == version_id)
            )
            == 1
        )
        assert (
            verify_session.scalar(
                select(func.count()).where(PublicationVersionNovelty.version_id == version_id)
            )
            == 1
        )
