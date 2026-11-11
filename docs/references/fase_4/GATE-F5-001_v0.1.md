---
documento: GATE-F5-001
version: 0.1
fecha: 2026-11-10
---
# GATE-F5-001 — Entrada a planificación, pruebas e instrucciones del agente

## Lo que entrega Fase 4

- Especificación OpenAPI 3.1.1 candidata (`API-001.openapi.yaml`) y catálogo de 35 operaciones.
- Reglas HTTP, errores y flujos escritos (`API-001`).
- Matriz de rol + ámbito + estado y política de sesión (`SEC-001`).
- Requisitos no funcionales y aceptación verificable (`NFR-001`).
- 18 escenarios AT vinculados a operaciones; pruebas de seguridad/integración planificadas (`TEST-API-001`).
- Registro de decisiones abiertas (`DEC-F4-001`).

## Fase 5 debe producir

1. Fixtures y cuentas demo por identidades/personas, asignaciones internas y scopes; secretos no embebidos en Git.
2. Pruebas Given/When/Then ejecutables: 18 AT, DT-01..39 y negativas HTTP; plan de entorno y pipelines CI.
3. Plan de increments con tickets autocontenidos, archivos previstos, dependencias, API/DB, riesgos y Definition of Done.
4. AGENT.md listo para instrucciones al agente; rutas, reglas, prioridades, prohibiciones, documentación de cambios y comandos verificables.
5. Verificar contradicciones entre DDL candidato, dominio, API y escenarios; no generar código con políticas ambiguas.

## Puerta antes de iniciar construcción con agente

- Decisiones D-F4-12/13 resueltas y aprobación **de prototipo** de las salvaguardas DEC-08/09.
- Especificaciones SCOPE, DOMAIN, ARCH, DATA, API y SEC marcadas por autores como implementables.
- Fixtures deterministas y 18 AT trazados a pruebas e instrucciones de ejecución.
- DDL/Alembic, PostgreSQL y pruebas reales **se ejecutan en desarrollo**, no ahora. No certificar como probados los documentos de diseño.
