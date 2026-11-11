# INC-01 — Evidencia de implementación y ejecución

**Corte:** 2026-11-10
**Alcance:** clientes, procesos judiciales, seguimientos, autorización contextual y seed local de asignaciones.
**Resultado técnico local:** PASS en verificaciones listadas. La decisión de gate corresponde al orquestador.

## Prerrequisitos revisados

- `governance/APROBACION-DEMO-001.json` acredita `ACEPTAR` para el alcance técnico y DF5-02/DF5-05. Se leyó sin modificarlo.
- INC-00 estaba implementado; la revisión previa de Alembic era `0001_identity_clients_audit`.
- OpenAPI, dominio, datos, seguridad y fixture se usaron como contratos. No se editaron el OpenAPI canónico ni los manifiestos canónicos de pruebas.

## Cambios

- Se implementaron los siete operationId del ticket: `createClient`, `getClient`, `createProcess`, `getProcess`, `createTracking`, `getTracking` y `activateTracking`.
- Solo ADMIN puede crear clientes, procesos y seguimientos. Las lecturas internas y la activación requieren asignación activa al seguimiento; activar admite ADMIN o ANALYST, solo en estado PENDING y con cliente ACTIVE. Las cuentas externas reciben 403 en la API interna. Recursos internos fuera de asignación devuelven 404 genérico.
- Las altas y activaciones exitosas se auditan en la misma transacción. Denegaciones de rol o ámbito usan causas constantes sin guardar el UUID del recurso ajeno.
- La migración `0002_clients_processes_trackings` añade procesos, seguimientos, scopes externos y asignaciones internas. Incluye radicado de exactamente 23 dígitos y único, máximo un seguimiento PENDING/ACTIVE por cliente/proceso, índices de lectura y FKs compuestas para impedir scopes entre clientes o asignar scopes externos a cuentas internas.
- `trackings` incluye ambas referencias de observación nullable y exige que estén presentes o ausentes juntas. Las FKs a observaciones se agregarán cuando exista esa tabla en el incremento que la implementa.
- `scripts/seed_authorization_context.py` lee el fixture sintético, valida cuentas, roles y relaciones por cliente/proceso, y agrega solo asignaciones y scopes faltantes. Está limitado a `legaltech_demo`; no revoca, reactiva ni reinicia filas. No se ejecutó su entrada CLI contra `legaltech_demo` porque todavía no existen allí los procesos y seguimientos del escenario. Su función se probó en PostgreSQL con el fixture canónico completo.
- Se actualizó `backend/README.md` con rutas, autorización, migraciones y uso del seed local.

## Pruebas relevantes

- AT-01/02: radicado válido; Alfa y Beta sobre PROC-001; SEG-A-002 sobre PROC-002; activación asignada.
- DT-01/02: longitud y caracteres de radicado; radicado duplicado. DT-03: dos clientes comparten proceso. DT-04/05/06: FK compuesta A→B, scope para cuenta interna y duplicado de scope. DT-39: la lectura sin asignación queda oculta con 404; la revisión de novedad se probará cuando exista ese módulo.
- API-N05: cuenta externa rechazada en rutas internas. API-N06: rol sin asignación no obtiene acceso al seguimiento; la ruta de novedades es de otro incremento. Los scopes no cruzan clientes; la denegación de A sin scope para A2 se probará en la ruta de portal, que aún no existe en INC-01.
- Se probaron duplicados con 409, campos extra con 422, Location en altas, respuestas `problem+json`, auditoría sanitizada y códigos `SEG-A-001`, `SEG-B-001`, `SEG-A-002`.
- Dos sesiones PostgreSQL independientes intentaron activar el mismo seguimiento concurrentemente: una obtuvo ACTIVE y la otra conflicto; quedó una sola transición/auditoría.
- El seed ejecutado dos veces agregó 9 asignaciones internas y 2 scopes en la primera ejecución, cero en la segunda; tampoco reactivó una asignación revocada.
- DT-07 (baseline con observación ajena) queda para el incremento de observaciones: `observations` aún no existe en INC-01.
- El test runtime compara rutas/operationId, seguridad bearer, schemas de los seis DTOs INC-01, referencias de request/response y media types con el OpenAPI canónico.

## Comandos y resultados reales

| Comando / comprobación | Resultado |
|---|---|
| `uv lock --check` | PASS; lock sincronizado, 52 paquetes resueltos |
| `uv run python -m scripts.alembic_test downgrade base` | PASS en `legaltech_test` aislada |
| `uv run python -m scripts.alembic_test upgrade head` | PASS en `legaltech_test` aislada |
| `uv run python -m scripts.alembic_test current` | `0002_clients_processes_trackings (head)` |
| `uv run python -m scripts.alembic_test check` | PASS; `No new upgrade operations detected` |
| `docker compose --project-name legaltech-backend --profile tools run --build --rm migrate` | PASS; migración aplicada a la DB local sintética `legaltech_demo` |
| `docker compose --project-name legaltech-backend --profile tools run --rm migrate current` | `0002_clients_processes_trackings (head)` |
| `docker compose --project-name legaltech-backend up -d --build api` | PASS; API actualizada en puerto host 8001 |
| Smoke HTTP con `urllib` a `/healthz` y `/openapi.json` | PASS; HTTP 200, 11 operationId esperados |
| `uv run mypy scripts/seed_authorization_context.py` | PASS; sin errores de tipos |
| `./scripts/quality.ps1` | PASS; sync congelado, Ruff lint/formato, mypy de app y pytest |
| Resultado de pytest dentro de quality | **25 passed in 5.47s**, sin warnings |
| `git diff --check` | PASS |

Una ejecución intermedia encontró problemas en los helpers de datos/transacción de pruebas; se corrigieron antes de la ejecución final. La suite final no reportó fallos ni warnings.

## Límites y entrega

- No se implementaron observaciones, novedades ni portal. Por ello DT-07 y los tramos específicos de API-N06/API-N07 que requieren esos módulos quedan para sus incrementos propietarios.
- Las FKs de baseline hacia observaciones quedan pendientes hasta que la tabla sea creada en su incremento.
- Todos los cambios están en `backend/`. No se modificaron gobierno, orquestación, `.autopilot/`, fixtures canónicos ni pruebas canónicas. No se hizo `git add`, commit o push.
- La rama sigue bajo verificación del orquestador; este reporte no declara aprobado el gate.

## Reintento 3: corrección del falso fallo de pruebas

El log `INC-01-attempt-02-verify-tests.log` mostró un falso positivo en `test_validation_errors_are_problem_json_without_request_values`: buscaba la subcadena `bad` en toda la respuesta y esta también aparece por azar en el UUID `request_id`. La respuesta no estaba reflejando ese valor de entrada. La prueba ahora compara el valor JSON serializado exacto y confirma que tampoco se refleje el campo adicional.

| Comando / comprobación | Resultado real |
|---|---|
| `uv lock --check` | PASS; 52 paquetes resueltos y lock sincronizado |
| `uv run pytest tests/test_auth_api.py::test_validation_errors_are_problem_json_without_request_values -q` | PASS; 1 prueba |
| `uv run python -m scripts.alembic_test downgrade base` y `upgrade head` | PASS en `legaltech_test` aislada |
| `uv run python -m scripts.alembic_test current` | `0002_clients_processes_trackings (head)` |
| `uv run python -m scripts.alembic_test check` | PASS; `No new upgrade operations detected` |
| `./scripts/quality.ps1` | PASS; Ruff lint, formato (47 archivos), mypy (32 archivos) y pytest |
| Resultado pytest dentro de quality | **25 passed in 9.57s**, sin fallos |
