# Fase 3 — Diseño de persistencia LegalTech v0.1

**Fecha:** 2026-11-10. **Estado:** paquete documental candidato; esquema PostgreSQL/Alembic NO ejecutado. **Alcance:** prototipo backend, datos sintéticos, no producción.

## Procedencia

Consolida SCOPE-001 (Fase 0), DOMAIN-001 y DOM-ME-001 (Fase 1), ARCH-001, ARCH-INT-001, ADR-003/004/006 y GATE-F3-001 (Fase 2). No cambia los requisitos de V1 y no ratifica DEC-08/09 ni políticas organizacionales.

## Inventario

| Ruta | Propósito |
|---|---|
| `DATA-001_v0.1.md` | Modelo, cardinalidades, controles, concurrencia y trazabilidad |
| `DATA-DIC-001_v0.1.md` | Diccionario de columnas, tipos, claves, condiciones |
| `diagramas/DATA-ER-001-Nucleo.mmd` | Compartido judicial y seguimiento privado |
| `diagramas/DATA-ER-002-Identidad.mmd` | Personas, cuentas, permisos, sesiones |
| `diagramas/DATA-ER-003-Publicaciones.mmd` | Contenedores, versiones, preparadores, aprobaciones |
| `ddl/DATA-DDL-001_CANDIDATO.sql` | Borrador íntegro de 24 tablas, índices, FK, triggers; **NO aplicar** |
| `DATA-MIG-001_v0.1.md` | Plan Alembic y de evolución del schema |
| `pruebas/DATA-TEST-001_v0.1.md` | 39 tests propuestos y matriz de los 18 AT |
| `DEC-F3-001_v0.1.md` | 18 decisiones, hipótesis, bloqueos |
| `GATE-F4-001_v0.1.md` | Entrada y tareas obligatorias de API/seguridad |
| `pruebas/validar_esquema_estatico.py` | Verifica referencias y elementos esenciales sin motor SQL |
| `SHA256SUMS.md` | Integridad de los archivos del paquete |

## Cómo utilizarlo

1. Revisar `DATA-001` junto a `DEC-F3-001` y validar decisiones que cambian esquema.
2. Contrastar el diccionario con los ER y el DDL. El DDL no tiene evidencia de ejecución; adaptarlo a 4 migraciones Alembic solo después de aprobación.
3. Usar `DATA-TEST-001` como contrato de verificación física en PostgreSQL real.
4. Llevar `GATE-F4-001` a diseño de API/seguridad. Los DTO no deben reflejar automáticamente estas tablas; diseñar operaciones de negocio.
5. Los archivos Mermaid son editables y están divididos deliberadamente para que la cardinalidad sea legible; los vínculos exactos se verifican en DDL.

## Limitaciones y advertencias

- No existe validación de SQL sobre una instancia PostgreSQL ni migraciones ejecutadas. Se han realizado **comprobaciones estructurales estáticas** del paquete si figura evidencia en la salida del proceso de validación.
- Los números `ACT-XX` y `SEG-A-001` son **códigos de fixtures**, no IDs físicos persistentes por sí solos; se relacionan con UUID del seed.
- El esquema propuesto solo maneja diferencias de incorporación `ADDED`; alteraciones/retiradas y fuentes reales requieren análisis y migración posterior.
- La restricción propuesta de un seguimiento no finalizado por cliente+proceso (`D-F3-03`) puede cambiar si el negocio confirma necesidad de paralelismo.
- La selección de tecnologías fue aceptada como dirección de trabajo, pero no constituye aprobación de las políticas jurídicas pendientes.
