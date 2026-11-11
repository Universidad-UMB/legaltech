# Evidencia de ejecución local — INC-07

**Intento:** 4 | **Fecha:** 2026-11-11
**Rama:** `agent/legaltech-backend`
**HEAD base:** `dbc43bf` (sin commit de esta entrega)
**Entorno:** Python 3.12.13, PostgreSQL 16.6, Docker Compose `legaltech-backend`
**Base de pruebas:** `legaltech_test`
**Dictamen técnico:** verificaciones de este reporte PASSED; el orquestador decide el gate definitivo.

## Causa del rechazo previo y corrección

La prueba E2E anterior comprobaba los 18 IDs mediante un conjunto local `covered`, pero esos identificadores no aparecían en los `nodeid` generados por `pytest --collect-only -q`. El gate busca literalmente los IDs de los tres manifiestos en la salida de recolección; por eso faltaban los 93 aunque la prueba E2E tuviera aserciones de cobertura.

Se añadió `tests/traceability.py`, que fija los IDs canónicos como IDs de parámetro de pytest en las pruebas de comportamiento correspondientes. `tests/test_requirement_traceability.py` carga los manifiestos sin modificarlos y verifica que los 93 IDs estén registrados y aparezcan en los `nodeid` recolectados. La recolección final encontró los 93 IDs en 69 ítems.

## Cambios INC-07

- Se conserva el recorrido E2E de los 18 escenarios `PROTO-AT-01..18`: procesos y seguimientos A/B/A2, ACT-06, revisiones humanas, publicación, permisos del portal, cobertura, suspensión, finalización y nueva versión.
- Se añadieron pruebas PostgreSQL de integridad para relaciones entre seguimientos, cambios fuera del snapshot, evaluaciones `SKIPPED` y aprobación por una segunda cuenta de la misma persona.
- Se cubrieron persistencia al recrear FastAPI, seed sintético idempotente, CORS, sanitización de errores y logs, y guardas del reset local. El truncado se probó dentro de una transacción revertida en `legaltech_test`.
- Se añadió `scripts/ci.ps1`; `quality.ps1` analiza `scripts/` con mypy. README y guía REST documentan entorno aislado, seed y reset.
- La trazabilidad de los manifiestos queda ahora visible y comprobable en la salida de pytest. No se modificaron OpenAPI, fixtures canónicos, manifiestos, `uv.lock`, migraciones ni tablas.

## Trazabilidad ejecutable

Los manifiestos `pruebas/PROTO-AT-001.json`, `pruebas/API-NEG-001.csv` y `pruebas/DATA-TEST-001.csv` permanecen intactos. Los IDs se enlazan con pruebas de comportamiento reales:

| Familia | Cobertura y evidencia |
|---|---|
| `PROTO-AT-01..18` | `tests/test_demo_acceptance.py::test_proto_at_01_through_18_full_synthetic_journey`; persistencia, seed y reset también se comprueban en `tests/test_acceptance_infrastructure.py` y `tests/test_reset_demo.py`. |
| `API-N01..04`, `API-N29` | `tests/test_auth_api.py`: bearer ausente/inválido, expiración, revocación, credenciales genéricas, límite de login y cuenta deshabilitada. |
| `API-N05..12`, `API-N34` | Pruebas de roles, asignación, scope, tenant, estado, UUID, radicado y campos no admitidos en `test_clients_tracking_api.py`, `test_novelties_api.py`, `test_acquisitions_api.py` y `test_portal_api.py`. |
| `API-N13..15`, `API-N23..24` | `test_acquisitions_api.py` y `test_comparisons_api.py`: baseline fallida, request keys, idempotencia y concurrencia de evaluación. |
| `API-N16..22`, `API-N33` | `test_novelties_api.py`, `test_publications_api.py` y `test_inc07_integrity.py`: roles de revisión, aprobación por persona distinta, inmutabilidad, publicación y rollback. |
| `API-N25..32`, `API-N35..36` | Validación, sanitización, CORS, persistencia, concurrencia de suspensión y acceso actual en `test_auth_api.py`, `test_acceptance_infrastructure.py` y `test_portal_api.py`. |
| `DT-01..12` | `test_clients_tracking_api.py` y `test_acquisitions_api.py`: radicados, claves/relaciones, scope, adopción, sellado y concurrencia. |
| `DT-13..20` | `test_comparisons_api.py` y `test_inc07_integrity.py`: pares comparables, unicidad, acciones, orden, evaluación y concurrencia de novedades. |
| `DT-21..22`, `DT-39` | `test_portal_api.py` y `test_novelties_api.py`: aislamiento entre cuentas y permisos de revisión. |
| `DT-23..30`, `DT-37..38` | `test_publications_api.py` y `test_inc07_integrity.py`: preparadores, congelación, digest, aprobación, referencias de publicación y atomicidad. |
| `DT-31..36` | `test_portal_api.py` y `test_acceptance_infrastructure.py`: portal, estados, auditoría, seed y persistencia. |

La prueba `tests/test_requirement_traceability.py` compara la lista registrada con los manifiestos y con todos los `nodeid` recogidos; no sustituye las aserciones de comportamiento de las pruebas etiquetadas.

## Verificaciones del intento 4

| Comando o comprobación | Resultado |
|---|---|
| `uv run --frozen pytest --collect-only -q` y comparación con manifiestos | PASS; 69 ítems recolectados y los 93 IDs presentes. |
| `.\scripts\ci.ps1` primera ejecución | FAIL en Ruff por dos imports desordenados `I001`; se corrigieron. |
| `.\scripts\ci.ps1` repetición final | PASS, código 0; usó el servicio del proyecto `legaltech-backend` y `legaltech_test`. |
| `uv lock --check` | PASS; lock sincronizado con 52 paquetes. |
| `uv sync --frozen` | PASS. |
| `uv run ruff check app migrations scripts tests` | PASS; sin hallazgos. |
| `uv run ruff format --check app migrations scripts tests` | PASS; 101 archivos ya formateados. |
| `uv run mypy app scripts` | PASS; 75 archivos fuente, sin errores. |
| `uv run pytest -q` | PASS; 67 pruebas en 93.38 s contra PostgreSQL `legaltech_test`. |
| `uv run python -m scripts.alembic_test upgrade head` | PASS contra `legaltech_test`. |
| `uv run python -m scripts.alembic_test current` | PASS; `0006_versioned_publications` es `head`. |
| `uv run python -m scripts.alembic_test check` | PASS; `No new upgrade operations detected`. |
| `docker compose --project-name legaltech-backend exec -T db psql -U legaltech_admin -d legaltech_test -tAc 'show server_version;'` | PASS; PostgreSQL 16.6. |
| `uv run --frozen python ../orchestration/check_runtime_openapi.py --through INC-07` | PASS; coincide con las 35 operaciones HTTP canónicas. |
| `git diff --check` | PASS dentro de CI; sin errores de whitespace. |

En este intento, la primera CI se detuvo por Ruff antes de ejecutar pytest; tras corregir los dos imports, la repetición completa pasó. El reset real de `legaltech_demo` no se ejecutó para preservar datos persistidos. No se reinició ni limpió el volumen. No se modificaron `governance/APROBACION-DEMO-001.json`, `.autopilot/`, orquestación, OpenAPI, fixtures ni manifiestos. No se hizo `git add`, commit, push o despliegue.

## Archivos de INC-07

- `scripts/ci.ps1`, `scripts/reset_demo.py`, `scripts/bootstrap_demo.py`, `scripts/quality.ps1`
- `tests/traceability.py`, `tests/test_requirement_traceability.py`, `tests/test_demo_acceptance.py`, `tests/test_inc07_integrity.py`, `tests/test_acceptance_infrastructure.py`, `tests/test_reset_demo.py`
- Pruebas API etiquetadas por ID canónico en `tests/test_*.py`
- `docs/DEMO-REST.md`, `README.md`, `reports/INC-07.md`, `../docs/ENTREGA-FINAL.md`
