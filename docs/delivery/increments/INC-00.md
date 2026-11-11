# INC-00 — Evidencia de implementación y ejecución

**Corte:** 2026-11-10
**Alcance:** identidad, núcleo API, clientes ficticios, auditoría de autenticación y calidad local.
**Resultado de ejecución local:** PASS para las verificaciones de INC-00 incluidas aquí. El gate del incremento sigue bajo decisión del orquestador.

## Cambios

- FastAPI implementa solamente `healthz`, `login`, `logout` y `getPrincipal`. Los errores de autenticación y validación usan `application/problem+json` y `X-Request-ID`; Swagger y `/openapi.json` se habilitan solo en `APP_ENV=local`.
- Identidad en capas: dominio sin dependencias web/ORM, servicios de aplicación, repositorio SQLAlchemy y DTO separados. Las contraseñas se guardan con Argon2id. Las sesiones usan tokens opacos aleatorios, digest SHA-256, expiración absoluta de 60 minutos y revocación.
- Los rechazos de login y bearer se auditan con causas constantes y sanitizadas; los eventos no guardan contraseñas, tokens ni recursos ajenos.
- La migración Alembic crea `persons`, `clients`, `accounts`, `account_roles`, `auth_sessions` y `audit_events`. `audit_events` se crea en INC-00 porque este ticket lo requiere para autenticación; `clients` se necesita para el bootstrap. La migración candidata DATA-MIG-001 ubicaba auditoría en una revisión posterior.
- Compose usa el proyecto `legaltech-backend`, PostgreSQL 16.6 y credenciales separadas de runtime/migración. La base de pruebas es `legaltech_test`; el runtime no recibe privilegios DDL y no puede actualizar ni borrar filas de auditoría.
- El bootstrap lee el fixture sintético existente, exige una contraseña externa o entrada oculta, y realiza upsert de personas, clientes, cuentas y roles. No crea procesos, seguimientos, observaciones ni publicaciones.
- `scripts/quality.ps1` es la entrada local reproducible para sync, Ruff, mypy y pytest.

## Verificaciones ejecutadas

| Comando / comprobación | Resultado real |
|---|---|
| `uv lock --check` | PASS; lock sincronizado con `pyproject.toml` |
| `uv sync --frozen` | PASS; entorno creado con Python 3.12.13 |
| `docker compose --project-name legaltech-backend up -d db` | PASS; PostgreSQL saludable en `127.0.0.1:55432` |
| `uv run python -m scripts.alembic_test upgrade head` | PASS sobre `legaltech_test` |
| `uv run python -m scripts.alembic_test current` | `0001_identity_clients_audit (head)` |
| `uv run python -m scripts.alembic_test check` | PASS; `No new upgrade operations detected` |
| `uv run python -m scripts.alembic_test downgrade base` y luego `upgrade head` | PASS; downgrade/reconstrucción sobre la base aislada de pruebas |
| `docker compose --project-name legaltech-backend --profile tools run --build --rm migrate` | PASS; Alembic ejecutado desde el servicio de migración Compose |
| `docker compose --project-name legaltech-backend up -d --build api` | PASS; API reconstruida y escuchando solo en `127.0.0.1:8001` |
| Bootstrap real contra `legaltech_demo` | PASS dos o más ejecuciones; resultado estable: 7 personas, 2 clientes, 8 cuentas, 8 roles; cero procesos/seguimientos/observaciones/publicaciones |
| Smoke API en Compose | PASS: `/healthz` 200, login válido, `/auth/me`, logout 204 y logout repetido 401 |
| `./scripts/quality.ps1` | PASS: Ruff check, Ruff format, mypy (`14 source files`) y pytest |
| `pytest -q` | PASS: 14 pruebas en PostgreSQL real; sin advertencias |

## Cobertura añadida

- API: login válido, credenciales inválidas genéricas, sesión expirada/revocada con auditoría, cuenta deshabilitada, principal, logout y reintento, 422 problem+json, 401 bearer y 429.
- PostgreSQL: revisión Alembic, privilegios mínimos de runtime, digest de 32 bytes, restricción de cuenta externa con cliente y correspondencia entre tipo de cuenta y rol.
- Contrato: se verifican las cuatro operaciones INC-00 contra las rutas canónicas, sus operationId, seguridad bearer, media type de errores, esquema `Principal` y Swagger deshabilitado en entorno test. El YAML canónico no se modificó.

## Límites y estado

- No se modificaron archivos fuera de `backend/`; tampoco `AGENTS.md`, `AGENT.md`, gobierno, `.autopilot/`, OpenAPI canónico ni manifiestos canónicos de pruebas. No se hizo commit.
- Un proceso preexistente escuchaba en el puerto host `5433`; quedó intacto. LegalTech usa `55432` para PostgreSQL y `8001` para FastAPI.
- El throttling de login vive en memoria porque el despliegue es una sola instancia local. No es un control distribuido ni una declaración de seguridad productiva.
- No se conectaron fuentes judiciales, correo, OCR, PDF, LLM ni servicios productivos.
