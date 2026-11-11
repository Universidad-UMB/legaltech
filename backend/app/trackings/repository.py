from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import exists, select, text
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.trackings.models import (
    InternalTrackingAssignment,
    JudicialProcess,
    Tracking,
)


def add_process(
    session: Session, *, process_id: UUID, radicado: str, label: str | None
) -> JudicialProcess:
    process = JudicialProcess(id=process_id, radicado=radicado, label=label)
    session.add(process)
    session.flush()
    return process


def process_for_assigned_account(
    session: Session, *, process_id: UUID, account_id: UUID
) -> JudicialProcess | None:
    assignment_exists = exists(
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
    return session.scalar(
        select(JudicialProcess).where(JudicialProcess.id == process_id, assignment_exists)
    )


def tracking_for_assigned_account(
    session: Session,
    *,
    tracking_id: UUID,
    account_id: UUID,
    lock: bool = False,
) -> Tracking | None:
    assignment_exists = exists(
        select(1).where(
            InternalTrackingAssignment.tracking_id == Tracking.id,
            InternalTrackingAssignment.account_id == account_id,
            InternalTrackingAssignment.revoked_at.is_(None),
        )
    )
    statement = select(Tracking).where(Tracking.id == tracking_id, assignment_exists)
    if lock:
        statement = statement.with_for_update(of=Tracking)
    return session.scalar(statement)


def add_tracking(
    session: Session,
    *,
    tracking_id: UUID,
    tracking_code: str,
    client_id: UUID,
    process_id: UUID,
) -> Tracking:
    tracking = Tracking(
        id=tracking_id,
        tracking_code=tracking_code,
        client_id=client_id,
        process_id=process_id,
        status="PENDING",
    )
    session.add(tracking)
    session.flush()
    return tracking


def next_tracking_code(session: Session, client_code: str) -> str:
    prefix_letter = next(
        (character.upper() for character in client_code if character.isalnum()), "X"
    )
    prefix = f"SEG-{prefix_letter}-"
    session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:lock_key))"),
        {"lock_key": f"legaltech-tracking-code:{prefix_letter}"},
    )
    existing = session.scalars(
        select(Tracking.tracking_code).where(Tracking.tracking_code.like(f"{prefix}%"))
    )
    suffixes = [int(code[len(prefix) :]) for code in existing if code[len(prefix) :].isdigit()]
    return f"{prefix}{max(suffixes, default=0) + 1:03d}"


def find_active_client(session: Session, client_id: UUID) -> Client | None:
    return session.scalar(select(Client).where(Client.id == client_id, Client.status == "ACTIVE"))


def find_process(session: Session, process_id: UUID) -> JudicialProcess | None:
    return session.get(JudicialProcess, process_id)


def activate_tracking(tracking: Tracking) -> None:
    tracking.status = "ACTIVE"
    tracking.updated_at = datetime.now(UTC)
