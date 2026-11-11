---
ticket: INC-02
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-02 — Adquisición sintética y línea base

## Objetivo observable
Adquisición sintética y línea base. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-01 y DF5-01 aceptada.

## Módulos / responsabilidades
acquisitions, trackings, fixture adapter, audit.

## Persistencia y migraciones
acquisition_runs, observations, observed_actions, baseline/last_adopted en trackings; triggers de sellado; no crear comparaciones aquí.

## Controles de seguridad
Solo actor interno asignado; solicitar fixtures OBS_001/OBS_002/FAILED/INCOMPLETE por enum; origen externo deshabilitado.

## API y contrato
`createAcquisition`, `getAcquisition`, `getObservation`, `adoptObservation`.

| operationId | Método | Ruta |
|---|---|---|
| `createAcquisition` | `POST` | `/api/v1/internal/acquisition-runs` |
| `getAcquisition` | `GET` | `/api/v1/internal/acquisition-runs/{run_id}` |
| `getObservation` | `GET` | `/api/v1/internal/observations/{observation_id}` |
| `adoptObservation` | `POST` | `/api/v1/internal/trackings/{tracking_id}/adoptions` |

## Pruebas requeridas
AT-03/15; DT-07..12; API-N13/N23/N24/N28; TEST-ORD-01/05/06; request_key mismo payload devuelve mismo run.

## Definition of Done verificable
OBS-001 crea baseline A con cero novedad; segunda OBS-002 sellada, failure no comparable; adopción posterior sin evaluación 409.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No tratar FAILED como NO_CHANGES ni adelantar cursor sin evaluación; no implementar scraping real.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
