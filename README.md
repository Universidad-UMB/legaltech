# LegalTech — Handoff de implementación backend (Fase 5, v0.1)

**Fecha:** 2026-11-10. **Estado:** PAQUETE DE DISEÑO CANDIDATO; ninguna aplicación, base de datos ni migración ha sido ejecutada en esta fase. **Datos exclusivamente sintéticos.**

## Propósito
Este repositorio empaquetado contiene todo lo necesario para revisar el primer incremento backend y encomendar a un agente la implementación **por tickets**, sujeto a aceptación de las decisiones bloqueantes. No es una entrega de código funcional, no contiene credenciales y no constituye aprobación jurídica u organizacional de la V1.

## Lectura obligatoria, en orden
1. `docs/GATE-DEV-001_v0.1.md` y `docs/DEC-F5-001_v0.1.md` (bloqueos y aprobación por autores).
2. `AGENT.md` (protocolo del agente; no empezar a implementar decisiones pendientes).
3. `docs/PLAN-DEV-001_v0.1.md` y `tickets/INC-00.md` ... `INC-07.md`.
4. `docs/TEST-001_v0.1.md` y `docs/PROTO-DAT-001_v0.1.md`.
5. Diseños fuente en `referencias/fase_0..fase_4`, contrato estructurado en `contratos/API-001.openapi.yaml` y análisis de origen en `referencias/analisis_original`.

## Orden de autoridad y gestión de conflictos
- Alcance aprobado del incremento y decisiones aprobadas por autores (en acta) > `AGENT.md` y tickets > OpenAPI (rutas/esquemas) + SEC (permisos) + DOMAIN (reglas) + DATA (invariantes) > fuentes de trabajo anteriores.
- **No** ignorar conflictos entre fuentes; abrir issue con evidencia y propuesta de diff, sin inventar política.
- `DEC-F5-001` ofrece decisiones **recomendadas** y NO las marca como aprobadas; una continuación conversacional sin elección explícita no equivale a aprobación de políticas de V1.
- Los ocho ADR previos están en `referencias/fase_2/ADR/`; la aprobación de autores se registra por separado.

## Contenido
- `AGENT.md`: instrucciones obligatorias al agente.
- `docs/`: estrategia de pruebas, plan, fixtures, conciliación de especificaciones, decisiones y puerta de inicio.
- `tickets/`: ocho incrementos implementables con alcance/entrega/pruebas.
- `fixtures/`: contrato de datos sintéticos, observaciones de cinco/seis actuaciones, casos fallido e incompleto y expectativas.
- `pruebas/`: manifiestos de 18 AT, 36 negativos HTTP y 39 persistencia. **Son especificaciones, no tests ejecutables.**
- `trazabilidad/`: operaciones → tickets y AT → RF/reglas/pruebas planeadas.
- `contratos/`: copia canónica del OpenAPI candidato v0.1.
- `referencias/`: originales sin modificar de fases 0–4 y paquete de análisis previo.
- `scripts/validate_handoff.py`: control estático del paquete, sin conexión a DB ni servicios externos.

## Inicio recomendado
1. Autores revisan y firman localmente las decisiones de `docs/GATE-DEV-001_v0.1.md` antes de construir comportamiento afectado.
2. Crear repositorio Git; conservar artefactos y abrir tickets por incremento. Las fuentes quedan inmutables/versionadas por commit.
3. El agente ejecuta **únicamente** INC-00 con el stack acordado; tras comprobar migraciones en PostgreSQL desechable, avanzar sucesivamente.
4. Ningún reporte de pruebas puede marcar `PASA` antes de ejecución real. Evidencias por commit, migración y entorno.

## No incluido deliberadamente
Backend Python, Compose ejecutable, Dockerfile, modelos ORM, migraciones Alembic, cuentas/contraseñas operativas ni pruebas ya automatizadas. Son precisamente las tareas del agente en desarrollo.
