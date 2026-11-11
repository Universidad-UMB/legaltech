# EXEC-001 — Arquitectura de la ejecución autónoma

## Objetivo
Completar en una ejecución retomable INC-00..INC-07, utilizando Codex CLI en modo no interactivo y comprobaciones ejecutadas por un orquestador externo al agente. El resultado **no está garantizado** ante ausencia de credenciales, límites del proveedor, fallos ambientales, decisiones materiales no aprobadas o errores no recuperables.

## Topología recomendada
- **Orquestador (Python stdlib):** lee gate y tickets, lanza `codex exec`, conserva logs y estado, verifica comandos realmente ejecutados; avanza por INC-00..INC-07.
- **Implementador (Codex CLI):** escribe backend y pruebas dentro del repositorio (sandbox `workspace-write`, sin aprobaciones por comandos; nunca acceso total a la máquina).
- **Verificador (comandos independientes):** validación documental, Docker Compose PostgreSQL local, migraciones Alembic, Ruff, mypy, pytest. Opcional segundo agente crítico en un worktree de solo lectura a partir de INC-03, sin edición simultánea.
- **Supervisión visual opcional:** nodeterm permite disponer terminal de orquestación y otra terminal de logs; **no es el motor de coordinación**.

## Decisiones y seguridad
- La aceptación de DF5-01..06 y del diseño técnico debe ser **una sola actuación explícita antes de `run`**. `APROBACION-DEMO-001.json` se entrega PENDIENTE.
- No modificar `governance/APROBACION-DEMO-001.json` por medio del agente. El orquestador detecta modificación durante ejecución y bloquea.
- Evitar `--dangerously-bypass-approvals-and-sandbox`, auto-push, cambios de producción y eliminación de volúmenes ajenos.
- El orquestador verifica la existencia de los artefactos mínimos y pruebas reales; el resultado del modelo por sí solo no autoriza DONE.
- Los reintentos son limitados (3 por defecto); tras agotarse, detener con `BLOCKED` y evidencia, sin bucles infinitos que consuman créditos.

## Máquina de estado
`PENDING → RUNNING → VERIFYING → DONE` o `BLOCKED`; un relanzamiento recupera el primer ticket que no esté en DONE. `INTERRUPTED` y error de ejecución permanecen como reintentables, nunca como DONE. Todos los logs se almacenan en `.autopilot/logs` localmente.

## Gates por ticket
- INC-00: estructura backend, `uv.lock`, Docker Compose y Alembic; Ruff, mypy, pytest y migración real contra DB de demostración.
- INC-01..06: misma verificación completa tras cada ticket, sin saltar errores para seguir al próximo.
- INC-07: cobertura mediante ejecución real de los 18 AT, 36 API-N y 39 DT: sus identificadores deben estar presentes en `pytest --collect-only -q` y la suite completa debe pasar.
- Handoff final: entrega ejecutable con comandos, evidencia, límites y documentos de operación. No declarar 100% finalizado mientras una puerta esté bloqueada.

## Reglas de revisión
Una revisión humana del resultado final sigue siendo necesaria antes de publicar el código o tratarlo como sistema productivo. El objetivo de la automatización es **eliminar intervenciones entre tickets técnicos**, no sustituir la responsabilidad de los autores por políticas de negocio.
