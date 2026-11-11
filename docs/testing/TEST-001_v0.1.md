---
documento: TEST-001
version: 0.1-candidata
fecha: 2026-11-10
estado: estrategia y especificaciones; 0 ejecutadas
---
# TEST-001 — Estrategia de calidad y aceptación del backend

## 1. Propósito
Probar comportamiento de negocio (no solo CRUD), independencia de tenants, ausencia de duplicados y atomicidad sobre PostgreSQL real. Basar casos en `docs/references/fase_0/SCOPE-001`, `docs/references/fase_1/DOMAIN-001`, `docs/references/fase_3/pruebas/DATA-TEST-001`, `docs/references/fase_4/pruebas/TEST-API-001`, el contrato OpenAPI y los fixtures `PROTO-DAT-001`.

**Inventario:** 18 escenarios originales `PROTO-AT-01..18` en `docs/testing/specifications/PROTO-AT-001.json`, 36 negativos HTTP en `docs/testing/specifications/API-NEG-001.csv` y 39 DB/integración en `docs/testing/specifications/DATA-TEST-001.csv`. **Son especificaciones, no archivos de prueba Python ejecutables ni pruebas PASA.** Los 18 deben convertirse en tests automatizados con trazabilidad y además tener un guion de presentación reproducible.

## 2. Pirámide de pruebas y reglas

| Nivel | Implementación por agente | Alcance mínimo |
|---|---|---|
| Estática | `ruff`, comprobación de tipos, checks importación, contrato OpenAPI y secretos | Fallar CI ante import prohibido del dominio o pérdida de 35 operationId |
| Unitaria | Pytest sobre entidades/servicios puros | Reglas de baseline, orden de observaciones, identidad y deduplicación; sin DB cuando no aporta valor |
| Integración PostgreSQL | Pytest con DB efímera real y dos conexiones cuando corresponde | FKs compuestas, UNIQUE, triggers, migraciones, aislamiento, transacciones y auditoría |
| API/integración | Cliente HTTP de prueba contra FastAPI + DB temporal | 35 operaciones con DTO, roles y respuestas; los 36 negativos API |
| E2E demo por API | `PROTO-AT-01..18` sobre entorno restablecible | Flujo A/B, OBS-001/002, ACT-06, NOV-A-001, revisión, publicación, 404, suspensión y fin |
| No funcional | Seguridad, reproducibilidad y observabilidad | RNF-01..14 con evidencia proporcionada por código/ejecución; sin inventar SLA productivo |

## 3. Especificación verificable para cada AT

La matriz `docs/development/traceability/AT-RF-TEST-001.csv` relaciona AT → RF del catálogo → DOM-R → incremento → operationId → test a implementar. Los identificadores propuestos `tests/acceptance/test_proto_at_nn.py::test_escenario` son *rutas objetivo*, no archivos existentes.

| AT | Acción/expectativa principal | Principal artefacto de prueba |
|---|---|---|
| 01 | Crear proceso de radicado 23 dígitos sin duplicado | `createProcess`, DB radicado |
| 02 | Dos clientes; activar A; contexto correcto | `createTracking`, `activateTracking` |
| 03 | Primera OBS-001 para A; baseline, cero novedad | `createAcquisition`, `adoptObservation` |
| 04 | Comparación OBS-001→OBS-002, ACT-06 ADDED | `compareObservations` |
| 05 | Comparación repetida devuelve mismos IDs/conteo | API + UNIQUE de comparación |
| 06 | Evaluación/reintento: una NOV-A-001; B baseline posterior cero históricas | `evaluateComparison`, `adoptObservation` |
| 07 | Analista asignado verifica y escala; evidencia/estado | `startOperativeReview`, `escalateNovelty` |
| 08 | Abogado distinto registra revisión jurídica ficticia | `recordLegalReview` |
| 09 | Borrador no visible desde portal | `createPublication`, `portalCurrentPublication` |
| 10 | Misma persona con otra cuenta no puede aprobar; coordinador diferente sí | `submitPublicationVersion`, `decidePublicationVersion` |
| 11 | Publish/selección vigente en mismo commit; lectura Alfa | `publishPublicationVersion`, `portalCurrentPublication` |
| 12 | Beta con UUID de A recibe 404 sin contenido | Portal, caso BOLA |
| 13 | Suspender Alfa corta lecturas posteriores al commit, conserva PUBLISHED | `suspendClient`/portal |
| 14 | Finalizar A cierra acceso, sin borrar histórico | `finishTracking`/portal |
| 15 | FAILED e INCOMPLETE mantienen coverage_no_verificada | adquisiciones + lectura autorizada |
| 16 | Seed y reset local reproducible; sin endpoint de reset | scripts CLI/compose/test reinicio |
| 17 | Usuario Alfa sin scope A2 recibe 404 aunque mismo cliente | portal/ámbito explícito |
| 18 | Contenido cambiado obliga nueva versión no preautorizada | `createPublicationVersion`, decisión |

## 4. Pruebas adicionales de orden: TEST-ORD

| Caso | Precondición/acción | Esperado |
|---|---|---|
| TEST-ORD-01 | A con baseline OBS-001; intentar adoptar OBS-002 sin evaluación | 409; cursor sigue OBS-001; sin novedad omitida |
| TEST-ORD-02 | A con baseline OBS-001; comparar y evaluar OBS-001→OBS-002; luego adoptar OBS-002 | Una NOV-A-001 y cursor avanza a OBS-002 |
| TEST-ORD-03 | Dos hilos/conexiones avanzan A hacia OBS-002 al mismo tiempo | Ambos respetan lock y resultado estable; sin pérdidas ni duplicados |
| TEST-ORD-04 | A con cursor OBS-002 intenta adoptar OBS-001 anterior | 409, cursor no retrocede; baseline histórica intacta |
| TEST-ORD-05 | B sin baseline adopta directamente OBS-002 | `BASELINE_SET`, cero novedades retrospectivas |
| TEST-ORD-06 | Falla adquisición, intenta evaluar/adoptar | Ningún cambio de cursor; coverage no implica NO_CHANGES |

Estos casos exigen aceptación de `DF5-01` antes de imponerlos como política. Un test de concurrencia debe usar barrera explícita y **conexiones PostgreSQL independientes**, no dos llamadas secuenciales.

## 5. Proceso de ejecución en la etapa de desarrollo
1. Preparar ambiente efímero de test en Compose con PostgreSQL y credenciales generadas localmente.
2. Instalar dependencias bloqueadas en lock; `alembic upgrade head`; verificar índices/triggers y conexión de usuario runtime con privilegios restringidos.
3. Aplicar seed de cuentas/ámbitos y ejecutar fixtures sintéticos vía API; nunca mezclar datos reales.
4. Ejecutar formateo/análisis estático, unit, PostgreSQL integration, API negativos y E2E; reportar por familia `PASS/FAIL/BLOCKED/SKIP` con justificación.
5. Injectar fallo antes de commit de publicación y comprobar desde otra conexión la ausencia de publicación parcial; repetir conflictos de unicidad.
6. Validar runtime `/openapi.json` frente a `contratos/API-001.openapi.yaml`. Se aceptan sólo desviaciones documentadas/aprobadas, no cambios tácitos.
7. Reiniciar contenedor API, conservar volumen para persistencia (RNF-13); ejecutar reset **únicamente en DB desechable de demo** y comprobar restauración (AT-16).
8. Generar `reports/` con fecha, commit, versión de Python/PostgreSQL, head Alembic, ejecución y fallos. No insertar secretos en logs o evidencias.

## 6. Puertas de aceptación y prioridad
- **P0 (bloquea entrega):** los 18 AT, aislamiento A/B/A2, auth, fuga por UUID, idempotencia y carrera, publicación atómica, orden de observaciones, migraciones reales y vuelta a semilla determinista.
- **P1:** 36 negativos HTTP y 39 DT aplicables (la suite debe documentar motivos de cambios de especificación), NFR 1..14, detección de secretos y compatibilidad OpenAPI.
- **No se exige:** porcentaje arbitrario de cobertura, pruebas de carga productiva no definida, pentest certificado, verificaciones sobre CPNU, SAMAI, LLM o PDF.

`PASA` requiere ejecución sobre código/DB reales y evidencia. Esta fase entrega únicamente el diseño.
