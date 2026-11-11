# ADR-007 — Auditoría transaccional de éxito y registro aislado de denegaciones

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** DOM-R20/24; D1-13; AT-07/08/12/13/14/18.

## Contexto
Se deben reconstruir decisiones y cambios de estado. Los intentos de acceso indebido no pueden exponer nombres, contenido o IDs de otros clientes, ni perderse accidentalmente por rollback del caso de uso rechazado.

## Decisión candidata
Dos responsabilidades: **eventos de negocio exitosos** persistidos en la misma transacción que la mutación; **eventos de denegación/error de autorización** escritos en una transacción corta separada tras revertir la operación fallida, con acción, identidad de actor, fecha UTC, correlación y motivo de categoría sanitizado. No guardar tokens, contraseñas, cuerpos íntegros ni detalles de recursos ajenos. Un log técnico con `request_id` permite diagnosticar fallos, sin confundirse con evidencia de negocio.

## Alternativas
Guardar todo solo en logs perdería trazabilidad DB; almacenar denegaciones en transacción abortada perdería el evento; integrar broker/event sourcing es innecesario.

## Consecuencias
Política de comportamiento cuando el almacenamiento de denegación falle se define en SEC-NFR-001; **el rechazo HTTP no cambia a permiso** y no se afirma entrega garantizada o no repudio. Reintentos de evento se diseñarán solo si se necesitan y se prueba que no inducen duplicados. Privacidad y retención operativa no están ratificadas.
