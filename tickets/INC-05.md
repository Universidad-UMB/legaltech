---
ticket: INC-05
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-05 — Publicación versionada y atómica

## Objetivo observable
Publicación versionada y atómica. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-04, DF5-03/04 aceptadas; contract DATA migrado a DB.

## Módulos / responsabilidades
publications, portal read model, audit.

## Persistencia y migraciones
publications, publication_versions, publication_preparers, publication_version_novelties, publication_approvals, state_transitions; triggers de congelación, FKs de seguimiento, puntero version actual.

## Controles de seguridad
Solo PREPARER asignado prepara; COORDINATOR asignado y persona diferente de todas las preparadoras aprueba; `person_id` desde sesión; datos de B no vinculables a A.

## API y contrato
`createPublication`, `getPublication`, `createPublicationVersion`, `getPublicationVersion`, `submitPublicationVersion`, `decidePublicationVersion`, `publishPublicationVersion`.

| operationId | Método | Ruta |
|---|---|---|
| `createPublication` | `POST` | `/api/v1/internal/publications` |
| `getPublication` | `GET` | `/api/v1/internal/publications/{publication_id}` |
| `createPublicationVersion` | `POST` | `/api/v1/internal/publications/{publication_id}/versions` |
| `getPublicationVersion` | `GET` | `/api/v1/internal/publication-versions/{version_id}` |
| `submitPublicationVersion` | `POST` | `/api/v1/internal/publication-versions/{version_id}/submit` |
| `decidePublicationVersion` | `POST` | `/api/v1/internal/publication-versions/{version_id}/decision` |
| `publishPublicationVersion` | `POST` | `/api/v1/internal/publication-versions/{version_id}/publish` |

## Pruebas requeridas
AT-09/10/11/18; DT-23..30, DT-37; API-N18..22/N33; rollback inyectado antes de commit, token B sin acceso, hash inmutable.

## Definition of Done verificable
v1 visible para A sólo después de publicar; intento misma persona rechazo; versión v2 no hereda autorización de v1; rollback deja APPROVED anterior.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No PDF ni entrega por email; publicar significa versión PUBLISHED seleccionada en DB bajo commit único.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
