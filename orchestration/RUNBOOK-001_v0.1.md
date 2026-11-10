# RUNBOOK-001 — Arranque local en Windows + WSL2 o Linux

1. Extraer ZIP en una carpeta nueva (sin documentos, claves ni bases de datos reales). Usar Linux/WSL2 con Python 3.11+, Git, Docker/Podman compatible con Compose, `uv` y Codex CLI instalados. No ejecutar en la máquina corporativa sin permiso de TI.
2. Inicializar repositorio de Git con identidad configurada y crear una rama de trabajo: `git init -b work/legaltech-backend` y `git add . && git commit -m "docs: handoff F6"`. No guardar `.env` ni archivos de estado; `.gitignore` está preparado.
3. Revisar y aceptar **personalmente** el documento `governance/APROBACION-DEMO-001.json` (sustituir PENDIENTE por ACEPTAR en seis decisiones y aceptación técnica; identificar autores y evidencia). No usar el agente para editar aprobaciones. Esta aceptación solo cubre el prototipo, no decisiones institucionales.
4. Verificar sesión del CLI: `codex login` (según método de autenticación disponible). `python3 orchestration/autopilot.py doctor` comprueba dependencias y gate sin ejecutar código.
5. Iniciar `python3 orchestration/autopilot.py run`. Ejecutar `python3 orchestration/autopilot.py status` desde otro terminal para observar el estado. El comando bloquea el terminal mientras continúa el trabajo; no cierra automáticamente la ejecución tras cada ticket.
6. Si hay interrupción, repetir `python3 orchestration/autopilot.py run`. Recupera el primer ticket no completado; no vuelve a validar como DONE un ticket sin evidencias.
7. No utilizar `sudo` para el agente, no darle acceso a bases productivas y no usar el modo sin sandbox de Codex.

## Opcional: nodeterm
Abrir la carpeta del proyecto desde nodeterm. Crear un nodo Terminal para el orquestador, un segundo nodo para `status`/logs y un nodo de editor/diffs. No lanzar un segundo Codex implementador sobre la misma rama: el orquestador ya lanza el CLI. Para varios agentes simultáneos, preparar `git worktree` separados y contratos de integración, por lo que no es la opción inicial recomendada.

**Advertencia Windows:** según la documentación oficial, nodeterm para Windows está en beta y la continuidad entre reinicios aún está en desarrollo. Preferir el orquestador ejecutado en WSL2; que nodeterm se cierre no significa que la ejecución pueda sobrevivir automáticamente a apagados o reinicios de Windows.

## Operaciones de diagnóstico
- `python3 orchestration/autopilot.py doctor`
- `python3 orchestration/autopilot.py status`
- `python3 -m unittest discover -s orchestration/tests -v`
- `python3 scripts/validate_handoff.py`
- `python3 orchestration/autopilot.py run --dry-run` (no llama al agente)

## Límite operativo
El supervisor no evita límites de cuota de la CLI, red sin Docker, cierres de sesión o reinicios. Al encontrar uno, deja estado `BLOCKED` con logs en lugar de afirmar éxito. El operador puede resolver el entorno y relanzar sin perder el progreso documentado.
