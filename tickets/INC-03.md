---
ticket: INC-03
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-03 — Comparación determinística, elegibilidad e idempotencia

## Objetivo observable
Comparación determinística, elegibilidad e idempotencia. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-02, DF5-01 y reglas DOM-R08..12 aceptadas.

## Módulos / responsabilidades
comparisons, novelties, trackings.

## Persistencia y migraciones
comparisons, technical_changes, tracking_evaluations, novelties; UNIQUE compuesto, `FOR UPDATE` y rollback de IntegrityError.

## Controles de seguridad
Comparador puro del set ACT-XX; evaluación protegida por asignación a seguimiento; no generar novedades cross-tenant ni retrospectivas.

## API y contrato
`compareObservations`, `getComparison`, `evaluateComparison`; coordinar `adoptObservation` ya diseñado sin ruta nueva.

| operationId | Método | Ruta |
|---|---|---|
| `compareObservations` | `POST` | `/api/v1/internal/comparisons` |
| `getComparison` | `GET` | `/api/v1/internal/comparisons/{comparison_id}` |
| `evaluateComparison` | `POST` | `/api/v1/internal/trackings/{tracking_id}/evaluations` |

## Pruebas requeridas
AT-04/05/06; DT-13..20; API-N14/N15/N34; TEST-ORD-02/03/04, concurrencia dos conexiones; misma respuesta/id si se repite evaluación equivalente.

## Definition of Done verificable
Una diferencia ADDED ACT-06; NOV-A-001 una sola vez; B con OBS-002 como baseline no hereda novedad; cursor no omite cambios.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No implementar diffs de texto libre, eliminación ni identidad judicial real; ACT-XX es solo fixture.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
