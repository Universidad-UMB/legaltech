from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.audit import repository as audit_repository
from app.authorization.service import (
    authorize_internal_account,
    authorize_internal_roles,
    record_denial,
)
from app.clients import repository
from app.clients.domain import ClientData, normalize_client_values
from app.core.errors import ResourceConflict, ResourceNotFound
from app.identity.domain import Principal
from app.identity.models import AuditEvent


class ClientService:
    def create(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_code: str,
        name: str,
    ) -> ClientData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code="CLIENT_CREATE",
            allowed_roles={"ADMIN"},
        )
        normalized_code, normalized_name = normalize_client_values(client_code, name)
        client_id = uuid4()
        try:
            with session.begin():
                client = repository.add_client(
                    session,
                    client_id=client_id,
                    client_code=normalized_code,
                    name=normalized_name,
                )
                session.add(
                    AuditEvent(
                        id=uuid4(),
                        request_id=request_id,
                        event_code="CLIENT_CREATE",
                        result="SUCCESS",
                        actor_account_id=principal.account_id,
                        resource_kind="CLIENT",
                        resource_id=client.id,
                    )
                )
                return ClientData(
                    id=client.id,
                    client_code=client.client_code,
                    name=client.name,
                    status=client.status,
                )
        except IntegrityError as exc:
            raise ResourceConflict from exc

    def get(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_id: UUID,
    ) -> ClientData:
        authorize_internal_account(
            session,
            principal=principal,
            request_id=request_id,
            event_code="CLIENT_READ",
        )
        client = repository.client_for_assigned_account(
            session,
            client_id=client_id,
            account_id=principal.account_id,
        )
        if client is None:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code="CLIENT_READ",
                reason="resource_not_in_scope",
            )
            raise ResourceNotFound
        return ClientData(
            id=client.id,
            client_code=client.client_code,
            name=client.name,
            status=client.status,
        )

    def suspend(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_id: UUID,
        reason: str,
    ) -> ClientData:
        return self._transition_status(
            session,
            principal=principal,
            request_id=request_id,
            client_id=client_id,
            reason=reason,
            source_status="ACTIVE",
            target_status="SUSPENDED",
            event_code="CLIENT_SUSPEND",
        )

    def reactivate(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_id: UUID,
        reason: str,
    ) -> ClientData:
        return self._transition_status(
            session,
            principal=principal,
            request_id=request_id,
            client_id=client_id,
            reason=reason,
            source_status="SUSPENDED",
            target_status="ACTIVE",
            event_code="CLIENT_REACTIVATE",
        )

    def _transition_status(
        self,
        session: Session,
        *,
        principal: Principal,
        request_id: UUID,
        client_id: UUID,
        reason: str,
        source_status: str,
        target_status: str,
        event_code: str,
    ) -> ClientData:
        authorize_internal_roles(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            allowed_roles={"ADMIN"},
        )
        try:
            with session.begin():
                client = repository.client_for_update(session, client_id=client_id)
                if client is None:
                    raise ResourceNotFound
                if client.status != source_status:
                    raise ResourceConflict

                client.status = target_status
                client.updated_at = datetime.now(UTC)
                audit_repository.add_state_transition(
                    session,
                    resource_type="CLIENT",
                    client_id=client.id,
                    from_state=source_status,
                    to_state=target_status,
                    principal=principal,
                    request_id=request_id,
                    reason=reason,
                )
                audit_repository.add_success_event(
                    session,
                    principal=principal,
                    request_id=request_id,
                    event_code=event_code,
                    resource_kind="CLIENT",
                    resource_id=client.id,
                    sanitized_reason="state_changed",
                )
                return ClientData(
                    id=client.id,
                    client_code=client.client_code,
                    name=client.name,
                    status=client.status,
                )
        except ResourceNotFound:
            record_denial(
                session,
                principal=principal,
                request_id=request_id,
                event_code=event_code,
                reason="resource_not_in_scope",
            )
            raise
        except IntegrityError as exc:
            raise ResourceConflict from exc
