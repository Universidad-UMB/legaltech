---
documento: GATE-F3-001
version: 0.1
fecha: 2026-11-10
estado: hoja de transferencia a diseño de persistencia
---

# GATE-F3-001 — Entrada a Fase 3 (diseño de datos)

## 1. Qué ya está modelado (propuesta)

- Proceso judicial compartido y seguimiento aislado por cliente; baseline propio por seguimiento.
- Observaciones técnicas y cambios deterministas compartibles **solo internamente**, novedades/publicaciones siempre privadas.
- `personaId` para separar preparador/aprobador; cuenta externa tiene un cliente y ámbito expreso.
- Un UoW por mutación y una DB PostgreSQL; publicar = versión publicada + puntero vigente en un commit.
- Registro de denegaciones fuera de la transacción abortada, sanitizado; datos 100 % sintéticos.

## 2. Decisiones que DATA-001 debe cerrar (no delegar al agente)

| P3-ID | Pregunta obligatoria | Regla de salida de DATA-001 | Referencias |
|---|---|---|---|
| P3-01 | ¿PK físicas y radicado? | Distinguir `procesoId` interno y radicado válido, criterio de unicidad explícito | DOM-R01/24; AT-01 |
| P3-02 | ¿Cómo asegurar pertenencia de todo seguimiento? | FK cliente/proceso, relaciones contextuales, no asociación cruzada | DOM-R01/02; AT-02/12/17 |
| P3-03 | ¿Cómo persistir persona, cuenta, ámbito y token opaco? | Integridad de persona, cuenta externa único cliente, scope y sesión revocable | ADR-004; AT-10/12/17 |
| P3-04 | ¿Cómo preservar adquisición, intento, observación, actuación, cobertura? | Snapshot/procedencia/inmutabilidad lógica, estados Fallido/Incompleto y timestamps UTC | DOM-R07/24; AT-03/15 |
| P3-05 | ¿Cómo representar baseline por seguimiento sin retroceder? | FK a observación comparable, condición de primera adopción y concurrencia | DOM-R06; AT-03 |
| P3-06 | ¿Cómo evitar cambio duplicado? | UNIQUE explícito par/versión regla/ACT/tipo; no suponer dedup interpares universal | DOM-R08..10; AT-04/05 |
| P3-07 | ¿Cómo evitar novedad duplicada? | UNIQUE `(seguimiento_id, cambio_id)` + concurrente recuperable | DOM-R11/12; AT-06 |
| P3-08 | ¿Cómo versionar publicación y congelar autores? | Snapshot, `personaId` preparadores, aprobador, estado y versionado | DOM-R15/16; AT-09/10/18 |
| P3-09 | ¿Cómo publicar sin parcialidad? | Transacción/versionamiento y FK/constraint del puntero vigente | DOM-R17/18/19; AT-11 |
| P3-10 | ¿Cómo persistir cambios de estado y auditoría? | Historial, proveniencia, UTC, request_id; éxito mismo commit, denegación separado | DOM-R20/24; AT-07/08/13/14 |
| P3-11 | ¿Cómo evitar riesgos cross-tenant en consultas? | Índices compuestos/joins acotados y pruebas de constraints; documentar elección de RLS | ADR-004; AT-12/17 |
| P3-12 | ¿Cómo evolucionar schema? | Alembic ordenado, naming de constraints, seeds distintos a migraciones, rollback estrategia | ADR-003/008; AT-16 |

## 3. Restricciones de diseño lógico

- Preferir claves internas no inferibles para recursos privados; **no usar secreto del identificador como autorización**.
- FK/UNIQUE/check/índices deben ser explícitos, y las reglas de estado que no expresen bien en SQL permanecen en dominio/transacción con pruebas.
- No guardar todas las entidades en un JSON de una sola tabla. JSONB solo para metadata de fuente sin alterar invariantes esenciales.
- No modelar datos judiciales reales ni evidencia de fuente autorizada cuando solo existe DEMO-FIXTURE.
- Separar tablas de relación cuenta-seguimiento/permisos de la propiedad de proceso compartido.
- Probar esquema y concurrencia con PostgreSQL real, no únicamente SQLite o mocks.
- Guardar `observed_at` y `received_at` por separado y usar UTC con zona.
- No incorporar soft-delete generalizado ni historificación/event sourcing completo sin requisito.

## 4. Artefactos de salida de Fase 3

- `DATA-001.md`: conceptual → lógico, diccionario de tablas y columnas, tipos, nulabilidad, constraints y supuestos.
- `DATA-ER-001.mmd`: ER editables, PK/FK y cardinalidades.
- `DATA-DDL-001.sql` **solo cuando el esquema esté aceptado** o migraciones Alembic iniciales propuestas, claramente no ejecutadas.
- `DATA-TEST-001.md`: fixtures de integridad, tenant, concurrencia, rollback y secuencias de migración.
- `DEC-F3-001.md`: decisiones de ambigüedad, riesgos y aprobación.

**Puerta:** Fase 3 puede comenzar con Fase 2 candidata; el agente no implementa migraciones definitivas hasta que los autores acepten las políticas y el modelo correspondiente.
