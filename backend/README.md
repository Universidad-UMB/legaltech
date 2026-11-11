# LegalTech backend — INC-00 a INC-04

INC-00 provides the local FastAPI shell, identity and session handling, PostgreSQL migration, synthetic identity bootstrap, and quality checks. INC-01 adds client, judicial process, and tracking management with contextual internal authorization. INC-02 adds synthetic fixture acquisitions, sealed observations, and tracking baseline adoption. INC-03 adds comparisons and eligibility evaluation. INC-04 adds human novelty reviews. Implemented operation IDs are `healthz`, `login`, `logout`, `getPrincipal`, `createClient`, `getClient`, `createProcess`, `getProcess`, `createTracking`, `getTracking`, `activateTracking`, `createAcquisition`, `getAcquisition`, `getObservation`, `adoptObservation`, `compareObservations`, `getComparison`, `evaluateComparison`, `listNovelties`, `getNovelty`, `startOperativeReview`, `escalateNovelty`, and `recordLegalReview`.

The bootstrap creates synthetic people, Alfa/Beta clients, accounts, and roles. Processes and trackings are created through the API; internal assignments and external scopes remain local seed data and have no API mutation routes.

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

After creating the fixture processes and trackings through the internal API, apply the fixture's internal assignments and external read scopes:

```powershell
uv run python -m scripts.seed_authorization_context
```

This seed is restricted to local `legaltech_demo`, adds only missing assignments/scopes, and does not reactivate revoked rows or reset data. It validates tracking codes and client/process references before committing. The API has no assignment or scope mutation routes.

## INC-02 synthetic acquisitions

`POST /api/v1/internal/acquisition-runs` accepts a process UUID, one of `OBS_001`, `OBS_002`, `FAILED`, or `INCOMPLETE`, and a `request_key`. It only uses the checked-in synthetic fixture bundle mounted read-only at `/fixtures` in Compose; no network source is configured. `ADMIN` or `ANALYST` must have an active assignment to an active tracking for the active client and requested process. Repeating the same key and request returns the existing run with HTTP 200; reusing the key for a different process or fixture returns 409.

Successful fixtures create immutable observations with append-only actions and a database seal. `FAILED` and `INCOMPLETE` runs retain their coverage result and do not create an observation. `GET /acquisition-runs/{run_id}` and `GET /observations/{observation_id}` require an internal account assigned to a tracking on the process. `POST /trackings/{tracking_id}/adoptions` is limited to an assigned analyst: the first comparable, sealed observation sets baseline and last-adopted references; an exact retry returns `ALREADY_ADOPTED`. A later observation returns 409 until a comparison and evaluation exist, so this increment cannot advance a tracking past an unevaluated change.

The local Swagger UI is available at `http://127.0.0.1:8001/docs`. `/healthz` confirms the API process is serving HTTP and intentionally does not claim database health.

## INC-03 comparisons and evaluations

The API compares sealed snapshots from the same process by fixture action key. It reports `ADDED` keys in a stable order and records an explicit `NOT_COMPARABLE` result for snapshots with incomplete quality, missing seals, duplicate action keys, or non-increasing observation times. It does not compare action descriptions or make legal judgments.

`POST /api/v1/internal/comparisons` is limited to an assigned analyst. Repeating the same ordered pair and rule version returns the stored comparison and change IDs. `GET /api/v1/internal/comparisons/{comparison_id}` requires an internal account assigned to the process.

`POST /api/v1/internal/trackings/{tracking_id}/evaluations` locks the assigned active tracking, requires its last adopted snapshot to be the comparison's old snapshot, and requires the new snapshot to be the next comparable snapshot. It creates the evaluation and eligible novelties in one transaction. Repeating the evaluation returns the same IDs. The first adopted snapshot remains a baseline and does not create a retrospective novelty.

The adoption route now advances an existing baseline only after a persisted evaluation for the exact old/new pair. It rejects a backward move, a skipped comparable snapshot, an unassessed pair, and a pair with a non-comparable result. The tracking row lock serializes evaluation and adoption attempts; unique constraints protect retries across database sessions.

## INC-04 human novelty review

Internal users assigned to a tracking can list its novelties and read one novelty. The list uses `limit` and an opaque keyset `cursor`; responses expose only the canonical novelty metadata and never return review notes.

Only an assigned `ANALYST` can start an operative review and escalate it with a decision and synthetic evidence note. Only an assigned `LAWYER` can record the human legal review after escalation. The lawyer must belong to a different `person_id` than the operative reviewer, including when a person has multiple accounts. Actor identity is taken from the authenticated session; actor fields in request bodies are rejected.

Protected reads also record sanitized success audits. Each successful state change locks the novelty and commits its status update, actor-attributed `state_transitions` row, and audit event together. Escalations and legal reviews also append an immutable `novelty_reviews` row with the supplied decision and evidence note. Illegal or repeated state changes return `409`; a role without access returns `403`, and an unassigned internal account receives a generic `404`. These endpoints record fictional human decisions only; they do not calculate legal deadlines or provide legal advice.

## PostgreSQL tests and migrations

Tests require the project database to be running. The test database command is deliberately limited to `legaltech_test`:

```powershell
uv run python -m scripts.alembic_test upgrade head
uv run python -m scripts.alembic_test current
uv run python -m scripts.alembic_test downgrade base
uv run python -m scripts.alembic_test upgrade head
uv run pytest -q
```

The migration test fixture also applies Alembic `head` before tests. Tests connect as `legaltech_runtime` to `legaltech_test`; setup resets only tables in that isolated test database and verifies real PostgreSQL constraints and runtime privileges. They never use `legaltech_demo`.

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

## INC-01 internal API

- Creating clients, processes, and trackings requires an active internal `ADMIN` session. Radicados are text and must contain exactly 23 ASCII digits; duplicate client codes, radicados, or open client/process tracking pairs return `409`.
- Reading a client, process, or tracking requires an internal account with an active assignment to a tracking in that resource's context. Having a role alone does not grant access; unassigned or foreign resources return a generic `404`.
- Activating a tracking requires `ADMIN` or `ANALYST`, an active assignment to that tracking, an active client, and the `PENDING` state. Only `PENDING → ACTIVE` is accepted.
- External accounts cannot call internal routes. Composite PostgreSQL foreign keys prevent an external account from receiving a scope for a different client's tracking and prevent external accounts from appearing in internal assignment rows.
- Tracking codes are allocated locally as `SEG-{initial}-{sequence}` under a PostgreSQL transaction lock. Identifiers remain random UUIDs; the code is not an authorization token.
