from uuid import UUID

from sqlalchemy import and_, desc, exists, func, or_, select, text
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.comparisons.models import Comparison
from app.novelties.domain import decode_novelty_cursor, encode_novelty_cursor
from app.novelties.models import Novelty, NoveltyReview, StateTransition, TrackingEvaluation
from app.trackings.models import InternalTrackingAssignment, Tracking
from app.trackings.repository import tracking_for_assigned_account


def evaluation_for_tracking(
    session: Session, *, tracking_id: UUID, comparison_id: UUID
) -> TrackingEvaluation | None:
    return session.scalar(
        select(TrackingEvaluation).where(
            TrackingEvaluation.tracking_id == tracking_id,
            TrackingEvaluation.comparison_id == comparison_id,
        )
    )


def evaluation_for_observation_pair(
    session: Session,
    *,
    tracking_id: UUID,
    old_observation_id: UUID,
    new_observation_id: UUID,
) -> bool:
    return bool(
        session.scalar(
            select(
                exists(
                    select(1)
                    .select_from(TrackingEvaluation)
                    .join(Comparison, Comparison.id == TrackingEvaluation.comparison_id)
                    .where(
                        TrackingEvaluation.tracking_id == tracking_id,
                        Comparison.old_observation_id == old_observation_id,
                        Comparison.new_observation_id == new_observation_id,
                        Comparison.result.in_(("CHANGES_FOUND", "NO_CHANGES")),
                    )
                )
            )
        )
    )


def novelties_for_evaluation(session: Session, evaluation_id: UUID) -> tuple[Novelty, ...]:
    return tuple(
        session.scalars(
            select(Novelty)
            .where(Novelty.evaluation_id == evaluation_id)
            .order_by(Novelty.novelty_code)
        )
    )


def novelty_for_assigned_account(
    session: Session,
    *,
    novelty_id: UUID,
    account_id: UUID,
    lock: bool = False,
) -> Novelty | None:
    assigned = exists(
        select(1).where(
            InternalTrackingAssignment.tracking_id == Novelty.tracking_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    statement = select(Novelty).where(Novelty.id == novelty_id, assigned)
    if lock:
        statement = statement.with_for_update(of=Novelty)
    return session.scalar(statement)


def novelties_for_assigned_tracking(
    session: Session,
    *,
    tracking_id: UUID,
    account_id: UUID,
    limit: int,
    cursor: str | None,
) -> tuple[tuple[Novelty, ...], str | None] | None:
    tracking = tracking_for_assigned_account(
        session, tracking_id=tracking_id, account_id=account_id
    )
    if tracking is None:
        return None

    statement = select(Novelty).where(Novelty.tracking_id == tracking.id)
    if cursor is not None:
        created_at, novelty_id = decode_novelty_cursor(cursor)
        statement = statement.where(
            or_(
                Novelty.created_at < created_at,
                and_(Novelty.created_at == created_at, Novelty.id < novelty_id),
            )
        )
    rows = tuple(
        session.scalars(
            statement.order_by(desc(Novelty.created_at), desc(Novelty.id)).limit(limit + 1)
        )
    )
    page = rows[:limit]
    next_cursor = None
    if len(rows) > limit:
        last = page[-1]
        next_cursor = encode_novelty_cursor(last.created_at, last.id)
    return page, next_cursor


def review_for_kind(
    session: Session, *, novelty_id: UUID, review_kind: str
) -> NoveltyReview | None:
    return session.scalar(
        select(NoveltyReview)
        .where(
            NoveltyReview.novelty_id == novelty_id,
            NoveltyReview.review_kind == review_kind,
        )
        .order_by(NoveltyReview.review_sequence.desc())
        .limit(1)
    )


def add_review(
    session: Session,
    *,
    review_id: UUID,
    novelty_id: UUID,
    review_kind: str,
    actor_account_id: UUID,
    actor_person_id: UUID,
    decision: str,
    evidence_note: str,
) -> NoveltyReview:
    sequence = session.scalar(
        select(func.coalesce(func.max(NoveltyReview.review_sequence), 0) + 1).where(
            NoveltyReview.novelty_id == novelty_id,
            NoveltyReview.review_kind == review_kind,
        )
    )
    review = NoveltyReview(
        id=review_id,
        novelty_id=novelty_id,
        review_kind=review_kind,
        review_sequence=int(sequence or 1),
        actor_account_id=actor_account_id,
        actor_person_id=actor_person_id,
        decision=decision,
        evidence_note=evidence_note,
    )
    session.add(review)
    session.flush()
    return review


def add_state_transition(
    session: Session,
    *,
    transition_id: UUID,
    novelty_id: UUID,
    from_state: str,
    to_state: str,
    actor_account_id: UUID,
    actor_person_id: UUID,
    request_id: UUID,
    reason: str,
) -> StateTransition:
    transition = StateTransition(
        id=transition_id,
        resource_type="NOVELTY",
        novelty_id=novelty_id,
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


def next_novelty_code(session: Session, *, client_code: str) -> str:
    prefix_letter = next(
        (character.upper() for character in client_code if character.isalnum()), "X"
    )
    prefix = f"NOV-{prefix_letter}-"
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
        {"lock_key": f"legaltech-novelty-code:{prefix_letter}"},
    )
    existing = session.scalars(
        select(Novelty.novelty_code).where(Novelty.novelty_code.like(f"{prefix}%"))
    )
    suffixes = [int(code[len(prefix) :]) for code in existing if code[len(prefix) :].isdigit()]
    return f"{prefix}{max(suffixes, default=0) + 1:03d}"


def add_evaluation(
    session: Session,
    *,
    evaluation_id: UUID,
    tracking: Tracking,
    comparison: Comparison,
    decision: str,
    reason: str,
) -> TrackingEvaluation:
    evaluation = TrackingEvaluation(
        id=evaluation_id,
        tracking_id=tracking.id,
        process_id=tracking.process_id,
        comparison_id=comparison.id,
        decision=decision,
        reason=reason,
    )
    session.add(evaluation)
    session.flush()
    return evaluation


def add_novelty(
    session: Session,
    *,
    novelty_id: UUID,
    novelty_code: str,
    tracking: Tracking,
    comparison: Comparison,
    change_id: UUID,
    evaluation: TrackingEvaluation,
) -> Novelty:
    novelty = Novelty(
        id=novelty_id,
        novelty_code=novelty_code,
        tracking_id=tracking.id,
        client_id=tracking.client_id,
        process_id=tracking.process_id,
        comparison_id=comparison.id,
        change_id=change_id,
        evaluation_id=evaluation.id,
        evaluation_decision=evaluation.decision,
        status="PENDING_OPERATIVE",
    )
    session.add(novelty)
    session.flush()
    return novelty


def active_client_for_tracking(session: Session, tracking: Tracking) -> Client | None:
    return session.scalar(
        select(Client).where(Client.id == tracking.client_id, Client.status == "ACTIVE")
    )
