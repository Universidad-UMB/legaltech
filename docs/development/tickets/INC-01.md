---
ticket: INC-01
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-01 — Clientes, procesos y seguimientos

## Objetivo observable
Clientes, procesos y seguimientos. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-00, DF5-02 (unicidad), DF5-05 (ADMIN) y DATA aceptados.

## Módulos / responsabilidades
clients, trackings, authorization contexts.

## Persistencia y migraciones
clients, judicial_processes, trackings, external_tracking_scopes, internal_tracking_assignments; índice parcial después de aceptación.

## Controles de seguridad
Permiso ADMIN para altas; rol correcto no basta para seguimiento; cuentas externas no tienen API interna; FKs compuestas deben impedir A→B.

## API y contrato
`createClient`, `getClient`, `createProcess`, `getProcess`, `createTracking`, `getTracking`, `activateTracking`.

| operationId | Método | Ruta |
|---|---|---|
| `createClient` | `POST` | `/api/v1/internal/clients` |
| `getClient` | `GET` | `/api/v1/internal/clients/{client_id}` |
| `createProcess` | `POST` | `/api/v1/internal/processes` |
| `getProcess` | `GET` | `/api/v1/internal/processes/{process_id}` |
| `createTracking` | `POST` | `/api/v1/internal/trackings` |
| `getTracking` | `GET` | `/api/v1/internal/trackings/{tracking_id}` |
| `activateTracking` | `POST` | `/api/v1/internal/trackings/{tracking_id}/activate` |

## Pruebas requeridas
AT-01/02; DT-01..07, DT-39; API-N05/N06/N07, validaciones radicado 22/24/caracteres; 409 duplicado.

## Definition of Done verificable
Dos seguimientos para PROC-001 de Alfa/Beta; SEG-A-002 para PROC-002; recursos ajenos inaccesibles y clave de radicado validada.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No implementar asignaciones editables desde API; scopes y asignaciones provienen de seed local.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
