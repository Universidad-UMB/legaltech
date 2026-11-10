# AGENT.md — Contrato de trabajo del agente backend LegalTech

## Identidad de la tarea
Actúas como ingeniero backend implementador. Construye **un prototipo funcional con datos 100% sintéticos**, por los tickets INC-00 a INC-07, para una plataforma de vigilancia de procesos judiciales. La documentación del handoff es una especificación candidata: **ninguna política aún PENDIENTE es autorización de implementación**.

## Antes de tocar código
1. Leer `README.md`, `docs/GATE-DEV-001_v0.1.md`, `docs/DEC-F5-001_v0.1.md`, el ticket correspondiente, `docs/TEST-001_v0.1.md`, `contratos/API-001.openapi.yaml` y fuentes de referencia aplicables.
2. Confirmar qué decisiones están **expresamente aceptadas** por los autores en una evidencia versionada. Si un ticket depende de decisión PENDIENTE, no inventarla: registrar bloqueo/pregunta y seguir solo con tareas no afectadas autorizadas.
3. Explicar plan breve de cambios, riesgos, comandos y tests del ticket. **Nunca** ejecutar todos los incrementos como cambio único.

## Stack y arquitectura obligatorios tras aceptación
- Python, FastAPI, Pydantic v2, PostgreSQL, SQLAlchemy 2 síncrono, psycopg 3, Alembic, Pytest y Docker Compose. Asegurar reproducibilidad con `pyproject.toml` y lock; usar Ruff y verificador de tipos.
- Un **monolito modular** con responsabilidades separadas por feature. Dominio **no** importa FastAPI/SQLAlchemy. Controladores solo validan y adaptan; servicios de aplicación aplican casos de uso y delimitan UoW/transacción; infraestructura implementa repositorios.
- No Kafka, microservicios, Kubernetes, Redis/Celery, RLS o proxies distribuidos sin necesidad y decisión documentada.
- Mantenimiento en inglés de nombres de rutas/código alineado con OpenAPI; documentación y justificaciones pueden estar en español.

## Contratos y seguridad no negociables
- Fuente HTTP: `contratos/API-001.openapi.yaml` (35 operationId). No añadir endpoints, modificar semántica/códigos, exponer SQL models en JSON ni permitir admin universal sin change request aprobado.
- Login y health únicos públicos; restante bearer opaco revocable con expiración, digest de token en DB y Argon2id para contraseñas cuando DF5-06 esté aceptada. Prohibido almacenar passwords en claro, tokens o datos personales/judiciales reales en Git/logs.
- Autorizar por rol, asignación, cliente, seguimiento, estado y persona. `client_id` en query/body **no** es identidad confiable; una cuenta externa solo obtiene su cliente desde sesión y scopes explícitos.
- 403 ante rol no habilitado, 404 genérico para recursos ajenos/inaccesibles por tenant/suspensión/finalización, 200 `available=false` solo si lectura autorizada sin versión vigente. RFC 9457 problem+json (incluido 422), sanitización de errores y X-Request-ID.
- Publicación: versión inmutable, revisión jurídica humana del prototipo, aprobador distinto por `person_id` tras aceptación DF5-03/04; publicación y puntero vigente en **único commit**, reintentos/fallos sin lectura parcial.
- Acquisitions son exclusivamente `DEMO-FIXTURE`. FAILED/INCOMPLETE no implican NO_CHANGES. Separar observación compartida vs novedad/publicación privada por seguimiento; no crear novedades históricas al fijar primera baseline.
- Garantizar idempotencia vía UNIQUE + UoW/rollback y bloqueo por fila donde haga falta. No decidir reglas de orden temporal por intuición; seguir DF5-01 solo cuando esté aceptada.

## Persistencia / migraciones
- `referencias/fase_3/ddl/DATA-DDL-001_CANDIDATO.sql` es **borrador técnico, no schema ya probado**. Traducir a migraciones Alembic versionadas; verificar constraints, FKs compuestas, triggers, reversibilidad segura en DB descartable, rollback de carrera.
- Crear y utilizar BD PostgreSQL desechable en desarrollo; usuario runtime con privilegios mínimos. Nunca realizar reset o `docker compose down -v` de una DB no verificada como demo descartable.
- Fixtures de `fixtures/` son un contrato reproducible; el seed no debe incluir claves operativas en archivos. UUIDv5 es únicamente para **identificadores de fixture**, no política general de generación de IDs.

## Flujo por ticket
1. Seleccionar **un** ticket de `tickets/INC-NN.md` y no tocar otros módulos sin justificación.
2. Crear/ajustar pruebas primero o junto al cambio; para seguridad, DB real y carreras, usar transacciones y conexiones independientes cuando corresponda.
3. Implementar caso de uso, permisos, validaciones, auditoría, DTO, persistencia y migración de ese ticket; no declarar DONE hasta pasar gate.
4. Ejecutar formatter/linter, tipos, tests unitarios/integración/API/AT aplicables. Registrar comandos y resultado real; no simular salidas ni evidencias.
5. Comparar API runtime `/openapi.json` con archivo aprobado y documentar diferencias; versionar cualquier cambio autorizable como ADR/PR.
6. Entregar en PR: diff, matriz RF→AT→test, migración, comandos, resultados PASS/FAIL/BLOCKED, restricciones conocidas y siguiente ticket. Esperar revisión humana antes de merge de política crítica.

## Comandos esperados después de crear la implementación
Los comandos son **objetivos de aceptación**, no instrucciones ejecutadas en este handoff. Ajustar a gestor de dependencias escogido en INC-00 y documentar equivalente:
```bash
docker compose up -d db
# Instalar dependencias desde lock del repositorio implementado
alembic upgrade head
python scripts/seed_demo.py        # archivo futuro: solo DB descartable
ruff check .
python -m mypy app
pytest -q
```
La suite debe incluir 18 AT, 36 negativos HTTP, 39 escenarios de datos pertinentes, TEST-ORD, y RNF. Recomendable ejecutar tests de PostgreSQL con DB/usuario de test independientes y reset explícito.

## Prohibiciones explícitas
- No integrar CPNU, SAMAI, Publicaciones Procesales, proveedores LLM, OCR propio, PDFs, envío de correos ni workflows programados en este incremento.
- No afirmar que la demo realiza consulta judicial real, revisión jurídica automatizada, cumplimiento ISO/OWASP, SLA de producción o que las pruebas pasan sin ejecutarlas.
- No modificar o borrar evidencias históricas ni crear endpoint de reset público.
- No ocultar casos fallidos/pendientes; no rellenar firmas de aceptación, ni elevar decisiones de prototipo a políticas V1.

## Handoff final por incremento
Registro por commit con: `ticket_id`, `commit`, `head alembic`, cambios OpenAPI/DB, tests ejecutados y resultados, fallas conocidas, capturas/logs sanitizados, decisiones/ADR cambiados y próximos riesgos. Si faltan aprobaciones, estado `BLOCKED`, no `DONE`.
