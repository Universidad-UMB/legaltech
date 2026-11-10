# LegalTech backend — INC-00

INC-00 provides the local FastAPI shell, identity and session handling, PostgreSQL migration, synthetic identity bootstrap, and quality checks. It implements only `healthz`, `login`, `logout`, and `getPrincipal` from the canonical OpenAPI contract. The bootstrap creates the synthetic people, Alfa/Beta clients, accounts, and roles; it does not create processes or trackings.

This is a local prototype. It has no connection to judicial sources, LLMs, OCR, email, PDF generation, or production services.

## Local setup

Use Python 3.12 or 3.13, `uv`, and Docker Compose. Run the following commands from `backend/` in PowerShell:

```powershell
python scripts/dev_setup.py
uv sync --frozen
docker compose --project-name legaltech-backend up -d db
```

`dev_setup.py` creates an untracked `.env` containing fresh, URL-safe database passwords for the isolated Compose project. It refuses to overwrite an existing file. `DEMO_SEED_PASSWORD` is separate and is requested without echo by the bootstrap command. Keep `.env` local.

The Compose project is named `legaltech-backend`. PostgreSQL is reachable from the host only at `127.0.0.1:55432`; the API is reachable at `http://127.0.0.1:8001`. It does not bind host port 8000. The `db` service initializes two databases: `legaltech_demo` for local use and `legaltech_test` for automated tests. The runtime role has table DML only; the separate migration role is used by the one-off `migrate` Compose service.

Apply the demo migration, then start the API and bootstrap synthetic identities:

```powershell
docker compose --project-name legaltech-backend --profile tools run --rm migrate
docker compose --project-name legaltech-backend up -d --build api
uv run python -m scripts.bootstrap_demo
```

The bootstrap requires a 12–256 character `DEMO_SEED_PASSWORD`, supplied through the hidden prompt or the current shell environment. The same password is assigned to all eight synthetic demo accounts. Re-running the bootstrap updates fixture identities and password hashes and revokes existing sessions for those accounts. It is safe only against the local `legaltech_demo` database.

The local Swagger UI is available at `http://127.0.0.1:8001/docs`. `/healthz` confirms the API process is serving HTTP and intentionally does not claim database health.

## PostgreSQL tests and migrations

Tests require the project database to be running. The test database command is deliberately limited to `legaltech_test`:

```powershell
uv run python -m scripts.alembic_test upgrade head
uv run python -m scripts.alembic_test current
uv run python -m scripts.alembic_test downgrade base
uv run python -m scripts.alembic_test upgrade head
uv run pytest -q
```

The migration test fixture also applies Alembic `head` before tests. Tests connect as `legaltech_runtime` to `legaltech_test`, clear only the identity rows within that database, and verify real PostgreSQL constraints and runtime privileges. They never use `legaltech_demo`.

## Quality checks

```powershell
./scripts/quality.ps1
```

This script runs the frozen dependency sync, Ruff lint and format checks, mypy on `app/`, and pytest. A CI runner can invoke the same script after provisioning the isolated PostgreSQL service and test database.

## Identity and operational boundaries

- Passwords use Argon2id. Session tokens contain 256 bits of random entropy; only the SHA-256 digest is stored. Sessions expire after 60 minutes and logout revokes the current session.
- Invalid credentials share one generic 401 response. Validation failures use sanitized `application/problem+json` responses with `X-Request-ID`.
- Login throttling is in-memory for the single local API worker. It is not a distributed production control.
- Swagger and `/openapi.json` are enabled only in `APP_ENV=local`.
- Database credentials and the bootstrap password are not stored in fixtures or source. The `legaltech_migrator` role is reserved for Alembic; the API runs as `legaltech_runtime`.
- Compose resources use the dedicated `legaltech-backend` project and its own named volume. Do not run global Docker cleanup commands for this project.
