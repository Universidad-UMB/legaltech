# PROMPT-AGENT-001 — Orden inicial reutilizable (NO es aprobación de políticas)

Lee primero `AGENT.md`, `docs/development/plan/GATE-DEV-001_v0.1.md` y `docs/decisions/DEC-F5-001_v0.1.md`. No asumas que las propuestas marcadas PENDIENTE están aceptadas. Revisa el repositorio y confirma qué decisiones del prototipo tienen aceptación explícita versionada.

**Trabajo solicitado, una vez autorizada la preparación técnica:** aborda **exclusivamente INC-00** en `docs/development/tickets/INC-00.md`: inicia el proyecto backend Python/FastAPI, base PostgreSQL desechable mediante Docker Compose, Alembic, estructura modular, entorno/lock de dependencias, controles estáticos y autenticación únicamente si DF5-06 está aceptada.

Antes de generar código entrega un plan breve con estructura de directorios, archivos, migraciones, tests y comandos. Si falta aprobación de decisiones críticas, documenta los bloqueos y limita tu trabajo a scaffolding no afectado, sin inferir reglas. No uses datos reales ni servicios externos.

Al finalizar devuelve: diff/archivos tocados, migraciones, instrucciones para levantar entorno, salida **real** de tests y herramientas, versión Python/PostgreSQL/lock, riesgos y próximos pasos. **No continúes automáticamente a INC-01** sin revisión humana.
