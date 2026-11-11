from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.authorization.domain import ACTIVATION_ROLES
from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.clients.models import Client
from app.core.errors import ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.trackings import repository
from app.trackings.domain import ProcessData, TrackingData
from app.trackings.models import JudicialProcess, Tracking


class TrackingService:
    def create_process(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        radicado: str,
        label: str | None,
    ) -> ProcessData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="PROCESS_CREATE",
            allowed_roles={"ADMIN"},
        )
        process_id = uuid4()
        try:
            with session.begin():
                process = repository.add_process(
                    session,
                    process_id=process_id,
                    radicado=radicado,
                    label=label,
                )
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    event_code="PROCESS_CREATE",
                    resource_kind="PROCESS",
                    resource_id=process.id,
                )
                return self._process_data(process)
        except IntegrityError as exc:
            raise ResourceConflict from exc

    def get_process(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        process_id: UUID,
    ) -> ProcessData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="PROCESS_READ",
        )
        process = repository.process_for_assigned_account(
            session,
            process_id=process_id,
            account_id=principal.account_id,
        )
        if process is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="PROCESS_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        return self._process_data(process)

    def create_tracking(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_id: UUID,
        process_id: UUID,
    ) -> TrackingData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="TRACKING_CREATE",
            allowed_roles={"ADMIN"},
        )
        tracking_id = uuid4()
        try:
            with session.begin():
                client = repository.find_active_client(session, client_id)
                if client is None:
                    if session.get(Client, client_id) is None:
                        raise ResourceNotFound
                    raise ResourceConflict
                process = repository.find_process(session, process_id)
                if process is None:
                    raise ResourceNotFound

                tracking_code = repository.next_tracking_code(session, client.client_code)
                tracking = repository.add_tracking(
                    session,
                    tracking_id=tracking_id,
                    tracking_code=tracking_code,
                    client_id=client.id,
                    process_id=process.id,
                )
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    event_code="TRACKING_CREATE",
                    resource_kind="TRACKING",
                    resource_id=tracking.id,
                )
                return self._tracking_data(tracking)
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="TRACKING_CREATE",
                reason="related_resource_not_found",
            )
            raise
        except IntegrityError as exc:
            raise ResourceConflict from exc

    def get_tracking(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
    ) -> TrackingData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="TRACKING_READ",
        )
        tracking = repository.tracking_for_assigned_account(
            session,
            tracking_id=tracking_id,
            account_id=principal.account_id,
        )
        if tracking is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="TRACKING_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        return self._tracking_data(tracking)

    def activate_tracking(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        tracking_id: UUID,
    ) -> TrackingData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="TRACKING_ACTIVATE",
            allowed_roles=ACTIVATION_ROLES,
        )
        try:
            with session.begin():
                tracking = repository.tracking_for_assigned_account(
                    session,
                    tracking_id=tracking_id,
                    account_id=principal.account_id,
                    lock=True,
                )
                if tracking is None:
                    raise ResourceNotFound
                if tracking.status != "PENDING":
                    raise ResourceConflict
                client = session.get(Client, tracking.client_id)
                if client is None or client.status != "ACTIVE":
                    raise ResourceConflict

                repository.activate_tracking(tracking)
                self._audit(
                    session,
                    request_id=request_id,
                    principal=principal,
                    event_code="TRACKING_ACTIVATE",
                    resource_kind="TRACKING",
                    resource_id=tracking.id,
                )
                return self._tracking_data(tracking)
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="TRACKING_ACTIVATE",
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            raise ResourceConflict from exc

    @staticmethod
    def _process_data(process: JudicialProcess) -> ProcessData:
        return ProcessData(id=process.id, radicado=process.radicado, label=process.label)

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
