# Fase 6 — Autonomía controlada del agente backend

**Estado:** ORQUESTADOR PREPARADO; NO SE HA EJECUTADO CODEx, FASTAPI, POSTGRESQL NI ALEMBIC. El gate de decisiones de autores sigue PENDIENTE.

## Qué contiene este ZIP

Este paquete es autocontenido: integra todos los 101 archivos de Fase 5, mantiene el análisis y los contratos originales, y añade la capa de orquestación, instrucciones compatibles con agentes, aprobación única inicial, runbook y pruebas del runner.

### Archivos nuevos relevantes
- `AGENTS.md`: instrucciones de Codex y política de autonomía (complementan `AGENT.md`).
- `governance/APROBACION-DEMO-001.json`: puerta de aceptación expresa, **PENDIENTE por defecto**.
- `orchestration/autopilot.py`: orquestador CLI `doctor`, `status`, `run`, `run --dry-run`.
- `orchestration/check_runtime_openapi.py`: compara el contrato HTTP esperado por incremento con FastAPI `app.openapi()`.
- `orchestration/EXEC-001_v0.1.md`: arquitectura, fallos, reintentos y criterio de finalización.
- `orchestration/RUNBOOK-001_v0.1.md`: preparación de entorno Windows + WSL2, ejecución y reanudación.
- `orchestration/PROMPT-ORQ-001_v0.1.md`: guía de implementación autónoma.
- `orchestration/tests/test_autopilot.py`: pruebas unitarias del runner.

## Comandos

Antes de cualquier implementación, los autores deben revisar y aceptar explícitamente las decisiones DF5-01..DF5-06 y el diseño de demo en `governance/APROBACION-DEMO-001.json`, con nombre, fecha y evidencia. Esta aprobación no ratifica decisiones institucionales de V1.

```bash
# 1. En carpeta nueva, con Git/Codex/uv/Docker ya instalados
python3 -m unittest discover -s orchestration/tests -v
python3 scripts/validate_handoff.py
python3 orchestration/autopilot.py run --dry-run

# 2. Solo después de configurar Git y la aceptación humana
python3 orchestration/autopilot.py doctor
python3 orchestration/autopilot.py run

# 3. Consultar avance o reanudar
python3 orchestration/autopilot.py status
python3 orchestration/autopilot.py run
```

Se verificaron localmente 10 pruebas del orquestador y la coherencia del handoff. `run --dry-run` no ejecuta el backend ni llama a la CLI Codex. El estado de los incrementos permanece PENDING.

## Qué significa «no detenerse hasta terminar»

Dentro de un ambiente autorizado y disponible, el orquestador ejecuta los tickets en secuencia sin pedir confirmación entre ellos. Si falla una validación, reintenta hasta 3 veces por ejecución y conserva logs. Cuando se agota el límite, aparece una decisión de negocio nueva, falla el entorno o se modifica el gate, detiene con estado BLOCKED para no simular éxito. El proceso no persiste por sí mismo tras reinicios del host y no puede sortear límites de sesión o proveedor.

## Límites de seguridad

Sandbox `workspace-write` para el implementador; sin `--yolo`, sin push/merge automáticos, sin instalaciones administrativas, sin fuentes judiciales reales. Se necesita DB de demo aislada. La revisión final humana es necesaria antes de integrar en `main`.
