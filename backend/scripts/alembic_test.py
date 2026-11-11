from __future__ import annotations

import argparse
import os

from alembic import command
from alembic.config import Config

from app.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a limited Alembic command against the isolated legaltech_test database."
    )
    parser.add_argument("action", choices=("upgrade", "downgrade", "current", "check"))
    parser.add_argument("revision", nargs="?", choices=("head", "base"))
    args = parser.parse_args()

    if args.action in {"upgrade", "downgrade"} and args.revision is None:
        parser.error("upgrade and downgrade require an explicit head or base revision")
    if args.action in {"current", "check"} and args.revision is not None:
        parser.error("current and check do not accept a revision")

    settings = Settings()
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = settings.test_database()
    os.environ["MIGRATION_DATABASE_URL"] = settings.test_database(migration=True)
    config = Config("alembic.ini")
    print(f"Running Alembic {args.action} against legaltech_test.", flush=True)

    if args.action == "upgrade":
        command.upgrade(config, args.revision)
    elif args.action == "downgrade":
        command.downgrade(config, args.revision)
    elif args.action == "current":
        command.current(config, verbose=True)
    else:
        command.check(config)


if __name__ == "__main__":
    main()
