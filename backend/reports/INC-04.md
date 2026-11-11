# Evidencia de ejecución — INC-04

- Fecha: 2026-11-10
- Rama: `agent/legaltech-backend`
- HEAD previo al trabajo: `0c55309`
- Revisión Alembic: `0005_human_novelty_reviews`
- Base verificada: `legaltech_test`, PostgreSQL 16.6, Compose `legaltech-backend`
- Python: 3.12.13
- Prerrequisito: `governance/APROBACION-DEMO-001.json` registra DF5-03 como `ACEPTAR`.

## Cambios

- Se implementaron las cinco operaciones canónicas `listNovelties`, `getNovelty`, `startOperativeReview`, `escalateNovelty` y `recordLegalReview`. El OpenAPI canónico no se modificó; el contrato runtime se compara con sus rutas y schemas.
- `ANALYST` asignado inicia y escala la revisión; `LAWYER` asignado registra la valoración humana después de la escalación. El abogado y el analista deben tener `person_id` distintos, incluso si una persona usa varias cuentas.
- La identidad del actor se obtiene de la sesión. Campos extra como un actor enviado por el cliente se rechazan con 422. Recursos sin asignación producen 404 genérico y los roles no habilitados reciben 403.
- Escalación y valoración guardan una revisión inmutable con decisión, evidencia ficticia, cuenta, persona y fecha. Cada cambio de estado guarda su transición y auditoría en la misma transacción.
- Las consultas protegidas registran auditoría de éxito sanitizada; las denegaciones por rol o asignación se conservan sin identificadores de recursos ajenos ni contenido de revisión.
- La lista usa paginación keyset por fecha/UUID. Las lecturas devuelven solo los campos del schema canónico de novedad y no exponen notas de revisión.
- La migración añade `novelty_reviews` y `state_transitions`, la clave compuesta cuenta-persona, restricciones, índices, triggers append-only y privilegios runtime de solo inserción/lectura para el historial. `audit_events` existente se reutiliza para acciones exitosas y denegaciones.

## Archivos

- `app/novelties/`: modelos, dominio, repositorio, servicio, schemas y controladores de revisión humana.
- `app/identity/models.py`, `app/main.py`: relación de integridad cuenta-persona y registro/contrato runtime.
- `migrations/versions/0005_human_novelty_reviews.py`: tablas, constraints, triggers y privilegios.
- `tests/test_novelties_api.py`: AT-07/08, API-N16/17, DT-22/36/39, cursor, 404/403/409/422, auditoría, append-only y rollback transaccional.
- `tests/test_runtime_contract.py`, `tests/test_postgres_schema.py`, `tests/conftest.py`: contrato OpenAPI runtime, esquema PostgreSQL y aislamiento de fixtures.
- `README.md`: descripción de las rutas y límites del flujo humano.
- `reports/INC-04.md`: esta evidencia.

## Verificaciones ejecutadas

| Comando | Resultado |
|---|---|
| `uv sync --frozen` | PASS; ejecutado por `scripts/quality.ps1`, lock sin cambios. |
| `./scripts/quality.ps1` | PASS, código 0; sincronización, Ruff, mypy y pytest. |
| `uv run ruff check app migrations scripts tests` | PASS. |
| `uv run ruff format --check app migrations scripts tests` | PASS; 76 archivos ya formateados. |
| `uv run mypy app` | PASS; 54 archivos fuente, sin errores. |
| `uv run pytest -q` | PASS; 43 pruebas, 43 pasaron en 37.29 s. |
| `uv run pytest -q tests/test_runtime_contract.py` | PASS; 2 pruebas pasaron. |
| `uv run python -m scripts.alembic_test downgrade base` | PASS en `legaltech_test` aislada. |
| `uv run python -m scripts.alembic_test upgrade head` | PASS en `legaltech_test` aislada. |
| `uv run python -m scripts.alembic_test current` | PASS; `0005_human_novelty_reviews` es `head`. |
| `uv run python -m scripts.alembic_test check` | PASS; no hay operaciones nuevas de migración. |
| `docker compose --project-name legaltech-backend exec -T db psql --version` | PASS; PostgreSQL 16.6. |
| `git diff --check` | PASS; sin errores de whitespace. |

## Alcance de entrega

Se usaron solo identidades, procesos, adquisiciones, observaciones y notas sintéticas en PostgreSQL local aislado. No se añadieron conectores judiciales, LLM, OCR, correo, PDF ni servicios productivos. `uv.lock` y `contratos/API-001.openapi.yaml` permanecen sin cambios. No se creó commit; queda para la verificación del orquestador.
