# AGENTS.md — Ejecución autónoma coordinada de LegalTech

Las políticas de negocio y de seguridad del archivo `AGENT.md` siguen vigentes. Este documento agrega el **modo de ejecución continua controlada** para INC-00..INC-07 sin modificar los requisitos ni autorizar decisiones pendientes.

## Regla superior del proyecto
1. Leer `AGENT.md`, el ticket `tickets/INC-NN.md`, contrato OpenAPI y documentos pertinentes antes de cambiar código.
2. La aprobación de autores solo se acredita desde `governance/APROBACION-DEMO-001.json`, gestionada fuera del trabajo del agente. **Prohibido editar ese archivo**, inventar aprobaciones o modificar las políticas para eludir el gate.
3. Trabajar exclusivamente dentro de este repositorio, con fixtures sintéticos, en rama de trabajo. No hacer push, merge a main, desplegar fuera del entorno local, ni ejecutar acciones de alto impacto externo.
4. No hacer preguntas entre tickets al usuario por dificultades ordinarias: leer documentación, explorar código, tomar decisiones técnicas reversibles de bajo impacto, escribir tests, arreglar fallos y continuar. Si aparece una decisión material de negocio o una operación destructiva no autorizada, declarar `BLOCKED` con causa y evidencia.
5. El orquestador, no un comentario de éxito del modelo, decide si un incremento cumple el gate. Nunca actualizar manualmente `.autopilot/state.json` ni falsificar logs/resultados.
6. Los cambios tienen que seguir el OpenAPI canónico, las 18 pruebas de aceptación, 36 negativos HTTP, 39 escenarios de datos y las restricciones de dominio. No se permite degradar tests para conseguir verde.
7. Registrar cambios y pruebas reales por incremento. El orquestador ejecuta automáticamente el siguiente ticket cuando el anterior esté validado; no solicitar aprobación para la siguiente tarea.

## Alcance y exclusiones
Implementar INC-00..INC-07. No conectar fuentes judiciales reales, LLM, OCR, correo, PDF ni servicios productivos. Al completar, dejar README de ejecución, esquema de migración, fixtures, evidencia de pruebas y un resumen final `docs/ENTREGA-FINAL.md`.

## Estructura de entregas
Todo software nuevo dentro de `backend/`. Usar `uv` con `uv.lock`, pytest, Ruff y mypy. En los tests usar PostgreSQL de desarrollo aislado; no tocar bases ajenas. La migración alembic y el levantamiento de PostgreSQL se hacen durante INC-00 y los incrementos posteriores, no durante esta preparación documental.

## Transición entre tickets
El agente implementa solamente el ticket que recibe del orquestador. Si falla calidad: diagnosticar y corregir en el siguiente intento conservando el estado del repositorio. Si pasa: cerrar ticket con evidencias. **No esperar confirmación humana entre incrementos ni hacer merge a ramas protegidas**.

### Aislamiento de infraestructura local

El desarrollo del backend LegalTech debe utilizar servicios Docker independientes de otros proyectos existentes en el equipo.

Reglas obligatorias:

- No detener, eliminar, modificar ni reutilizar contenedores, redes, bases de datos o volúmenes de otros proyectos.
- Utilizar el nombre de proyecto Docker Compose `legaltech-backend`.
- Evitar publicar FastAPI en el puerto 8000 del host. Utilizar 8001 cuando sea necesario.
- Configurar las conexiones, migraciones Alembic y pruebas según el entorno donde se ejecuten.
- Utilizar exclusivamente datos sintéticos de LegalTech.
- No ejecutar operaciones Docker globales de limpieza.
- No modificar archivos de configuración ni recursos pertenecientes a otros proyectos.
- Continuar automáticamente entre incrementos cuando las verificaciones sean satisfactorias.
- No omitir verificaciones para conseguir que un incremento sea marcado como completado.
