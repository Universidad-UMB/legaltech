from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, aliased

from app.acquisitions.models import Observation
from app.comparisons.models import Comparison, TechnicalChange
from app.trackings.models import InternalTrackingAssignment, Tracking


def observation_pair_for_account(
    session: Session,
    *,
    old_observation_id: UUID,
    new_observation_id: UUID,
    account_id: UUID,
) -> tuple[Observation, Observation] | None:
    old = aliased(Observation)
    new = aliased(Observation)
    assignment_exists = exists(
        select(1)
        .select_from(Tracking)
        .join(InternalTrackingAssignment, InternalTrackingAssignment.tracking_id == Tracking.id)
        .where(
            Tracking.process_id == old.process_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    pair = session.execute(
        select(old, new).where(
            old.id == old_observation_id,
            new.id == new_observation_id,
            old.process_id == new.process_id,
            assignment_exists,
        )
    ).one_or_none()
    return (pair[0], pair[1]) if pair is not None else None


def comparison_by_key(
    session: Session,
    *,
    old_observation_id: UUID,
    new_observation_id: UUID,
    rule_version: str,
) -> Comparison | None:
    return session.scalar(
        select(Comparison).where(
            Comparison.old_observation_id == old_observation_id,
            Comparison.new_observation_id == new_observation_id,
            Comparison.rule_version == rule_version,
        )
    )


def comparison_for_assigned_account(
    session: Session, *, comparison_id: UUID, account_id: UUID
) -> Comparison | None:
    assignment_exists = exists(
        select(1)
        .select_from(Tracking)
        .join(InternalTrackingAssignment, InternalTrackingAssignment.tracking_id == Tracking.id)
        .where(
            Tracking.process_id == Comparison.process_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    return session.scalar(
        select(Comparison).where(Comparison.id == comparison_id, assignment_exists)
    )


def comparison_for_tracking(
    session: Session, *, comparison_id: UUID, tracking: Tracking
) -> Comparison | None:
    return session.scalar(
        select(Comparison).where(
            Comparison.id == comparison_id,
            Comparison.process_id == tracking.process_id,
        )
    )


def add_comparison(
    session: Session,
    *,
    comparison_id: UUID,
    process_id: UUID,
    old_observation_id: UUID,
    new_observation_id: UUID,
    rule_version: str,
    result: str,
) -> Comparison:
    comparison = Comparison(
        id=comparison_id,
        process_id=process_id,
        old_observation_id=old_observation_id,
        new_observation_id=new_observation_id,
        rule_version=rule_version,
        result=result,
    )
    session.add(comparison)
    session.flush()
    return comparison


def add_technical_change(
    session: Session,
    *,
    change_id: UUID,
    comparison: Comparison,
    action_key: str,
) -> TechnicalChange:
    change = TechnicalChange(
        id=change_id,
        comparison_id=comparison.id,
        process_id=comparison.process_id,
        new_observation_id=comparison.new_observation_id,
        action_key=action_key,
        change_kind="ADDED",
        evidence=(
            f"Action {action_key} is present in the newer sealed observation "
            f"{comparison.new_observation_id}."
        ),
    )
    session.add(change)
    session.flush()
    return change


def changes_for_comparison(session: Session, comparison_id: UUID) -> tuple[TechnicalChange, ...]:
    return tuple(
        session.scalars(
            select(TechnicalChange)
            .where(TechnicalChange.comparison_id == comparison_id)
            .order_by(TechnicalChange.action_key, TechnicalChange.id)
        )
    )


def observation_snapshot(
    observation: Observation, *, action_keys: tuple[str, ...]
) -> tuple[UUID, UUID, str, bool, datetime, tuple[str, ...]]:
    return (
        observation.id,
        observation.process_id,
        observation.quality,
        observation.sealed_at is not None,
        observation.observed_at,
        action_keys,
    )
