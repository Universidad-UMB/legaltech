from typing import Literal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.authorization.domain import (
    require_external_reader,
    require_internal_account,
    require_internal_role,
)
from app.core.errors import ForbiddenOperation
from app.identity.domain import Principal
from app.identity.models import AuditEvent

DenialReason = Literal[
    "permission_denied",
    "resource_not_in_scope",
    "related_resource_not_found",
]


def authorize_internal_roles(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
    allowed_roles: set[str] | frozenset[str],
) -> None:
    try:
        require_internal_role(principal, allowed_roles)
    except ForbiddenOperation:
        record_denial(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            reason="permission_denied",
        )
        raise


def authorize_internal_account(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
) -> None:
    try:
        require_internal_account(principal)
    except ForbiddenOperation:
        record_denial(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            reason="permission_denied",
        )
        raise


def authorize_external_reader(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
) -> None:
    try:
        require_external_reader(principal)
    except ForbiddenOperation:
        record_denial(
            session,
            principal=principal,
            request_id=request_id,
            event_code=event_code,
            reason="permission_denied",
        )
        raise


def record_denial(
    session: Session,
    *,
    principal: Principal,
    request_id: UUID,
    event_code: str,
    reason: DenialReason,
) -> None:
    if session.in_transaction():
        session.rollback()
    with session.begin():
        session.add(
            AuditEvent(
                id=uuid4(),
                request_id=request_id,
                event_code=event_code,
                result="DENIED",
                actor_account_id=principal.account_id,
                sanitized_reason=reason,
            )
        )
