# ADR-008 — Ejecución local reproducible y pruebas por capas

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** AT-01..18; INC-00/07; DOM-R21; calidad/mantenibilidad.

## Contexto
El agente desarrollará incrementalmente. No puede asumirse que la aplicación existe o se probó solo por entregar documentos y código. El mismo escenario debe funcionar después de levantar una DB limpia.

## Decisión candidata
Docker Compose `api`+`db` con DB healthcheck y volumen persistente; Alembic migraciones explícitas; `seed_demo` idempotente y limitado a `local/test`; configuración `.env.example` sin secretos; dependencias fijadas; tests unitarios en memoria y tests integración/API/aceptación en PostgreSQL descartable, no SQLite como sustituto. Ruff, un solo typechecker elegido en INC-00, Pytest y verificación de importaciones. CI ejecuta quality gates y reporta resultado.

## Alternativas
Servidor DB manual es menos reproducible; servicios adicionales sin caso de uso elevan carga; API con `create_all()` en arranque oculta la disciplina de migraciones.

## Consecuencias
CI no es evidencia hasta que se implemente y ejecute. La salud de `db` se usa para la dependencia de arranque (`service_healthy`) y `readiness` prueba conexión antes de servir operaciones. Reinicio de contenedor no borra datos; reseteo solo explícito y local. Todas las versiones concretas se fijan al crear el repositorio; Fase 2 no inventa una combinación comprobada de dependencias.

Fuentes: https://docs.docker.com/reference/compose-file/services/ ; https://fastapi.tiangolo.com/tutorial/bigger-applications/
