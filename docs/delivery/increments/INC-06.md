# Evidencia de ejecución — INC-06

- Fecha: 2026-11-10
- Rama: `agent/legaltech-backend`
- HEAD previo al trabajo: `791bf6f`
- Base verificada: `legaltech_test`, PostgreSQL 16.6, Compose `legaltech-backend`
- Python: 3.12.13
- Prerrequisitos: INC-05 y las aprobaciones de demostración requeridas constan aceptadas en el registro de gobernanza, consultado en modo lectura.

## Cambios

- Se implementaron las cinco operaciones canónicas `portalTrackings`, `portalCurrentPublication`, `suspendClient`, `reactivateClient` y `finishTracking`. El OpenAPI canónico no se modificó y el contrato runtime valida rutas, métodos, operation IDs y schemas.
- El portal deriva el cliente de la sesión externa, filtra por alcance activo `READ_PUBLICATIONS`, y devuelve solo seguimientos y clientes activos. Los UUID fuera de alcance, de otro cliente, suspendidos o finalizados reciben el mismo `404` genérico. La ausencia autorizada de publicación vigente devuelve `200`, sin contenido.
- Las lecturas exponen únicamente la versión corriente `PUBLISHED` y reportan la cobertura de la adquisición más reciente como `COMPARABLE`, `INCOMPLETE`, `FAILED` o `NOT_OBSERVED`. La lista usa paginación por cursor UUID y rechaza parámetros de tenant aportados por el cliente.
- `ADMIN` puede suspender y reactivar clientes. Un `ADMIN` o `ANALYST` asignado puede finalizar un seguimiento activo. Cada transición exige motivo y persiste el estado, el historial con actor y el evento de auditoría en una transacción; los fallos revierten los tres cambios.
- Se reutilizó el esquema de transiciones existente; no fue necesaria una migración. No se añadieron integraciones reales ni se editaron `uv.lock`, el OpenAPI, gobernanza, `.autopilot/` u orquestación.
- Las pruebas INC-06 cubren aislamiento de tenant y scope, paginación y cobertura, lecturas tras cambios de estado, conservación de publicaciones e historial, rollback y la concurrencia entre publicación y suspensión.

## Archivos

- `app/audit/`: utilidades compartidas para registrar transiciones y auditoría.
- `app/portal/`: router, modelos de dominio, schemas, consultas y servicio del portal.
- `app/authorization/domain.py`, `app/authorization/service.py`: autorización del lector externo.
- `app/clients/`: suspensión/reactivación transaccional de clientes.
- `app/trackings/`: finalización transaccional de seguimientos.
- `app/main.py`: registro del router y respuestas de problema uniformes.
- `tests/test_portal_api.py`, `tests/test_runtime_contract.py`: flujos, aislamiento, concurrencia y contrato runtime.
- `README.md`: operaciones y límites del portal INC-06.
- `docs/delivery/increments/INC-06.md`: esta evidencia.

## Verificaciones ejecutadas

| Comando | Resultado |
|---|---|
| `uv sync --frozen` | PASS; ejecutado por `scripts/quality.ps1`; lock sin cambios. |
| `uv run ruff check app migrations scripts tests` | PASS; ejecutado por el script de calidad. |
| `uv run ruff format --check app migrations scripts tests` | PASS; 94 archivos ya formateados. |
| `uv run mypy app` | PASS; 69 archivos fuente, sin errores. |
| `uv run pytest -q tests/test_runtime_contract.py tests/test_portal_api.py` | PASS; 6 pruebas aprobadas en 11.60 s. |
| `uv run pytest -q` | PASS; 51 pruebas aprobadas en 59.40 s. |
| `uv run python -m scripts.alembic_test current` | PASS; `0006_versioned_publications` es `head` en `legaltech_test`. |
| `uv run python -m scripts.alembic_test check` | PASS; no se detectaron operaciones de migración pendientes. |
| `uv run python -m scripts.alembic_test upgrade head` | PASS; aplicado contra `legaltech_test`. |
| `uv run python -m scripts.alembic_test current` | PASS; sigue en `0006_versioned_publications` después de la actualización. |
| `docker compose --project-name legaltech-backend exec -T db psql --version` | PASS; PostgreSQL 16.6. |
| `git diff --check` | PASS; sin errores de whitespace. |

Las pruebas usaron exclusivamente datos sintéticos en la base aislada `legaltech_test`. No se creó commit; el orquestador verificará y cerrará el incremento.
