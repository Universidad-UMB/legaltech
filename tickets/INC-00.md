---
ticket: INC-00
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-00 — Base ejecutable, identidad y calidad

## Objetivo observable
Base ejecutable, identidad y calidad. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
Gate técnico y DF5-06 aceptados para identidad; configuración de repositorio autorizada.

## Módulos / responsabilidades
Identidad, app core, migrations, auth, audit, devops.

## Persistencia y migraciones
persons, accounts, account_roles, auth_sessions, audit_events; crear secuencia Alembic coherente con DATA-MIG-001.

## Controles de seguridad
Asegurar secretos por entorno, Argon2id, token opaco, SHA-256 digest, revocación y TTL; DB runtime con privilegios mínimos.

## API y contrato
`GET /healthz`, `POST /auth/sessions`, `DELETE /auth/sessions/current`, `GET /auth/me`; Swagger solo dev.

| operationId | Método | Ruta |
|---|---|---|
| `healthz` | `GET` | `/healthz` |
| `login` | `POST` | `/api/v1/auth/sessions` |
| `logout` | `DELETE` | `/api/v1/auth/sessions/current` |
| `getPrincipal` | `GET` | `/api/v1/auth/me` |

## Pruebas requeridas
401 inválido/expirado/revocado, 204 logout, logout repetido según contrato; contrato 422 problem+json; DB vacía→head→seed; ruff, tipos y pytest en CI.

## Definition of Done verificable
Compose arranca API+DB efímera; script bootstrap exige secret externo y produce identidades, cuentas y clientes ficticios (sin procesos ni seguimientos); login real con token en tabla; migraciones ejecutables y comprobadas.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No integrar otras features, fuente real ni endpoints de administración de usuarios.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
