from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.trackings.models import InternalTrackingAssignment, Tracking


def add_client(
    session: Session,
    *,
    client_id: UUID,
    client_code: str,
    name: str,
) -> Client:
    client = Client(
        id=client_id,
        client_code=client_code,
        name=name,
        status="ACTIVE",
    )
    session.add(client)
    session.flush()
    return client


def client_for_assigned_account(
    session: Session, *, client_id: UUID, account_id: UUID
) -> Client | None:
    assignment_exists = exists(
        select(1)
        .select_from(Tracking)
        .join(
            InternalTrackingAssignment,
            InternalTrackingAssignment.tracking_id == Tracking.id,
        )
        .where(
            Tracking.client_id == Client.id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    return session.scalar(select(Client).where(Client.id == client_id, assignment_exists))
