# ADR-001 — Monolito modular en lugar de microservicios

- **Estado:** Propuesto para aprobación de autores (no aprobado)
- **Fecha:** 2026-11-10
- **Impulsores:** SCOPE-001; DOMAIN-001 CTX-ID..CTX-AUD; D1-20; INC-00..07.

## Contexto
El primer incremento debe demostrar una secuencia judicial con seguridad contextual, transacciones y auditoría, con un solo equipo pequeño, un agente implementador y fuentes exclusivamente sintéticas. No existen requisitos medidos de escalado independiente ni disponibilidad multi-región.

## Decisión candidata
Un único proceso de aplicación FastAPI organizado en módulos de negocio y una base PostgreSQL. Entre módulos se prefieren contratos internos de aplicación y llamadas locales. Una única entrega/imagen de backend y migrations versionadas.

## Alternativas evaluadas
- Microservicios: permiten escalado por dominio, pero añaden contratos remotos, despliegue, observabilidad y consistencia distribuida sin beneficio demostrado.
- Monolito sin módulos: rápido al inicio, pero aumenta acoplamiento y errores de privacidad conforme crece la funcionalidad.
- Monolito modular (**selección propuesta**): permite transacciones ACID y límites de dominio verificables con complejidad operativa moderada.

## Consecuencias y pruebas
Módulos no equivalen a microservicios ni a múltiples esquemas físicos. Una base compartida requiere disciplina de ownership y pruebas de importaciones. No se anticipa extracción de servicios. Prueba de decisión: el recorrido completo AT-01..18 funciona en una sola instancia sin cola ni red interna entre módulos.

## Revisar si
Escalado por módulo medido, equipos autónomos, requisitos regulatorios de aislamiento físico o necesidades de disponibilidad lo exigen, con ADR posterior.
