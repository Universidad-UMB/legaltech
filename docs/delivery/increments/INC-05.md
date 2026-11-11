# Evidencia de ejecución — INC-05

- Fecha: 2026-11-10
- Rama: `agent/legaltech-backend`
- HEAD previo al trabajo: `c565dd6`
- Revisión Alembic: `0006_versioned_publications` (head)
- Base verificada: `legaltech_test`, PostgreSQL 16.6, Compose `legaltech-backend`
- Python: 3.12.13
- Prerrequisitos: INC-04 aplicado; `governance/APROBACION-DEMO-001.json` registra DF5-03 y DF5-04 como `ACEPTAR`.

## Cambios

- Se implementaron las siete operaciones canónicas: `createPublication`, `getPublication`, `createPublicationVersion`, `getPublicationVersion`, `submitPublicationVersion`, `decidePublicationVersion` y `publishPublicationVersion`. El OpenAPI canónico no se modificó; el contrato runtime se contrasta con sus rutas y schemas.
- La preparación y creación de versiones requiere rol `PREPARER`, asignación activa a la misma tracking y cliente activos, y novedades `TREATMENT_DEFINED` con revisión legal registrada. La identidad preparadora se obtiene de la sesión.
- Cada borrador guarda texto sintético, destinatario, novedades, preparadoras y SHA-256. Al enviar se congela el snapshot. Una persona con rol `COORDINATOR` y asignación activa puede aprobarlo o rechazarlo si su `person_id` es distinto al de todas las preparadoras; se almacena la decisión con el hash revisado y la justificación.
- Una versión posterior se crea después de que la anterior se publique o rechace, y requiere su propio envío y aprobación. Publicar exige una versión aprobada y un hash coincidente; estado, transición, auditoría y puntero `current_version_id` se confirman en una transacción. Un fallo antes de actualizar el puntero revierte la publicación y conserva la versión vigente anterior.
- La migración añade publicaciones versionadas, aprobaciones inmutables, claves foráneas compuestas y restricciones/triggers de integridad. También integra las transiciones de estado de publicación con el historial existente. La lectura externa del portal corresponde a INC-06 y no se añadió aquí.
- Las pruebas comprueban el puntero vacío antes de publicar y su cambio tras el commit, rechazo de aprobación por la misma persona (incluidas preparadoras secundarias), creación de una versión v2 con aprobación nueva, inmutabilidad del hash y rollback. Una cuenta interna asignada a una tracking Beta recibe 404 al intentar leer una publicación Alfa.
- No se añadieron integraciones judiciales, LLM, OCR, correo, PDF ni servicios productivos. Se usaron datos sintéticos en la base aislada `legaltech_test`.

## Archivos

- `app/publications/`: dominio, schemas, modelos, repositorio, servicio y siete controladores internos.
- `app/main.py`, `app/novelties/models.py`: registro de rutas/respuestas y compatibilidad del historial de transiciones con publicaciones.
- `migrations/env.py`, `migrations/versions/0006_versioned_publications.py`: modelos y migración PostgreSQL de INC-05.
- `tests/test_publications_api.py`: flujo versionado, permisos, separación de personas, hash y congelación, versionado independiente, rollback inyectado y restricciones PostgreSQL.
- `tests/test_runtime_contract.py`, `tests/test_postgres_schema.py`, `tests/conftest.py`: contrato, esquema y limpieza de fixtures aislados.
- `README.md`: setup local e instrucciones del flujo de publicaciones.
- `docs/delivery/increments/INC-05.md`: esta evidencia.

## Verificaciones ejecutadas

| Comando | Resultado |
|---|---|
| `uv sync --frozen` | PASS; ejecutado por `scripts/quality.ps1`, lock sin cambios. |
| `.\scripts\quality.ps1` | PASS, código 0; sync congelado, Ruff, mypy y pytest. |
| `uv run ruff check app migrations scripts tests` | PASS; ejecutado por el script de calidad. |
| `uv run ruff format --check app migrations scripts tests` | PASS; 85 archivos ya formateados. |
| `uv run mypy app` | PASS; 61 archivos fuente, sin errores. |
| `uv run pytest -q` | PASS; 47 pruebas aprobadas en 46.70 s. |
| `uv run --frozen pytest -q tests/test_publications_api.py` | PASS; 4 pruebas aprobadas en 10.07 s, incluyendo aislamiento Alfa/Beta, rollback y restricciones PostgreSQL. |
| `uv run --frozen pytest -q tests/test_runtime_contract.py` | PASS; 2 pruebas aprobadas. |
| `uv run --frozen python -m scripts.alembic_test downgrade base` | PASS en `legaltech_test` aislada. |
| `uv run --frozen python -m scripts.alembic_test upgrade head` | PASS en `legaltech_test` aislada. |
| `uv run --frozen python -m scripts.alembic_test current` | PASS; `0006_versioned_publications` es `head`. |
| `uv run --frozen python -m scripts.alembic_test check` | PASS; no se detectaron operaciones de migración pendientes. |
| `docker compose --project-name legaltech-backend exec -T db psql --version` | PASS; PostgreSQL 16.6. |
| `git diff --check` | PASS; sin errores de whitespace. |

Los primeros chequeos locales detectaron problemas de formato, tipado, metadatos OpenAPI runtime y sintaxis PL/pgSQL en la migración; se corrigieron antes de ejecutar las verificaciones finales. No queda un bloqueo conocido. `uv.lock` y `contratos/API-001.openapi.yaml` permanecen sin cambios. No se creó commit; el orquestador verificará el incremento.
