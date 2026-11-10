# Paquete Fase 2 — Arquitectura del backend LegalTech (v0.1 candidata)

**Fecha:** 2026-11-10  
**Uso:** discusión técnica y transferencia a Fase 3; **no** prueba de código implementado o seguridad productiva.  
**Estado de aceptación:** pendiente de autores (ver `DEC-F2-001_v0.1.md`).

## 1. Dependencias de entrada

- Fase 0: `SCOPE-001_v0.1.md`, `DEC-F0-001_v0.1.md`, `TRZ-F0-001_v0.1.csv`, `BACKLOG-F0-001_v0.1.md`.
- Fase 1: `DOMAIN-001_v0.1.md`, `DOM-ME-001_v0.1.md`, `DOM-TRZ-001_v0.1.csv`, `DEC-F1-001_v0.1.md`.
- Fuentes originales en el paquete de handoff: `RF-CAT-001 v0.8`, `RF-DEC-001 v0.4`, `PROTO-001 v0.1`, TO-BE y BPMN.

Este ZIP de Fase 2 no altera ni sustituye los paquetes previos.

## 2. Inventario

| Ruta | Propósito |
|---|---|
| `ARCH-001_v0.1.md` | Arquitectura de referencia, tecnologías, componentes, reglas, seguridad, transacciones, despliegue |
| `ARCH-INT-001_v0.1.md` | Contratos internos lógicos, flujos y matriz de acceso mínima |
| `DEC-F2-001_v0.1.md` | 18 decisiones, pendientes y registro de aceptación sin completar |
| `ADR/ADR-001...008.md` | Ocho registros motivados de decisiones arquitectónicas (todos **propuestos**) |
| `ARCH-TRZ-001_v0.1.csv` | Los 18 PROTO-AT mapeados a módulos, ADR, regla y evidencia futura |
| `diagramas/C4-L1-CONTEXTO.mmd` | Contexto de sistema (estilo C4 L1) |
| `diagramas/C4-L2-CONTENEDORES.mmd` | API + PostgreSQL como contenedores C4 L2 |
| `diagramas/C4-L3-BACKEND.mmd` | Componentes internos de la aplicación C4 L3 |
| `diagramas/SEQ-001-PUBLICACION-SEGURA.mmd` | Secuencia de preparación, aprobación y lectura externa |
| `diagramas/SEQ-002-COMPARACION-Y-ELEGIBILIDAD.mmd` | Secuencia OBS-001/002, ACT-06, baseline A/B |
| `GATE-F3-001_v0.1.md` | Preguntas y criterios de diseño de persistencia para la Fase 3 |
| `referencias/FUENTES_TECNICAS.md` | Enlaces técnicos oficiales consultados y uso previsto |
| `SHA256SUMS.md` | Huellas SHA-256 de los archivos entregables excluyéndose a sí mismo |

## 3. Decisiones principales, sin fingir aprobación

- Arquitectura **propuesta**: monolito modular FastAPI en Python con PostgreSQL.
- SQLAlchemy 2 síncrono y migraciones Alembic; una sesión por caso de uso, transacciones por mutación.
- Autenticación local con cuentas ficticias y sesiones opacas revocables, autorización por rol y recurso.
- DEMO-FIXTURE, comparación determinista y publicación textual local; nada de fuentes judiciales reales ni LLM.
- Versiones inmutables y selección de vigente en un commit; auditoría coherente.
- Se mantienen `PR-F1` para DEC-08/09, baseline B y políticas sin ratificar; **no se declaran aprobadas**.

## 4. Uso sugerido

1. Revisar `ARCH-001`, diagramas y ocho ADR con los autores.
2. Resolver/aceptar supuestos de `DEC-F2-001`, o mantenerlos marcados para discusión.
3. Usar `GATE-F3-001` al modelar PostgreSQL, verificando cada invariante.
4. En Fase 4 definir API/SEC y en Fase 5 pruebas, fixtures y guías de agente.
5. No encargar implementación autónoma integral todavía.

## 5. Integridad documental

Los diagramas Mermaid son **código fuente editable**; no representan infraestructura desplegada. La matriz CSV está diseñada, no ejecutada. Revisar `SHA256SUMS.md` para comparar huellas. Las pruebas de aplicación se incorporarán cuando exista código.
