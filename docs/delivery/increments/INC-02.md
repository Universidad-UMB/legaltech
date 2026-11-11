# INC-02 — Evidencia de implementación y ejecución

**Corte:** 2026-11-10
**Alcance:** adquisiciones sintéticas `DEMO-FIXTURE`, snapshots sellados, adopción de baseline y autorización contextual.
**Resultado técnico local:** PASS en las verificaciones listadas. La decisión del gate corresponde al orquestador.

## Prerrequisitos revisados

- INC-01 se encuentra implementado y la rama de trabajo parte de la migración `0002_clients_processes_trackings`.
- `governance/APROBACION-DEMO-001.json` registra `ACEPTAR` para DF5-01…06 y la aceptación técnica. El acta se leyó sin modificarla.
- El OpenAPI canónico y los fixtures sintéticos se usaron como contratos. No se cambiaron el YAML, los manifiestos canónicos de pruebas ni los datos de `fixtures/`.

## Cambios

- Se implementaron los cuatro `operationId` de INC-02: `createAcquisition`, `getAcquisition`, `getObservation` y `adoptObservation`. El runtime conserva las rutas y esquemas del OpenAPI canónico.
- El adaptador carga exclusivamente `OBS_001`, `OBS_002`, `FAILED` e `INCOMPLETE` desde el bundle sintético. Compose monta `../fixtures` en `/fixtures` como solo lectura.
- `request_key` es único. La misma carga devuelve el mismo run con HTTP 200; otra carga con la misma clave devuelve 409. El hash privado del payload permite detectar la diferencia sin exponerlo en la respuesta.
- Los runs `FAILED` e `INCOMPLETE` preservan el resultado de cobertura y no crean observación. Las adquisiciones exitosas persisten las actuaciones y sellan la observación dentro de la misma transacción.
- La migración `0003_synthetic_acquisitions` crea `acquisition_runs`, `observations` y `observed_actions`; añade FKs compuestas de baseline al mismo proceso; y crea triggers de finalización única, aceptación, sellado, append-only, y orden de baseline.
- Crear adquisiciones requiere `ADMIN` o `ANALYST` asignado a un seguimiento activo de un cliente activo. Lecturas requieren cuenta interna asignada a algún seguimiento del proceso. La adopción requiere `ANALYST` asignado al seguimiento activo.
- La primera adopción fija baseline y último adoptado. Repetir la misma adopción responde `ALREADY_ADOPTED`. Una adopción posterior sin evaluación devuelve 409 y conserva el cursor; INC-02 no crea comparaciones ni evaluaciones.
- Se actualizó la limpieza de pruebas para truncar tablas únicamente en `legaltech_test`, necesario para probar evidencia append-only sin desactivar sus triggers.

## Relación de pruebas

`tests/test_acquisitions_api.py` cubre AT-03/15, DT-07..12, API-N13/N23/N24/N28 y TEST-ORD-01/05/06: primera baseline de A sin novedad histórica, baseline inicial de B sobre OBS-002, 409 sin evaluación, fallos y cobertura explícita, aislamiento por asignación, request_key idempotente, restricciones de sellado y concurrencia con sesiones independientes.

`tests/test_runtime_contract.py` compara rutas, operationId, modelos, estados y media types con el OpenAPI canónico. `tests/test_postgres_schema.py` comprueba revisión, tablas, privilegios del rol runtime y triggers en PostgreSQL real.

## Comandos y resultados reales

| Comando / comprobación | Resultado |
|---|---|
| `uv lock --check` | PASS; 52 paquetes resueltos, lock sincronizado |
| `uv run python -m scripts.alembic_test downgrade base` | PASS en `legaltech_test` aislada |
| `uv run python -m scripts.alembic_test upgrade head` | PASS en `legaltech_test` aislada |
| `uv run python -m scripts.alembic_test current` | `0003_synthetic_acquisitions (head)` |
| `uv run python -m scripts.alembic_test check` | PASS; `No new upgrade operations detected` |
| `./scripts/quality.ps1` | PASS; Ruff, formato (57 archivos), mypy (40 fuentes) y pytest |
| Pytest dentro de quality | **32 passed in 18.92s** |
| `docker compose --project-name legaltech-backend --profile tools run --rm migrate` | PASS; migración aplicada a `legaltech_demo` local |
| `docker compose --project-name legaltech-backend --profile tools run --rm migrate current` | `0003_synthetic_acquisitions (head)` |
| `docker compose --project-name legaltech-backend up -d --build api` | PASS; API local en puerto host 8001 |
| Smoke HTTP a `/healthz` y `/openapi.json` | PASS; ambos HTTP 200; 15 operationId, incluidos los cuatro de INC-02 |
| `docker compose --project-name legaltech-backend exec -T api python -c "from app.acquisitions.fixture_adapter import load_fixture; item=load_fixture('OBS_001'); print(item.fixture_code, item.process_alias, len(item.actions), item.status)"` | PASS; contenedor leyó `/fixtures`, `PROC-001`, 5 actuaciones, `SUCCESS` |
| `git diff --check` | PASS |

## Límites y entrega

- No se conectaron fuentes judiciales, LLM, OCR, correo, PDF ni servicios productivos.
- No se editó `contratos/API-001.openapi.yaml`, `docs/testing/specifications/`, `governance/`, `.autopilot/`, `AGENTS.md` ni `AGENT.md`.
- No se ejecutaron `git add`, commit o push. Las pruebas usan solamente la base aislada `legaltech_test`; la migración local de demo es aditiva y se ejecutó en el proyecto Compose `legaltech-backend`.
- El reporte documenta ejecución técnica; no sustituye la decisión del orquestador sobre el gate.
