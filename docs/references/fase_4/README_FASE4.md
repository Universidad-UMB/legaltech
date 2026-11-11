# Fase 4 — Contratos API y seguridad (backend LegalTech)

**Versión:** 0.1-candidata · **Fecha:** 2026-11-10 · **Estado:** diseño documentado, **NO implementado**.

## Entregables

- `API-001_v0.1.md`: contrato funcional HTTP y reglas de respuesta.
- `contratos/API-001.openapi.yaml`: contrato OpenAPI 3.1.1 candidato (35 operaciones, DTO y respuestas).
- `contratos/API-INVENTARIO-001.csv`: catálogo de operaciones.
- `SEC-001_v0.1.md`: identidad, permisos, seguridad, auditoría y amenazas.
- `NFR-001_v0.1.md`: 14 requisitos no funcionales verificables.
- `DEC-F4-001_v0.1.md`: decisiones propuestas y pendientes.
- `pruebas/TEST-API-001_v0.1.md`: 18 AT + 36 pruebas HTTP adicionales (diseñadas, no ejecutadas).
- `pruebas/API-TRZ-AT-001.csv`: trazabilidad con 18 AT.
- `pruebas/validar_contrato_estatico.py`: verificación estática de contrato, sin servidor.
- `diagramas/SEQ-API-AUTORIZACION.mmd`, `diagramas/SEQ-API-PUBLICACION.mmd`: secuencias.
- `ejemplos/REQUESTS-DEMO-001.http`: llamadas de referencia sin claves reales.
- `GATE-F5-001_v0.1.md`: entrada a planificación y handoff.
- `SHA256SUMS.md`: hashes de archivos incluidos.

## Referencias de diseño

SCOPE-001 (F0), DOMAIN-001 y DOM-ME-001 (F1), ARCH-001/ARCH-INT-001/ADR (F2), DATA-001/DATA-DIC-001/GATE-F4-001 (F3). Todas siguen siendo propuestas sujetas a validación de los autores para demo. No certificar políticas jurídicas V1 con este documento.

## Fases

**Fase 5:** fixtures, pruebas de aceptación ejecutables, tareas agent-friendly, AGENT.md y gates. **Desarrollo:** Docker Compose, PostgreSQL real, migraciones Alembic, servicios FastAPI y pruebas reales. Nada de esto se declara ya ejecutado.

## Referencias técnicas

- OpenAPI 3.1.1: https://spec.openapis.org/oas/v3.1.1.html
- RFC 9457: https://www.rfc-editor.org/rfc/rfc9457.html
- OWASP API Top 10 (2023): https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- OWASP REST Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html
- FastAPI security: https://fastapi.tiangolo.com/tutorial/security/
