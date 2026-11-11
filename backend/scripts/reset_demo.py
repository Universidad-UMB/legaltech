from __future__ import annotations

import argparse
from collections.abc import Sequence

from sqlalchemy import Connection, text
from sqlalchemy.engine import Engine, make_url

from app.config import Settings
from app.db import create_database_engine

DEMO_DATABASE = "legaltech_demo"
DEMO_ALEMBIC_HEAD = "0006_versioned_publications"
RESET_TABLES: tuple[str, ...] = (
    "observed_actions",
    "observations",
    "acquisition_runs",
    "state_transitions",
    "publication_approvals",
    "publication_version_novelties",
    "publication_preparers",
    "publication_versions",
    "publications",
    "novelty_reviews",
    "novelties",
    "tracking_evaluations",
    "technical_changes",
    "comparisons",
    "external_tracking_scopes",
    "internal_tracking_assignments",
    "trackings",
    "judicial_processes",
    "account_roles",
    "auth_sessions",
    "audit_events",
    "accounts",
    "clients",
    "persons",
)


def validate_reset_request(settings: Settings, confirmation: str) -> str:
    if settings.app_env != "local":
        raise ValueError("Demo reset is available only when APP_ENV=local.")

    database_url = settings.database(migration=True)
    url = make_url(database_url)
    if url.database != DEMO_DATABASE:
        raise ValueError("Demo reset is restricted to the legaltech_demo database.")
    if confirmation != DEMO_DATABASE:
        raise ValueError("Pass --confirm legaltech_demo to reset the synthetic demo database.")
    return database_url


def truncate_demo_tables(connection: Connection) -> None:
    tables = ", ".join(f'"{table}"' for table in RESET_TABLES)
    connection.execute(text(f"TRUNCATE TABLE {tables} RESTART IDENTITY"))


def reset_demo_database(engine: Engine) -> str:
    with engine.begin() as connection:
        database_name, role_name = connection.execute(
            text("SELECT current_database(), current_user")
        ).one()
        if database_name != DEMO_DATABASE or role_name != "legaltech_migrator":
            raise ValueError("Reset requires legaltech_migrator on the local legaltech_demo DB.")

        revision = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one_or_none()
        if revision != DEMO_ALEMBIC_HEAD:
            raise ValueError("Demo reset requires the reviewed Alembic head to be applied.")

        truncate_demo_tables(connection)
    return DEMO_DATABASE


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Clear synthetic LegalTech demo data in the isolated local database."
    )
    parser.add_argument(
        "--confirm",
        required=True,
        metavar="DATABASE",
        help="must be exactly legaltech_demo",
    )
    args = parser.parse_args(argv)

    settings = Settings()
    try:
        validate_reset_request(settings, args.confirm)
        engine = create_database_engine(settings, migration=True)
        try:
            target = reset_demo_database(engine)
        finally:
            engine.dispose()
    except ValueError as exc:
        parser.error(str(exc))

    print(f"Synthetic data cleared from {target}; Alembic schema was preserved.")


if __name__ == "__main__":
    main()
