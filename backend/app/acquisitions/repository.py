from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID

from sqlalchemy import exists, func, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.acquisitions.domain import AcquisitionFixture, ObservedActionData
from app.acquisitions.models import AcquisitionRun, Observation, ObservedAction
from app.clients.models import Client
from app.trackings.models import InternalTrackingAssignment, JudicialProcess, Tracking


def eligible_process_for_account(
    session: Session, *, process_id: UUID, account_id: UUID
) -> JudicialProcess | None:
    statement = (
        select(JudicialProcess)
        .join(Tracking, Tracking.process_id == JudicialProcess.id)
        .join(Client, Client.id == Tracking.client_id)
        .join(
            InternalTrackingAssignment,
            InternalTrackingAssignment.tracking_id == Tracking.id,
        )
        .where(
            JudicialProcess.id == process_id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
            Tracking.status == "ACTIVE",
            Client.status == "ACTIVE",
        )
        .distinct()
    )
    return session.scalar(statement)


def _assigned_process_exists(account_id: UUID) -> ColumnElement[bool]:
    return exists(
        select(1)
        .select_from(Tracking)
        .join(
            InternalTrackingAssignment,
            InternalTrackingAssignment.tracking_id == Tracking.id,
        )
        .where(
            Tracking.process_id == JudicialProcess.id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )


def process_for_assigned_account(
    session: Session, *, process_id: UUID, account_id: UUID
) -> JudicialProcess | None:
    return session.scalar(
        select(JudicialProcess).where(
            JudicialProcess.id == process_id,
            _assigned_process_exists(account_id),
        )
    )


def acquisition_for_assigned_account(
    session: Session, *, run_id: UUID, account_id: UUID
) -> AcquisitionRun | None:
    return session.scalar(
        select(AcquisitionRun).where(
            AcquisitionRun.id == run_id,
            exists(
                select(1)
                .select_from(Tracking)
                .join(
                    InternalTrackingAssignment,
                    InternalTrackingAssignment.tracking_id == Tracking.id,
                )
                .where(
                    Tracking.process_id == AcquisitionRun.process_id,
                    InternalTrackingAssignment.account_id == account_id,
                    InternalTrackingAssignment.revoked_at.is_(None),
                )
            ),
        )
    )


def observation_for_assigned_account(
    session: Session, *, observation_id: UUID, account_id: UUID
) -> Observation | None:
    return session.scalar(
        select(Observation).where(
            Observation.id == observation_id,
            exists(
                select(1)
                .select_from(Tracking)
                .join(
                    InternalTrackingAssignment,
                    InternalTrackingAssignment.tracking_id == Tracking.id,
                )
                .where(
                    Tracking.process_id == Observation.process_id,
                    InternalTrackingAssignment.account_id == account_id,
                    InternalTrackingAssignment.revoked_at.is_(None),
                )
            ),
        )
    )


def acquisition_by_request_key(session: Session, request_key: str) -> AcquisitionRun | None:
    return session.scalar(select(AcquisitionRun).where(AcquisitionRun.request_key == request_key))


def observation_for_run(session: Session, run_id: UUID) -> Observation | None:
    return session.scalar(select(Observation).where(Observation.acquisition_run_id == run_id))


def observation_for_tracking(
    session: Session, *, observation_id: UUID, process_id: UUID
) -> Observation | None:
    return session.scalar(
        select(Observation).where(
            Observation.id == observation_id,
            Observation.process_id == process_id,
        )
    )


def next_comparable_observation(
    session: Session, *, process_id: UUID, after: datetime
) -> Observation | None:
    return session.scalar(
        select(Observation)
        .where(
            Observation.process_id == process_id,
            Observation.quality == "COMPARABLE",
            Observation.sealed_at.is_not(None),
            Observation.observed_at > after,
        )
        .order_by(Observation.observed_at, Observation.id)
        .limit(1)
    )


def actions_for_observation(
    session: Session, observation_id: UUID
) -> tuple[ObservedActionData, ...]:
    actions = session.scalars(
        select(ObservedAction)
        .where(ObservedAction.observation_id == observation_id)
        .order_by(ObservedAction.action_key)
    )
    return tuple(
        ObservedActionData(
            action_key=action.action_key,
            description=action.description,
            occurred_on=action.occurred_on,
        )
        for action in actions
    )


def add_acquisition_run(
    session: Session,
    *,
    run_id: UUID,
    process_id: UUID,
    fixture: AcquisitionFixture,
    request_key: str,
    request_payload_sha256: str,
) -> AcquisitionRun:
    run = AcquisitionRun(
        id=run_id,
        process_id=process_id,
        source_code="DEMO-FIXTURE",
        fixture_code=fixture.fixture_code,
        status="PENDING",
        request_key=request_key,
        request_payload_sha256=request_payload_sha256,
        error_code=None,
        coverage_note=None,
    )
    session.add(run)
    session.flush()
    run.status = fixture.status
    run.finished_at = datetime.now(UTC)
    run.error_code = fixture.error_code
    run.coverage_note = fixture.coverage_note
    session.flush()
    return run


def add_observation(
    session: Session,
    *,
    observation_id: UUID,
    process_id: UUID,
    run_id: UUID,
    fixture: AcquisitionFixture,
) -> Observation:
    if fixture.observed_at is None or fixture.quality is None:
        raise ValueError("A successful fixture must contain an observation snapshot.")
    observation = Observation(
        id=observation_id,
        process_id=process_id,
        acquisition_run_id=run_id,
        quality=fixture.quality,
        observed_at=fixture.observed_at,
        payload_sha256=fixture.payload_sha256,
        provenance="DEMO-FIXTURE",
        coverage_note=fixture.coverage_note,
    )
    session.add(observation)
    session.flush()
    for action in fixture.actions:
        canonical_content = "\n".join(
            (
                action.action_key,
                action.occurred_on.isoformat() if action.occurred_on is not None else "",
                action.description,
            )
        )
        session.add(
            ObservedAction(
                observation_id=observation.id,
                action_key=action.action_key,
                content_sha256=sha256(canonical_content.encode("utf-8")).hexdigest(),
                description=action.description,
                occurred_on=action.occurred_on,
            )
        )
    session.flush()
    session.execute(
        update(Observation).where(Observation.id == observation.id).values(sealed_at=func.now())
    )
    session.refresh(observation)
    return observation
