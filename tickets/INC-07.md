---
ticket: INC-07
version: 0.1-candidata
status: NOT_STARTED / BLOCKED_UNTIL_ACCEPTANCE
---
# INC-07 — Consolidación, aceptación y presentación técnica

## Objetivo observable
Consolidación, aceptación y presentación técnica. Crear software real **únicamente después de confirmar los prerrequisitos**.

## Dependencias y decisiones
INC-00..INC-06 implementados y reglas aprobadas.

## Módulos / responsabilidades
test harness, ci, docs, fixture reset.

## Persistencia y migraciones
No nuevos endpoints ni tablas por defecto; reset local de DB descartable y snapshots/seed reproducibles.

## Controles de seguridad
Auditar logs sanitizados, no secretos, probar DOS sesiones/roles, permisos cruzados y rutas internas.

## API y contrato
No agregar rutas al OpenAPI; validar las 35 presentes/implementadas y capturar diferencias autorizadas.

| operationId | Método | Ruta |
|---|---|---|
| No añade operaciones | — | — |

## Pruebas requeridas
Ejecutar 18 AT, 36 API-N, 39 DT, 6 TEST-ORD; RNF 1..14; matriz de resultados por commit, migración y entorno.

## Definition of Done verificable
README runnable, guía REST demo, reportes de CI, pruebas reales, reporte fallos/bloqueos, persistencia tras reinicio, reset seguro, entrega para demostración.

- Código en módulos/capas permitidos, sin acceso directo indiscriminado a datos de otro cliente.
- API/DTO versionados y consistentes con YAML canónico o cambio autorizado.
- Tests positivos, negativos y transaccionales ejecutados realmente; comandos, resultados y logs sanitizados registrados.
- Migraciones de este ticket aplicadas sobre PostgreSQL de prueba, `alembic current` correcto, errores tratados con rollback.
- PR con resumen de archivos/cambios, relación RF/AT/test, estado CI y preguntas pendientes.

## Fuera de alcance
No inventar capturas ni marcar PASA sin ejecución; no ampliar a V1 ni probar con datos reales.

**Entrega prohibida:** NO marcar completado basándose solo en archivos generados; sin evidencia real de tests/DB, estado sigue NOT_VERIFIED.
