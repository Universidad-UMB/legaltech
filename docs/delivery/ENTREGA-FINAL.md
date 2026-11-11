# Entrega técnica final — LegalTech backend

**Fecha:** 2026-11-11
**Intento INC-07:** 4
**Rama de trabajo:** `agent/legaltech-backend`
**HEAD base:** `dbc43bf`
**Entorno verificado:** Python 3.12.13, PostgreSQL 16.6, Compose `legaltech-backend`

## Resultado

INC-07 consolida la aceptación E2E, la integridad PostgreSQL, la trazabilidad de requisitos en pytest, el seed y reset local protegidos, la CI y la guía REST. El gate anterior no encontraba los 93 IDs porque estaban comprobados dentro de una prueba, pero no figuraban en la salida de recolección. Los IDs ahora aparecen en los `nodeid` de pruebas de comportamiento; una prueba de regresión contrasta la recolección con los tres manifiestos canónicos.

La recolección encontró **93 IDs** (18 AT, 36 API-N y 39 DT) en 69 ítems. La CI final pasó con **67 pruebas aprobadas en 93.38 s** en `legaltech_test`; Ruff, mypy, Alembic y la comparación de las 35 operaciones OpenAPI también pasaron. El orquestador determina el gate definitivo.

No se añadieron rutas, tablas ni integraciones reales. No cambiaron el contrato OpenAPI canónico, los manifiestos de pruebas ni `uv.lock`. Las pruebas usan fixtures sintéticos en PostgreSQL dedicado. El reset de `legaltech_demo` no se ejecutó y no se reinició ni limpió el volumen Docker.

## Entorno y reproducción

Desde `backend/` en PowerShell:

```powershell
uv lock --check
uv sync --frozen
.\scripts\ci.ps1
```

La CI inicia solo el servicio PostgreSQL del proyecto Compose `legaltech-backend`, ejecuta Alembic en `legaltech_test` y corre Ruff, formato, mypy, pytest y `git diff --check`. La primera ejecución del intento 4 se detuvo por dos imports desordenados de Ruff; se corrigieron y la repetición completa pasó.

La revisión aplicada fue `0006_versioned_publications`; `alembic check` informó que no hay operaciones sin migración. El reporte [INC-07](increments/INC-07.md) registra los comandos, resultados, trazabilidad y límites.

Para verificar que pytest sigue mostrando todos los IDs de los manifiestos:

```powershell
uv run --frozen pytest --collect-only -q
```

La prueba `tests/test_requirement_traceability.py` hace la misma comprobación durante `pytest -q` y falla si un ID canónico deja de estar registrado o recolectado.

## API y demostración

`uv run --frozen python ../orchestration/check_runtime_openapi.py --through INC-07` pasó y confirmó las 35 operaciones canónicas. La guía REST está en [DEMO-REST.md](../operations/DEMO-REST.md).

El seed de identidades se ejecutó dos veces en `legaltech_test`, comparó conteos, revocó sesiones previas y autenticó de nuevo tras recrear FastAPI. El bootstrap rechaza bases distintas de `legaltech_demo`; una prueba confirma que no modifica la base de pruebas.

El flujo de reset requiere `APP_ENV=local`, `legaltech_demo`, rol migrador, revisión Alembic esperada y `--confirm legaltech_demo`. Preserva la tabla de migraciones y rechaza `legaltech_test`. El reset real no se ejecutó para conservar los datos locales existentes.

## Evidencia principal

| Verificación | Resultado |
|---|---|
| IDs canónicos visibles en recolección | PASS: 93 IDs, 69 ítems. |
| CI completa | PASS: 67 pruebas en 93.38 s. |
| Ruff y formato | PASS: sin hallazgos; 101 archivos formateados. |
| mypy | PASS: 75 archivos fuente. |
| Alembic | PASS: `0006_versioned_publications` es `head`; sin operaciones nuevas. |
| Runtime OpenAPI | PASS: 35 operaciones coinciden con el contrato. |
| PostgreSQL | PASS: 16.6; `legaltech_test` aislada. |
| `git diff --check` | PASS dentro de CI. |

## Límites registrados

- No se hizo un escaneo independiente de secretos del repositorio.
- No se eliminó, reconstruyó ni reinició el volumen Docker.
- No se ejecutó reset de la base persistente `legaltech_demo`.
- La persistencia se verificó recreando FastAPI contra PostgreSQL; no se reinició el contenedor PostgreSQL.
- No se conectaron fuentes judiciales, LLM, OCR, correo, PDF ni servicios productivos.

No se ejecutaron `git add`, commit, push ni despliegues. El orquestador hará la verificación final.
