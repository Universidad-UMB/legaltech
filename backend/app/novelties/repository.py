from uuid import UUID

from sqlalchemy import exists, select, text
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.comparisons.models import Comparison
from app.novelties.models import Novelty, TrackingEvaluation
from app.trackings.models import Tracking


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
