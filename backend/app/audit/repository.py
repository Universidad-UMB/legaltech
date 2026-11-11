from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.identity.domain import Principal
from app.identity.models import AuditEvent
from app.novelties.models import StateTransition


def add_state_transition(
    session: Session,
    *,
    resource_type: Literal["CLIENT", "TRACKING"],
    client_id: UUID | None = None,
    tracking_id: UUID | None = None,
    from_state: str,
    to_state: str,
    principal: Principal,
    request_id: UUID,
    reason: str,
) -> StateTransition:
    transition = StateTransition(
        id=uuid4(),
        resource_type=resource_type,
        client_id=client_id,
        tracking_id=tracking_id,
        from_state=from_state,
        to_state=to_state,
        actor_account_id=principal.account_id,
        actor_person_id=principal.person_id,
        actor_kind="USER",
        request_id=request_id,
        reason=reason,
    )
    session.add(transition)
    session.flush()
    return transition


def add_success_event(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
    resource_kind: str,
    resource_id: UUID,
    sanitized_reason: str = "authorized_operation",
) -> AuditEvent:
    event = AuditEvent(
        id=uuid4(),
        request_id=request_id,
        event_code=event_code,
        result="SUCCESS",
        actor_account_id=principal.account_id,
        resource_kind=resource_kind,
        resource_id=resource_id,
        sanitized_reason=sanitized_reason,
    )
    session.add(event)
    return event


def add_portal_read_event(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
    resource_kind: str,
    resource_id: UUID,
) -> AuditEvent:
    return add_success_event(
        session,
        principal=principal,
        request_id=request_id,
        event_code=event_code,
        resource_kind=resource_kind,
        resource_id=resource_id,
        sanitized_reason="authorized_read",
    )
