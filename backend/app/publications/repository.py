from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.novelties.models import Novelty, NoveltyReview, StateTransition
from app.publications.models import (
    Publication,
    PublicationApproval,
    PublicationPreparer,
    PublicationVersion,
    PublicationVersionNovelty,
)
from app.trackings.models import InternalTrackingAssignment, Tracking


def tracking_for_assigned_account(
    session: Session,
    *,
    tracking_id: UUID,
    account_id: UUID,
    lock: bool = False,
) -> Tracking | None:
    assignment_exists = exists(
        select(1).where(
            InternalTrackingAssignment.tracking_id == Tracking.id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    statement = select(Tracking).where(Tracking.id == tracking_id, assignment_exists)
    if lock:
        statement = statement.with_for_update(of=Tracking)
    return session.scalar(statement)


def publication_for_assigned_account(
    session: Session,
    *,
    publication_id: UUID,
    account_id: UUID,
    lock: bool = False,
) -> Publication | None:
    assigned = exists(
        select(1).where(
            InternalTrackingAssignment.tracking_id == Publication.tracking_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    statement = select(Publication).where(Publication.id == publication_id, assigned)
    if lock:
        statement = statement.with_for_update(of=Publication)
    return session.scalar(statement)


def version_for_assigned_account(
    session: Session,
    *,
    version_id: UUID,
    account_id: UUID,
    lock: bool = False,
) -> tuple[PublicationVersion, Publication] | None:
    assigned = exists(
        select(1).where(
            InternalTrackingAssignment.tracking_id == Publication.tracking_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    statement = (
        select(PublicationVersion, Publication)
        .join(Publication, Publication.id == PublicationVersion.publication_id)
        .where(PublicationVersion.id == version_id, assigned)
    )
    if lock:
        statement = statement.with_for_update(of=(Publication, PublicationVersion))
    row = session.execute(statement).one_or_none()
    return (row[0], row[1]) if row is not None else None


def novelties_for_tracking(
    session: Session, *, tracking_id: UUID, novelty_ids: tuple[UUID, ...]
) -> tuple[Novelty, ...]:
    return tuple(
        session.scalars(
            select(Novelty).where(
                Novelty.tracking_id == tracking_id,
                Novelty.id.in_(novelty_ids),
            )
        )
    )


def has_legal_review(session: Session, *, novelty_id: UUID) -> bool:
    return bool(
        session.scalar(
            select(
                exists(
                    select(1).where(
                        NoveltyReview.novelty_id == novelty_id,
                        NoveltyReview.review_kind == "LEGAL",
                    )
                )
            )
        )
    )


def has_nonterminal_version(session: Session, *, publication_id: UUID) -> bool:
    return bool(
        session.scalar(
            select(
                exists(
                    select(1).where(
                        PublicationVersion.publication_id == publication_id,
                        PublicationVersion.status.in_(("DRAFT", "PENDING_APPROVAL", "APPROVED")),
                    )
                )
            )
        )
    )


def next_version_number(session: Session, *, publication_id: UUID) -> int:
    current = session.scalar(
        select(func.coalesce(func.max(PublicationVersion.version_number), 0)).where(
            PublicationVersion.publication_id == publication_id
        )
    )
    return int(current or 0) + 1


def version_ids(session: Session, *, publication_id: UUID) -> tuple[UUID, ...]:
    return tuple(
        session.scalars(
            select(PublicationVersion.id)
            .where(PublicationVersion.publication_id == publication_id)
            .order_by(PublicationVersion.version_number)
        )
    )


def add_preparer(
    session: Session, *, version_id: UUID, person_id: UUID, account_id: UUID
) -> PublicationPreparer:
    preparer = PublicationPreparer(
        version_id=version_id, person_id=person_id, account_id=account_id
    )
    session.add(preparer)
    return preparer


def add_version_novelty(
    session: Session, *, version_id: UUID, tracking_id: UUID, novelty_id: UUID
) -> PublicationVersionNovelty:
    link = PublicationVersionNovelty(
        version_id=version_id, tracking_id=tracking_id, novelty_id=novelty_id
    )
    session.add(link)
    return link


def preparer_person_ids(session: Session, *, version_id: UUID) -> frozenset[UUID]:
    return frozenset(
        session.scalars(
            select(PublicationPreparer.person_id).where(
                PublicationPreparer.version_id == version_id
            )
        )
    )


def approval_for_version(session: Session, *, version_id: UUID) -> PublicationApproval | None:
    return session.scalar(
        select(PublicationApproval).where(PublicationApproval.version_id == version_id)
    )


def add_approval(
    session: Session,
    *,
    approval_id: UUID,
    version_id: UUID,
    approver_account_id: UUID,
    approver_person_id: UUID,
    verdict: str,
    snapshot_sha256: str,
    justification: str,
) -> PublicationApproval:
    approval = PublicationApproval(
        id=approval_id,
        version_id=version_id,
        approver_account_id=approver_account_id,
        approver_person_id=approver_person_id,
        verdict=verdict,
        snapshot_sha256=snapshot_sha256,
        justification=justification,
    )
    session.add(approval)
    session.flush()
    return approval


def add_state_transition(
    session: Session,
    *,
    transition_id: UUID,
    version_id: UUID,
    from_state: str | None,
    to_state: str,
    actor_account_id: UUID,
    actor_person_id: UUID,
    request_id: UUID,
    reason: str,
) -> StateTransition:
    transition = StateTransition(
        id=transition_id,
        resource_type="PUBLICATION_VERSION",
        version_id=version_id,
        from_state=from_state,
        to_state=to_state,
        actor_account_id=actor_account_id,
        actor_person_id=actor_person_id,
        actor_kind="USER",
        request_id=request_id,
        reason=reason,
    )
    session.add(transition)
    session.flush()
    return transition


def update_current_version(session: Session, *, publication: Publication, version_id: UUID) -> None:
    publication.current_version_id = version_id
    session.flush()
