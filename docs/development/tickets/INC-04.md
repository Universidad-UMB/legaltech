---
ticket: INC-04
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-04 — Gestión humana de novedades

## Objetivo observable
Gestión humana de novedades. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-03 y DF5-03 aceptada como salvaguarda de demo.

## Módulos / responsabilidades
novelties, legal review, audit.

## Persistencia y migraciones
novelty_reviews, state_transitions, audit_events; historial consistente bajo UoW.

## Controles de seguridad
Solo ANALYST asignado inicia/escala revisión; solo LAWYER asignado registra valoración; registrar person_id/actor desde sesión.

## API y contrato
`listNovelties`, `getNovelty`, `startOperativeReview`, `escalateNovelty`, `recordLegalReview`.

| operationId | Método | Ruta |
|---|---|---|
| `listNovelties` | `GET` | `/api/v1/internal/trackings/{tracking_id}/novelties` |
| `getNovelty` | `GET` | `/api/v1/internal/novelties/{novelty_id}` |
| `startOperativeReview` | `POST` | `/api/v1/internal/novelties/{novelty_id}/start-operative-review` |
| `escalateNovelty` | `POST` | `/api/v1/internal/novelties/{novelty_id}/escalate` |
| `recordLegalReview` | `POST` | `/api/v1/internal/novelties/{novelty_id}/legal-review` |

## Pruebas requeridas
AT-07/08; DT-22, DT-36/38/39; API-N16/17; estados ilegales 409; campos extra 422.

## Definition of Done verificable
Analista registra evidencia ficticia y estado; abogado distinto registra valoración humana rastreable; no hay bypass de roles/ámbitos.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No delegar criterio jurídico al LLM ni afirmar dictamen real; no implementar estados avanzados de V1.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
