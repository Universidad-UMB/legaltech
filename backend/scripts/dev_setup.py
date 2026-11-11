from __future__ import annotations

import secrets
from pathlib import Path


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    env_path = backend_root / ".env"
    if env_path.exists():
        raise SystemExit("backend/.env already exists; it was left unchanged.")

    admin_password = secrets.token_urlsafe(36)
    runtime_password = secrets.token_urlsafe(36)
    migrator_password = secrets.token_urlsafe(36)
    env_contents = "\n".join(
        [
            "APP_ENV=local",
            f"POSTGRES_ADMIN_PASSWORD={admin_password}",
            f"POSTGRES_RUNTIME_PASSWORD={runtime_password}",
            f"POSTGRES_MIGRATOR_PASSWORD={migrator_password}",
            "DATABASE_URL="
            f"postgresql+psycopg://legaltech_runtime:{runtime_password}@127.0.0.1:55432/legaltech_demo",
            "MIGRATION_DATABASE_URL="
            f"postgresql+psycopg://legaltech_migrator:{migrator_password}@127.0.0.1:55432/legaltech_demo",
            "TEST_DATABASE_URL="
            f"postgresql+psycopg://legaltech_runtime:{runtime_password}@127.0.0.1:55432/legaltech_test",
            "TEST_MIGRATION_DATABASE_URL="
            f"postgresql+psycopg://legaltech_migrator:{migrator_password}@127.0.0.1:55432/legaltech_test",
            "",
        ]
    )
    with env_path.open("x", encoding="utf-8", newline="\n") as env_file:
        env_file.write(env_contents)
    print("Created backend/.env with fresh local PostgreSQL credentials.")
    print("The demo seed password is separate and must be supplied when bootstrap runs.")


if __name__ == "__main__":
    main()
