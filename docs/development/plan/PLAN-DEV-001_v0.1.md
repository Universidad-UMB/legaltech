---
documento: PLAN-DEV-001
version: 0.1-candidata
fecha: 2026-11-10
estado: plan de desarrollo por agente; pendiente Gate de aceptación
---
# PLAN-DEV-001 — Ejecución incremental del backend por agente

## 1. Enfoque de ciclo de vida
Iteraciones pequeñas y verificables con Git; contratos acordados antes de código; migraciones en desarrollo; pruebas automáticas y revisión humana de decisiones de negocio. No ejecutar el proyecto completo de una sola vez ni utilizar microservicios o abstracciones innecesarias.

## 2. Incrementos y secuencia
| ID | Dependencias | Módulos / entrega vertical | Operaciones OpenAPI | Aceptación |
|---|---|---|---:|---|
| INC-00 | Gate técnico mínimo, ambiente Git limpio | Python/FastAPI, Compose local, config segura, Alembic inicial, usuario DB limitado, login/logout/me/health, CI | 4 | Auth 401, sesiones revocadas, migraciones reproducibles |
| INC-01 | INC-00 y DF5-02/05 | Clientes, procesos, seguimientos, activación; asignaciones demo | 7 | AT-01/02, tenant isolation |
| INC-02 | INC-01 y DF5-01 | Fixture adapter, run/observaciones selladas, baseline, fallos | 4 | AT-03/15, orden de cursor |
| INC-03 | INC-02 | Comparador ADDED, evaluación contextual, deduplicación | 3 | AT-04/05/06, TEST-ORD, DT-20 |
| INC-04 | INC-03 y DF5-03 | Novedades, revisión analista y valoración abogado | 5 | AT-07/08, reglas de actor y evidencia |
| INC-05 | INC-04 y DF5-04 | Versiones, aprobadores por persona, transacción de publicación | 7 | AT-09/10/11/18, atomicidad |
| INC-06 | INC-05 | Portal, suspensión, reactivación y cierre seguimiento | 5 | AT-12/13/14/17 + coverage AT-15 |
| INC-07 | INC-00..06 | Orquestación y reporte E2E; reset seguro local; docs y evidencias | 0 nuevas | 18 AT + 36 API-N + 39 DT + RNF por evidencia |

**Suma única:** 35 `operationId` asignados exactamente una vez; ver `docs/development/traceability/OPERACIONES-INC-001.csv`. Aunque la implementación de tests comienza en INC-00, INC-07 es la consolidación, no una excusa para diferir calidad.

## 3. Contrato de cada ticket
1. Identificador, objetivo observable y componentes permitidos; RF/AT/operaciones.
2. Precondiciones de negocio y decisiones aceptadas; bloqueo si faltan.
3. Cambios previstos en DTO, OpenAPI, migraciones y permisos; todos controlados por versión.
4. Pruebas unitarias, de DB, negativas, carreras y aceptación pertinentes.
5. Evidencia reproducible: comandos, estado de CI, logs sanitizados, commit y cabeza Alembic.
6. Fuera de alcance explícito; PR pequeño revisable; no refactor masivo ajeno.

## 4. Secuencia de un ticket para el agente
- Leer `AGENT.md`, contrato, código vigente, decisión y ticket; presentar breve plan de archivos tocados.
- Confirmar que gate del ticket está aceptado; si no, **detener la lógica bloqueada** y registrar pregunta.
- Agregar primero prueba que describa el caso positivo y su negativo/estado conflictivo.
- Implementar la menor cantidad de código coherente con las capas. Commit de migraciones por función; sin editar datos históricos arbitrariamente.
- Ejecutar pruebas locales y comandos de calidad; capturar resultado **real**. Revisar cambios OpenAPI y reglas de tenencia.
- Actualizar README, trazabilidad y registro de decisiones; PR para revisión humana; no fusionar unilateralmente por supuesta aprobación.

## 5. Estructura deseada al crear el repositorio Python
```text
backend/
  pyproject.toml
  uv.lock                      # si se adopta uv en INC-00
  app/
    main.py
    core/                      # configuración, exceptions, unidad de trabajo y auth transversal
    modules/
      identity/                # api / application / domain / infrastructure
      clients/
      trackings/
      acquisitions/
      comparisons/
      novelties/
      publications/
      portal/
      audit/
    infrastructure/            # session factory, adapters mínimos, no dominio
  alembic/
  tests/
    unit/
    integration/
    api/
    acceptance/
  scripts/                     # seeds/reset local; no endpoints de reset
  Dockerfile
  compose.yaml
  .env.example
  README.md
```
La estructura se ajustará al ADR aceptado. No crear 4 capas de carpetas vacías si no aportan separación real.

## 6. Métricas de seguimiento y evidencias
| Métrica | Cómo calcular | Criterio |
|---|---|---|
| RF/AT vinculados | `docs/development/traceability/AT-RF-TEST-001.csv` + tests | 18/18 AT con pruebas y resultados en entrega |
| Operaciones HTTP | Archivo canónico vs app en ejecución | 35/35 operaciones cubiertas o diferencias versionadas/aceptadas |
| Negativos seguridad | `API-NEG-001.csv` + pytest | 36 escenarios evaluados; fallos críticos bloquean |
| Integridad/concurrencia | `DATA-TEST-001.csv` + pytest | 39 escenarios evaluados, prioridad P0 bloqueante |
| Migraciones | DB vacía → head → seed → tests; upgrades repetidos | Pasa en PostgreSQL efímero; rollback probado donde proceda |
| Calidad | ruff, tipos, pruebas, secretos | Todo en CI; sin hardcoded secrets |

## 7. Exclusiones
Fuentes judiciales reales, análisis LLM, OCR independiente, documentos PDF, notificaciones externas, multiempresa productiva, HA y cargas masivas. Contratos futuros podrían incorporarse por nuevas decisiones, **no en estos tickets**.
