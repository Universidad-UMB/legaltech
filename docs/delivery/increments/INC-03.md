# Evidencia de ejecución — INC-03

- Fecha: 2026-11-10
- Rama: `agent/legaltech-backend`
- HEAD previo al trabajo: `cdb1d40`
- Revisión Alembic: `0004_comparisons_and_novelties`
- Base verificada: `legaltech_test`, PostgreSQL 16.6
- Python: 3.12.13

## Cambios

- Comparador puro para snapshots sintéticos: calcula claves ACT añadidas, en orden estable, sin comparar texto libre. Pares incompletos, sin sellar, ambiguos o temporalmente invertidos quedan como `NOT_COMPARABLE` sin cambios técnicos.
- Nuevas rutas canónicas `compareObservations`, `getComparison` y `evaluateComparison`, con autorización por rol y asignación. No se modificó `contratos/API-001.openapi.yaml`.
- Persistencia de comparaciones, cambios técnicos, evaluaciones y novedades con claves foráneas compuestas y restricciones únicas. Comparación y evaluación repetidas recuperan los mismos identificadores.
- Evaluación y creación de novedades se guardan en una transacción. El seguimiento se bloquea con `FOR UPDATE`; solo evalúa el siguiente snapshot comparable y solo avanza tras evaluación persistida del par exacto.
- La creación de novedades es contextual al seguimiento; adoptar OBS-002 como primera baseline en B no crea novedades históricas.
- Se mantuvo `adoptObservation` sin ruta nueva y se trasladó su mutación al servicio de seguimientos.

## Archivos

- `app/comparisons/`: dominio, modelos, repositorio, servicio, esquemas y rutas.
- `app/novelties/`: dominio, modelos, repositorio, servicio, esquemas y rutas.
- `app/trackings/service.py`, `app/acquisitions/repository.py` y `app/acquisitions/service.py`: bloqueo, orden e idempotencia del cursor existente.
- `app/main.py` y `migrations/env.py`: registro de rutas, respuestas problem+json y metadatos.
- `migrations/versions/0004_comparisons_and_novelties.py`: migración versionada y reversible.
- `tests/test_comparison_domain.py`, `tests/test_comparisons_api.py`, `tests/test_postgres_schema.py`, `tests/test_runtime_contract.py` y `tests/conftest.py`: reglas, API, concurrencia, restricciones y contrato runtime.
- `README.md`: configuración y comportamiento de INC-03.
- `docs/delivery/increments/INC-03.md`: esta evidencia.

## Verificaciones ejecutadas

| Comando | Resultado |
|---|---|
| `uv sync --frozen` | PASS; dependencias sincronizadas desde `uv.lock` sin cambios al lock. |
| `./scripts/quality.ps1` | PASS, código 0; Ruff check y format, mypy y pytest. |
| `uv run pytest -q` vía script de calidad | PASS; 40 pruebas, 40 pasaron en 27.86 s. |
| `uv run mypy app` vía script de calidad | PASS; 54 archivos fuente, sin errores. |
| `uv run ruff check app migrations scripts tests` vía script de calidad | PASS. |
| `uv run ruff format --check app migrations scripts tests` vía script de calidad | PASS; 74 archivos sin cambios de formato. |
| `uv run python -m scripts.alembic_test downgrade base` | PASS en `legaltech_test` aislada. |
| `uv run python -m scripts.alembic_test upgrade head` | PASS en `legaltech_test` aislada. |
| `uv run python -m scripts.alembic_test current` | PASS; `0004_comparisons_and_novelties` es `head`. |
| `uv run python -m scripts.alembic_test check` | PASS; no hay operaciones nuevas de migración. |
| `docker compose --project-name legaltech-backend exec -T db psql --version` | PASS; PostgreSQL 16.6. |
| `git diff --check` | PASS; sin errores de whitespace. |

Las pruebas ejercitan AT-04/05/06 y los negativos API-N14/15/34. También verifican dos sesiones PostgreSQL concurrentes para comparación, evaluación y adopción; rechazo de evaluación retrospectiva en B; rechazo de saltos de snapshots; y recuperación de la unicidad de ACT-06.

## Alcance de entrega

No se añadieron integraciones externas. `uv.lock` y el OpenAPI canónico permanecen sin cambios. No se creó commit; queda para el orquestador. Estas evidencias describen las verificaciones ejecutadas para INC-03; el gate final corresponde al orquestador.
