# ADR-003 — PostgreSQL y transacciones explícitas por caso de uso

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** DOM-R06..12, DOM-R15..20; D1-03/09/10; AT-05/06/11/18.

## Contexto
Se requieren cambios/novedades idempotentes, referencia basal por seguimiento, versionado y publicación vigente sin estados parciales. Las pruebas deben ejecutar restricciones reales de PostgreSQL.

## Decisión candidata
PostgreSQL única; SQLAlchemy 2 síncrono con psycopg 3; Alembic para migraciones. Endpoints `def` al usar driver síncrono. Una `Session` por operación/request, no compartida. Un `UnitOfWork` controla `begin/commit/rollback` en la capa aplicación; repositorios no hacen `commit`. Acciones exitosas y auditoría asociada se escriben atómicamente. Unicidad DB + operación idempotente bajo concurrencia. DB única evita saga/outbox para publicación **local**, pero no garantiza entregas externas futuras.

## Alternativas
SQLAlchemy asíncrono añade complejidad que la demo no necesita; SQLite no prueba igual las garantías de PostgreSQL; eventos distribuidos requieren compensación innecesaria. Ninguna se selecciona por ahora.

## Consecuencias y pruebas
No guardar transacciones mientras se llama un servicio externo. Evitar abrir `session.begin` si ya existe autobegin activo; sesión administrada por UoW desde inicio. Fase 3 cerrará claves y bloqueos concretos (`UNIQUE`, FK compuestas, `FOR UPDATE`, optimistic locking). Tests contra PostgreSQL incluyen dos entregas concurrentes, fallo en publicación y rollback.

Fuente técnica: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
