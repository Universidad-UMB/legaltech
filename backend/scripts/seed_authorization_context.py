from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from sqlalchemy import select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.clients.models import Client
from app.config import Settings
from app.db import create_database_engine, session_factory
from app.identity.models import Account, AccountRole
from app.identity.service import normalize_username
from app.trackings.models import (
    ExternalTrackingScope,
    InternalTrackingAssignment,
    JudicialProcess,
    Tracking,
)

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "PROTO-DAT-001.json"
EXTERNAL_PERMISSION = "READ_PUBLICATIONS"


def _records(fixture: dict[str, object], field: str) -> list[dict[str, object]]:
    value = fixture.get(field)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"Synthetic fixture field {field!r} is missing or invalid")
    return cast(list[dict[str, object]], value)


def _string(record: dict[str, object], field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Synthetic fixture field {field!r} is missing or invalid")
    return value


def _string_list(record: dict[str, object], field: str) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Synthetic fixture field {field!r} is missing or invalid")
    return cast(list[str], value)


def _resolve_accounts(session: Session, fixture: dict[str, object]) -> dict[str, Account]:
    account_specs = _records(fixture, "accounts")
    resolved: dict[str, Account] = {}
    clients = {_string(row, "alias"): row for row in _records(fixture, "clients")}
    for spec in account_specs:
        username = normalize_username(_string(spec, "username"))
        expected_kind = _string(spec, "kind")
        account = session.scalar(select(Account).where(Account.username == username))
        if account is None or account.status != "ACTIVE" or account.account_kind != expected_kind:
            raise ValueError(f"Fixture account {username!r} is not present and active")

        client_ref = spec.get("client_ref")
        if expected_kind == "EXTERNAL":
            if not isinstance(client_ref, str) or client_ref not in clients:
                raise ValueError(f"Fixture account {username!r} has no valid client")
            client_code = _string(clients[client_ref], "client_code")
            expected_client = session.scalar(
                select(Client).where(Client.client_code == client_code)
            )
            if expected_client is None or account.client_id != expected_client.id:
                raise ValueError(f"Fixture account {username!r} has the wrong client")
        elif client_ref is not None or account.client_id is not None:
            raise ValueError(f"Internal fixture account {username!r} cannot have a client")

        expected_roles = set(_string_list(spec, "roles"))
        actual_roles = set(
            session.scalars(
                select(AccountRole.role_code).where(AccountRole.account_id == account.id)
            )
        )
        if not expected_roles.issubset(actual_roles):
            raise ValueError(f"Fixture account {username!r} is missing a required role")
        resolved[username] = account
    return resolved


def _resolve_trackings(session: Session, fixture: dict[str, object]) -> dict[str, Tracking]:
    clients = {_string(row, "alias"): row for row in _records(fixture, "clients")}
    processes = {_string(row, "alias"): row for row in _records(fixture, "processes")}
    resolved: dict[str, Tracking] = {}
    for spec in _records(fixture, "trackings"):
        alias = _string(spec, "alias")
        client_ref = _string(spec, "client")
        process_ref = _string(spec, "process")
        if client_ref not in clients or process_ref not in processes:
            raise ValueError(f"Fixture tracking {alias!r} has an invalid reference")
        client_code = _string(clients[client_ref], "client_code")
        radicado = _string(processes[process_ref], "radicado")
        client = session.scalar(select(Client).where(Client.client_code == client_code))
        process = session.scalar(
            select(JudicialProcess).where(JudicialProcess.radicado == radicado)
        )
        tracking = session.scalar(select(Tracking).where(Tracking.tracking_code == alias))
        if (
            client is None
            or process is None
            or tracking is None
            or tracking.client_id != client.id
            or tracking.process_id != process.id
        ):
            raise ValueError(f"Fixture tracking {alias!r} is not present with matching references")
        resolved[alias] = tracking
    return resolved


def seed_authorization_context(session: Session, fixture: dict[str, object]) -> tuple[int, int]:
    if fixture.get("synthetic_only") is not True:
        raise ValueError("Authorization seeding requires a synthetic-only fixture")
    accounts = _resolve_accounts(session, fixture)
    trackings = _resolve_trackings(session, fixture)
    internal_added = 0
    external_added = 0

    for assignment in _records(fixture, "internal_tracking_assignments"):
        username = normalize_username(_string(assignment, "username"))
        account = accounts.get(username)
        if account is None or account.account_kind != "INTERNAL":
            raise ValueError(f"Internal assignment account {username!r} is invalid")
        for tracking_alias in _string_list(assignment, "trackings"):
            tracking = trackings.get(tracking_alias)
            if tracking is None:
                raise ValueError(f"Internal assignment tracking {tracking_alias!r} is invalid")
            key = (account.id, tracking.id)
            if session.get(InternalTrackingAssignment, key) is None:
                session.add(
                    InternalTrackingAssignment(
                        account_id=account.id,
                        account_kind="INTERNAL",
                        tracking_id=tracking.id,
                    )
                )
                internal_added += 1

    for scope in _records(fixture, "external_tracking_scopes"):
        username = normalize_username(_string(scope, "username"))
        account = accounts.get(username)
        if account is None or account.account_kind != "EXTERNAL" or account.client_id is None:
            raise ValueError(f"External scope account {username!r} is invalid")
        for tracking_alias in _string_list(scope, "trackings"):
            tracking = trackings.get(tracking_alias)
            if tracking is None or tracking.client_id != account.client_id:
                raise ValueError(
                    f"External scope tracking {tracking_alias!r} is outside the client"
                )
            scope_key = (account.id, tracking.id, EXTERNAL_PERMISSION)
            if session.get(ExternalTrackingScope, scope_key) is None:
                session.add(
                    ExternalTrackingScope(
                        account_id=account.id,
                        account_kind="EXTERNAL",
                        client_id=account.client_id,
                        tracking_id=tracking.id,
                        permission_code=EXTERNAL_PERMISSION,
                    )
                )
                external_added += 1

    session.flush()
    return internal_added, external_added


def load_fixture(path: Path = FIXTURE_PATH) -> dict[str, object]:
    value: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("synthetic_only") is not True:
        raise ValueError("Authorization seeding requires the checked-in synthetic-only fixture")
    return cast(dict[str, object], value)


def main() -> None:
    settings = Settings()
    database_url = settings.database()
    parsed_url = make_url(database_url)
    if parsed_url.database != "legaltech_demo" or parsed_url.host not in {
        "localhost",
        "127.0.0.1",
        "db",
    }:
        raise SystemExit("Authorization seeding is restricted to local legaltech_demo.")

    engine = create_database_engine(settings)
    factory = session_factory(engine)
    try:
        with factory.begin() as session:
            internal_added, external_added = seed_authorization_context(session, load_fixture())
    finally:
        engine.dispose()
    print(
        "Authorization context seeded: "
        f"internal_assignments_added={internal_added}, external_scopes_added={external_added}."
    )


if __name__ == "__main__":
    main()
