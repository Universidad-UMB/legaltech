from __future__ import annotations

import getpass
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.engine import make_url

from app.config import Settings
from app.db import create_database_engine, session_factory
from app.identity.models import Account, AccountRole, AuthSession, Client, Person
from app.identity.service import IdentityService, normalize_username

FIXTURE_PATH = Path(__file__).resolve().parents[2] / "fixtures" / "PROTO-DAT-001.json"


def _records(fixture: dict[str, object], name: str) -> list[dict[str, object]]:
    value = fixture.get(name)
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"Synthetic fixture field {name!r} is missing or invalid")
    return cast(list[dict[str, object]], value)


def _string(record: dict[str, object], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Synthetic fixture field {key!r} is missing or invalid")
    return value


def _seed_password() -> str:
    password = os.environ.get("DEMO_SEED_PASSWORD")
    if password is None and sys.stdin.isatty():
        password = getpass.getpass("DEMO_SEED_PASSWORD: ")
    if password is None or len(password) < 12 or len(password) > 256:
        raise SystemExit("Supply a 12–256 character DEMO_SEED_PASSWORD without storing it in Git.")
    return password


def seed_demo(settings: Settings, password: str) -> tuple[int, int, int, int]:
    database_url = settings.database()
    parsed_url = make_url(database_url)
    if parsed_url.database != "legaltech_demo" or parsed_url.host not in {
        "localhost",
        "127.0.0.1",
        "db",
    }:
        raise SystemExit("Bootstrap is restricted to the isolated local legaltech_demo database.")

    fixture_value: object = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(fixture_value, dict) or fixture_value.get("synthetic_only") is not True:
        raise SystemExit("Bootstrap requires the checked-in synthetic-only fixture.")
    fixture = cast(dict[str, object], fixture_value)
    clients = _records(fixture, "clients")
    persons = _records(fixture, "persons")
    accounts = _records(fixture, "accounts")
    if not clients or not persons or not accounts:
        raise SystemExit("Bootstrap fixture must contain demo identities, clients, and accounts.")

    client_ids = {_string(row, "alias"): UUID(_string(row, "id")) for row in clients}
    person_ids = {_string(row, "alias"): UUID(_string(row, "id")) for row in persons}
    identity_service = IdentityService()
    hashed_accounts = [(row, identity_service.hash_password(password)) for row in accounts]

    engine = create_database_engine(settings)
    factory = session_factory(engine)
    try:
        with factory.begin() as session:
            now = datetime.now(UTC)
            for row in clients:
                fixture_client_id = UUID(_string(row, "id"))
                client = session.get(Client, fixture_client_id)
                values = {
                    "client_code": _string(row, "client_code"),
                    "name": _string(row, "name"),
                    "status": _string(row, "status"),
                }
                if client is None:
                    session.add(Client(id=fixture_client_id, **values))
                else:
                    for key, value in values.items():
                        setattr(client, key, value)
                    client.updated_at = now

            for row in persons:
                person_id = UUID(_string(row, "id"))
                person = session.get(Person, person_id)
                if person is None:
                    session.add(
                        Person(
                            id=person_id,
                            display_name=_string(row, "display_name"),
                        )
                    )
                else:
                    person.display_name = _string(row, "display_name")

            session.flush()
            for row, password_hash in hashed_accounts:
                username = normalize_username(_string(row, "username"))
                person_ref = _string(row, "person_ref")
                kind = _string(row, "kind")
                client_ref = row.get("client_ref")
                if person_ref not in person_ids or kind not in {"INTERNAL", "EXTERNAL"}:
                    raise ValueError("Synthetic account identity reference is invalid")
                account_client_id: UUID | None
                if kind == "EXTERNAL":
                    if not isinstance(client_ref, str) or client_ref not in client_ids:
                        raise ValueError(
                            "Synthetic external account must reference its fixture client"
                        )
                    account_client_id = client_ids[client_ref]
                else:
                    if client_ref is not None:
                        raise ValueError("Synthetic internal account cannot reference a client")
                    account_client_id = None

                account_id = UUID(_string(row, "id"))
                account = session.get(Account, account_id)
                if account is None:
                    account = Account(
                        id=account_id,
                        person_id=person_ids[person_ref],
                        username=username,
                        password_hash=password_hash,
                        account_kind=kind,
                        client_id=account_client_id,
                        status=_string(row, "status"),
                    )
                    session.add(account)
                else:
                    account.person_id = person_ids[person_ref]
                    account.username = username
                    account.password_hash = password_hash
                    account.account_kind = kind
                    account.client_id = account_client_id
                    account.status = _string(row, "status")
                    session.execute(
                        update(AuthSession)
                        .where(
                            AuthSession.account_id == account_id, AuthSession.revoked_at.is_(None)
                        )
                        .values(revoked_at=now)
                    )
                    session.execute(delete(AccountRole).where(AccountRole.account_id == account_id))

                roles_value = row.get("roles")
                if not isinstance(roles_value, list) or not all(
                    isinstance(role, str) for role in roles_value
                ):
                    raise ValueError("Synthetic fixture account roles are invalid")
                for role in cast(list[str], roles_value):
                    session.add(
                        AccountRole(account_id=account_id, account_kind=kind, role_code=role)
                    )
        return (
            len(persons),
            len(clients),
            len(accounts),
            sum(len(cast(list[object], row["roles"])) for row in accounts),
        )
    finally:
        engine.dispose()


def main() -> None:
    password = _seed_password()
    try:
        counts = seed_demo(Settings(), password)
    finally:
        password = ""
    persons, clients, accounts, roles = counts
    print(
        "Demo bootstrap complete: "
        f"persons={persons}, clients={clients}, accounts={accounts}, roles={roles}; "
        "no judicial processes, trackings, observations, or publications were created."
    )


if __name__ == "__main__":
    main()
