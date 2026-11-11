from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.identity.models import Account, AccountRole, AuditEvent, AuthSession


def account_by_username(session: Session, username: str) -> Account | None:
    return session.scalar(select(Account).where(Account.username == username))


def active_session_by_digest(
    session: Session, token_digest: bytes, now: datetime
) -> tuple[AuthSession, Account] | None:
    row = session.execute(
        select(AuthSession, Account)
        .join(Account, Account.id == AuthSession.account_id)
        .where(
            AuthSession.token_digest == token_digest,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
            Account.status == "ACTIVE",
        )
    ).one_or_none()
    return (row[0], row[1]) if row is not None else None


def roles_for_account(session: Session, account_id: UUID) -> tuple[str, ...]:
    roles = session.scalars(
        select(AccountRole.role_code)
        .where(AccountRole.account_id == account_id)
        .order_by(AccountRole.role_code)
    )
    return tuple(roles)


def revoke_active_session(session: Session, session_id: UUID, now: datetime) -> UUID | None:
    result = session.execute(
        update(AuthSession)
        .where(
            AuthSession.id == session_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > now,
        )
        .values(revoked_at=now)
        .returning(AuthSession.account_id)
    )
    return result.scalar_one_or_none()


def record_audit_event(
    session: Session,
    *,
    request_id: UUID,
    event_code: str,
    result: str,
    actor_account_id: UUID | None = None,
    sanitized_reason: str | None = None,
) -> None:
    session.add(
        AuditEvent(
            id=uuid4(),
            request_id=request_id,
            event_code=event_code,
            result=result,
            actor_account_id=actor_account_id,
            sanitized_reason=sanitized_reason,
        )
    )
