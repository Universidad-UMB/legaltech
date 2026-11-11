---
ticket: INC-06
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-06 — Portal y restricciones de acceso externas

## Objetivo observable
Portal y restricciones de acceso externas. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-05, DEC-01/03/04 de demo, SEC-001 aceptados.

## Módulos / responsabilidades
portal, clients, trackings, identity, audit.

## Persistencia y migraciones
Reutilizar clientes/trackings/scopes/session; cambios de estado + auditoría en transacción; evitar nuevas tablas salvo ADR.

## Controles de seguridad
Filtro de cliente desde sesión, scope de tracking, estado client ACTIVE y tracking ACTIVE y versión vigente PUBLISHED; respuesta 404 uniforme por ID ajeno, 200 available=false si autorizado sin publicación.

## API y contrato
`portalTrackings`, `portalCurrentPublication`, `suspendClient`, `reactivateClient`, `finishTracking`.

| operationId | Método | Ruta |
|---|---|---|
| `portalTrackings` | `GET` | `/api/v1/portal/trackings` |
| `portalCurrentPublication` | `GET` | `/api/v1/portal/trackings/{tracking_id}/current-publication` |
| `suspendClient` | `POST` | `/api/v1/internal/clients/{client_id}/suspend` |
| `reactivateClient` | `POST` | `/api/v1/internal/clients/{client_id}/reactivate` |
| `finishTracking` | `POST` | `/api/v1/internal/trackings/{tracking_id}/finish` |

## Pruebas requeridas
AT-12/13/14/17, AT-15 lectura cobertura; DT-21/31..33; API-N08/09/10/27/28/35/36; suspender cliente tras token emitido.

## Definition of Done verificable
B y Alfa sin A2 bloqueados por UUID; suspensión/finalización niegan lecturas desde commit; pub/histórico internos persistentes.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No generar informes PDF ni endpoint de lectura de versiones históricas del portal; finalización no retira publicación DB automáticamente.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
