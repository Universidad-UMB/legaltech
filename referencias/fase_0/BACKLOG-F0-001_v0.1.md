# BACKLOG-F0-001 — Incrementos sugeridos para la implementación por agente

**Versión:** 0.1 · **Fecha:** 2026-11-10 · **Estado:** planificación candidata; NO es orden de codificar aún.

## 1. Reglas para crear tareas de agente

Cada ticket debe indicar objetivo observable; RF y casos de aceptación; entradas y salidas; estados y validaciones; autorización; persistencia y migraciones; pruebas positivas, negativas e idempotencia; evidencia y archivos modificables. El agente **no decide ni aprueba** políticas del dominio. No se acepta «funciona en mi equipo» como evidencia de terminado.

## 2. Orden por dependencias (verticales y verificables)

| Inc. | Objetivo | Entrada necesaria | Entrega concreta | Criterios de aceptación mínimos |
|---|---|---|---|---|
| INC-00 | Entorno + autenticación de prueba + autorizador contextual | DOMAIN, ADR, SEC-NFR y base técnica | API ejecutable con DB, migraciones, semillas de personas/roles/cuentas, políticas de autorización base y bitácora | Credenciales inválidas rechazadas, acceso por recurso sin ámbito denegado |
| INC-01 | Proceso común y seguimientos de dos clientes | Modelo relacional, estados de seguimiento | Alta del radicado, Alfa/Beta y seguimientos independientes con consultas | PROTO-AT-01/02 y aislamiento desde servidor |
| INC-02 | Adquisiciones DEMO-FIXTURE y línea base | Modelo de intento, observación y cobertura | OBS-001 establecida sin novedades, OBS-002 persistida, estado Fallido/Incompleto | PROTO-AT-03/15 |
| INC-03 | Comparador + elegibilidad | Identidad ACT-XX, reglas e idempotencia | ACT-06 única; entrega a A, B no hereda novedades | PROTO-AT-04/05/06 (parte técnica) |
| INC-04 | Ciclo revisión operativa y jurídica | Máquina ME-03 acotada, matriz de permisos | NOV-A-001, revisión, valoración y tratamiento, historial | PROTO-AT-06/07/08 |
| INC-05 | Versiones y aprobación | ME-05 acotada, guardas y identidad persona | Borrador textual v1 inmutable, autorización por tercero, publicación local | PROTO-AT-09/10/11/18 |
| INC-06 | Portal cliente + suspensión/finalización | Autorizador contextual y política de recursos | Lecturas protegidas A/B, suspensión A, finalización SEG-A-001 | PROTO-AT-12/13/14/17 y cobertura AT-15 |
| INC-07 | Validación reproducible | Dataset, pruebas automatizadas, guía de demo | Reinicio local; ejecución/documentación de los 18 AT; reporte de alcance y pendientes | PROTO-AT-01..18, incluido AT-16 |

### Restricción de dependencias

- Las APIs del portal no pueden confiar en filtros de frontend; requieren pruebas de bypass por ID.
- La comparación no debe producir novedades hasta que el seguimiento tenga baseline y elegibilidad válidas.
- La autorización no puede completarse sin verificar versión inmutable y revisor correspondiente.
- `Publicada` solo después de disponibilidad externa local verificable; no enviar mensajes a cliente real.

## 3. Definición de terminado por ticket / entrega del agente

- Código organizado en capas/módulos acordados, sin dependencias circulares evitables.
- Migración y datos fixture reproducibles; bases limpias y seeds idempotentes.
- Tipado, validación, errores estructurados y pruebas acordadas en CI.
- Autorización verificada por servidor para cada endpoint protegido, con pruebas de IDOR/tenencia.
- Operaciones idempotentes según contrato; error no equivale a éxito parcial.
- Pruebas positivas, negativas y persistencia pasan con evidencia y comandos documentados.
- El reporte de resultados diferencia tests automatizados, aceptación manual y políticas no ratificadas.
- No hay secretos en repositorio ni servicios externos que procesen datos reales.

## 4. Entregables faltantes antes de crear tareas implementables

1. `DOMAIN-001`: frontera de dominio, agregados, invariantes, transiciones y tratamiento de fallos.
2. `ARCH-001`/`ADR`: decisión motivada sobre monolito modular, composición y dependencias.
3. `DATA-001`: ER y esquema lógico, índices, claves, multi-tenencia, versiones y auditoría.
4. `API-001`: OpenAPI versionado y matriz RBAC + ámbito + estado por operación.
5. `SEC-NFR-001`: seguridad, privacidad, errores y atributos de calidad medibles.
6. `PROTO-DAT-001`: dataset A, B, SEG-A-002, identidad de personas y variantes fallidas.
7. `TEST-001`: ejecución automatizable de los 18 AT, negativos y pruebas de idempotencia.
8. `AGENT.md`: tarea atómica, repositorio, convenciones, límites, criterios de terminado y prohibiciones.

> No se debe confundir el presente backlog de alto nivel con tickets listos para codificar. La descomposición a historias/tareas pequeñas ocurre tras arquitectura, datos y contratos.
