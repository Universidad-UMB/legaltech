import hashlib
import json
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.acquisitions import repository
from app.acquisitions.domain import (
    AcquisitionCreateResult,
    AcquisitionData,
    FixtureCode,
    ObservationData,
)
from app.acquisitions.fixture_adapter import load_fixture
from app.acquisitions.models import AcquisitionRun, Observation
from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.core.errors import InvalidInput, ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.trackings.domain import TrackingData
from app.trackings.models import Tracking
from app.trackings.repository import tracking_for_assigned_account


class AcquisitionService:
    def create(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        process_id: UUID,
        fixture_code: FixtureCode,
        request_key: str,
    ) -> AcquisitionCreateResult:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="ACQUISITION_CREATE",
            allowed_roles={"ADMIN", "ANALYST"},
        )
        fixture = load_fixture(fixture_code)
        payload_digest = hashlib.sha256(
            json.dumps(
                {"fixture_code": fixture_code, "process_id": str(process_id)},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        try:
            with session.begin():
                process = repository.eligible_process_for_account(
                    session,
                    process_id=process_id,
                    account_id=principal.account_id,
                )
                if process is None:
                    raise ResourceNotFound
                if process.radicado != fixture.process_radicado:
                    raise InvalidInput

                existing = repository.acquisition_by_request_key(session, request_key)
                if existing is not None:
                    if existing.request_payload_sha256 != payload_digest:
                        raise ResourceConflict
                    observation = repository.observation_for_run(session, existing.id)
                    return AcquisitionCreateResult(
                        acquisition=self._acquisition_data(existing, observation),
                        created=False,
                    )

                run = repository.add_acquisition_run(
                    session,
                    run_id=uuid4(),
                    process_id=process.id,
                    fixture=fixture,
                    request_key=request_key,
                    request_payload_sha256=payload_digest,
                )
                observation = None
                if fixture.status == "SUCCESS":
                    observation = repository.add_observation(
                        session,
                        observation_id=uuid4(),
                        process_id=process.id,
                        run_id=run.id,
                        fixture=fixture,
                    )
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    event_code="ACQUISITION_CREATE",
                    resource_kind="ACQUISITION_RUN",
                    resource_id=run.id,
                )
                return AcquisitionCreateResult(
                    acquisition=self._acquisition_data(run, observation),
                    created=True,
                )
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="ACQUISITION_CREATE",
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            session.rollback()
            existing = repository.acquisition_by_request_key(session, request_key)
            if existing is not None and existing.request_payload_sha256 == payload_digest:
                observation = repository.observation_for_run(session, existing.id)
                return AcquisitionCreateResult(
                    acquisition=self._acquisition_data(existing, observation),
                    created=False,
                )
            raise ResourceConflict from exc

    def get_acquisition(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        run_id: UUID,
    ) -> AcquisitionData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="ACQUISITION_READ",
        )
        run = repository.acquisition_for_assigned_account(
            session,
            run_id=run_id,
            account_id=principal.account_id,
        )
        if run is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="ACQUISITION_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        observation = repository.observation_for_run(session, run.id)
        return self._acquisition_data(run, observation)

    def get_observation(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        observation_id: UUID,
    ) -> ObservationData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="OBSERVATION_READ",
        )
        observation = repository.observation_for_assigned_account(
            session,
            observation_id=observation_id,
            account_id=principal.account_id,
        )
        if observation is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="OBSERVATION_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        return self._observation_data(session, observation)

    def adopt_observation(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
        observation_id: UUID,
    ) -> tuple[TrackingData, Literal["BASELINE_SET", "ADVANCED", "ALREADY_ADOPTED"]]:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="TRACKING_ADOPT_OBSERVATION",
            allowed_roles={"ANALYST"},
        )
        try:
            with session.begin():
                tracking = tracking_for_assigned_account(
                    session,
                    tracking_id=tracking_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if tracking is None:
                    raise ResourceNotFound
                if tracking.status != "ACTIVE":
                    raise ResourceConflict

                observation = repository.observation_for_tracking(
                    session,
                    observation_id=observation_id,
                    process_id=tracking.process_id,
                )
                if observation is None:
                    raise ResourceNotFound
                if observation.quality != "COMPARABLE" or observation.sealed_at is None:
                    raise ResourceConflict

                outcome: Literal["BASELINE_SET", "ADVANCED", "ALREADY_ADOPTED"]
                if tracking.baseline_observation_id is None:
                    tracking.baseline_observation_id = observation.id
                    tracking.last_adopted_observation_id = observation.id
                    tracking.updated_at = datetime.now(UTC)
                    outcome = "BASELINE_SET"
                elif tracking.last_adopted_observation_id == observation.id:
                    outcome = "ALREADY_ADOPTED"
                else:
                    # INC-03/04 add comparison and evaluation persistence. Until then,
                    # a later snapshot cannot move the cursor without an evaluation.
                    raise ResourceConflict

                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    event_code="TRACKING_ADOPT_OBSERVATION",
                    resource_kind="TRACKING",
                    resource_id=tracking.id,
                )
                return self._tracking_data(tracking), outcome
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="TRACKING_ADOPT_OBSERVATION",
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            raise ResourceConflict from exc

    @staticmethod
    def _acquisition_data(run: AcquisitionRun, observation: Observation | None) -> AcquisitionData:
        return AcquisitionData(
            id=run.id,
            process_id=run.process_id,
            source_code="DEMO-FIXTURE",
            status=run.status,  # type: ignore[arg-type]
            request_key=run.request_key,
            observation_id=observation.id if observation is not None else None,
            error_code=run.error_code,
            coverage_note=run.coverage_note,
        )

    @staticmethod
    def _observation_data(session: Session, observation: Observation) -> ObservationData:
        return ObservationData(
            id=observation.id,
            process_id=observation.process_id,
            quality=observation.quality,  # type: ignore[arg-type]
            sealed=observation.sealed_at is not None,
            observed_at=observation.observed_at,
            actions=repository.actions_for_observation(session, observation.id),
            coverage_note=observation.coverage_note,
        )

    @staticmethod
    def _tracking_data(tracking: Tracking) -> TrackingData:
        return TrackingData(
            id=tracking.id,
            tracking_code=tracking.tracking_code,
            client_id=tracking.client_id,
            process_id=tracking.process_id,
            status=tracking.status,
            baseline_observation_id=tracking.baseline_observation_id,
            last_adopted_observation_id=tracking.last_adopted_observation_id,
            created_at=tracking.created_at,
            updated_at=tracking.updated_at,
        )

    @staticmethod
    def _audit(
        session: Session,
        *,
        request_id: UUID,
        principal: Principal,
        event_code: str,
        resource_kind: str,
        resource_id: UUID,
    ) -> None:
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code=event_code,
                result="SUCCESS",
                actor_account_id=principal.account_id,
                resource_kind=resource_kind,
                resource_id=resource_id,
            )
        )
