from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
