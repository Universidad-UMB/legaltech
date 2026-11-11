# LegalTech backend — INC-00 a INC-07

INC-00 provides the local FastAPI shell, identity and session handling, PostgreSQL migration, synthetic identity bootstrap, and quality checks. INC-01 adds client, judicial process, and tracking management with contextual internal authorization. INC-02 adds synthetic fixture acquisitions, sealed observations, and tracking baseline adoption. INC-03 adds comparisons and eligibility evaluation. INC-04 adds human novelty reviews. INC-05 adds versioned text publications, independent approval, and atomic selection of the current version. INC-06 adds the external portal, client suspension/reactivation, and tracking finalization. Implemented operation IDs are `healthz`, `login`, `logout`, `getPrincipal`, `createClient`, `getClient`, `suspendClient`, `reactivateClient`, `createProcess`, `getProcess`, `createTracking`, `getTracking`, `activateTracking`, `finishTracking`, `createAcquisition`, `getAcquisition`, `getObservation`, `adoptObservation`, `compareObservations`, `getComparison`, `evaluateComparison`, `listNovelties`, `getNovelty`, `startOperativeReview`, `escalateNovelty`, `recordLegalReview`, `createPublication`, `getPublication`, `createPublicationVersion`, `getPublicationVersion`, `submitPublicationVersion`, `decidePublicationVersion`, `publishPublicationVersion`, `portalTrackings`, and `portalCurrentPublication`.

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

## INC-05 versioned publications

Only an assigned `PREPARER` can create a publication or draft version, and the tracking and client must be active. A draft contains reviewed `TREATMENT_DEFINED` novelties from one tracking, the exact synthetic text, and its SHA-256 digest. The server records the preparer's `person_id` from the authenticated session.

Submitting a draft freezes its text, recipient, novelty links, and preparer list. An assigned `COORDINATOR` can approve or reject that exact snapshot only when their person differs from every preparer. The approval record stores the snapshot digest and justification. A new version can be created after a prior version is published or rejected; it receives a new digest and must be submitted and approved independently.

Publishing requires an approved version whose digest still matches the stored text. The `PUBLISHED` status, state transition, audit event, and `publications.current_version_id` update commit together. A forced failure before the pointer update rolls back the status change and keeps the prior current version. PostgreSQL constraints, triggers, composite foreign keys, and append-only approval/history tables reinforce these rules.

## INC-06 external portal and access restrictions

The portal derives the client from the authenticated external account and requires an active `READ_PUBLICATIONS` scope for each listed or requested tracking. It returns only active trackings for active clients. A direct lookup outside the account's tenant or scope, or for a suspended client or finished tracking, returns the same generic `404` problem response. An authorized tracking without a published current version returns `200` with `available=false` and no publication content.

The portal reports the latest acquisition result as coverage: `COMPARABLE`, `INCOMPLETE`, `FAILED`, or `NOT_OBSERVED`. Failed and incomplete acquisitions never imply no changes. Current publication reads select only a current version whose status is `PUBLISHED`; drafts, rejected versions, and non-current versions are not exposed. Listing uses a UUID keyset cursor and does not accept tenant IDs in query parameters.

Only `ADMIN` can suspend or reactivate a client. An assigned `ADMIN` or `ANALYST` can finish an active tracking. Each transition requires a reason and commits the new state, actor-attributed `state_transitions` history, and audit event in one transaction. These actions keep existing publications and account sessions intact; external access is rechecked against current client and tracking state on each request.

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

This script runs the frozen dependency sync, Ruff lint and format checks, mypy on `app/` and `scripts/`, and pytest. A CI runner can invoke the same script after provisioning the isolated PostgreSQL service and test database.

## INC-07 acceptance, CI, and safe demo reset

The acceptance suite includes an API journey for `PROTO-AT-01..18`, restart persistence checks, PostgreSQL-backed negative and integrity coverage, runtime OpenAPI comparison, and reset-command safety tests. `tests/traceability.py` exposes canonical manifest IDs in pytest node IDs, and `tests/test_requirement_traceability.py` checks all 93 AT, API-N, and DT IDs against the collected test items. Run `uv run --frozen pytest --collect-only -q` from this directory to inspect them. Execution results are recorded in `reports/INC-07.md`.

Run the full local CI entry point from PowerShell. It creates a local `.env` only when absent, starts only the `legaltech-backend` PostgreSQL service, applies migrations to `legaltech_test`, and runs lock, Ruff, mypy, pytest, Alembic, and whitespace checks. It does not stop containers or volumes.

```powershell
.\scripts\ci.ps1
```

The dedicated demo reset requires a local environment, the migration role, the `legaltech_demo` database at the reviewed Alembic head, and an explicit target confirmation. It clears application data but preserves the migration schema. It does not accept `legaltech_test`.

```powershell
uv run python -m scripts.reset_demo --confirm legaltech_demo
uv run python -m scripts.bootstrap_demo
```

`bootstrap_demo` prompts for `DEMO_SEED_PASSWORD` without echo. Recreate processes and trackings through the API, then run `uv run python -m scripts.seed_authorization_context`. Never use a Compose volume removal to reset the demo. See [`docs/DEMO-REST.md`](docs/DEMO-REST.md) for the complete synthetic API sequence.

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
