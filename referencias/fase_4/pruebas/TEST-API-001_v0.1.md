---
documento: TEST-API-001
version: 0.1-candidata
fecha: 2026-11-10
estado: diseñado, NO ejecutado
---
# TEST-API-001 — Pruebas HTTP/seguridad y trazabilidad

## 1. Método

Pytest + httpx TestClient para API y PostgreSQL desechable real para operaciones transaccionales; servicios de fixture sintético; no mocks para seguridad de consultas ni FKs. Seeds deterministas con tres seguimientos (`SEG-A-001`, `SEG-B-001`, `SEG-A-002`), dos snapshots (`OBS-001`,`OBS-002`), personas distintas para analista/abogado/preparador/coordinador y **dos cuentas pertenecientes a una misma persona preparadora** para negar autoaprobación.

## 2. Cobertura de pruebas de aceptación

| AT | operationId implicadas | Resultado |
|---|---|---|
| PROTO-AT-01 | `createProcess` | Radicado de 23 dígitos y proceso persistido |
| PROTO-AT-02 | `createTracking;activateTracking` | Dos seguimientos y activación de A |
| PROTO-AT-03 | `createAcquisition;adoptObservation` | OBS-001 baseline A sin novedad |
| PROTO-AT-04 | `createAcquisition;compareObservations` | OBS-002 añade ACT-06 |
| PROTO-AT-05 | `compareObservations` | Mismo par y regla no duplican cambio |
| PROTO-AT-06 | `adoptObservation;evaluateComparison` | A crea novedad una vez y B no retroactiva |
| PROTO-AT-07 | `startOperativeReview;escalateNovelty` | Revisión operativa de analista asignado |
| PROTO-AT-08 | `recordLegalReview` | Valoración jurídica humana de abogado asignado |
| PROTO-AT-09 | `createPublication;portalCurrentPublication` | Borrador no visible externamente |
| PROTO-AT-10 | `submitPublicationVersion;decidePublicationVersion` | Aprobación por persona distinta |
| PROTO-AT-11 | `publishPublicationVersion;portalCurrentPublication` | Publicación vigente tras commit |
| PROTO-AT-12 | `portalCurrentPublication` | B jamás obtiene A incluso por UUID |
| PROTO-AT-13 | `suspendClient;portalCurrentPublication` | Suspensión bloquea portal sin borrar datos |
| PROTO-AT-14 | `finishTracking;portalCurrentPublication` | Finalización bloquea portal, preserva historia |
| PROTO-AT-15 | `createAcquisition;getAcquisition` | Fallo no es no-cambios |
| PROTO-AT-16 | `healthz;login` | Seed/reinicio demo por CLI + API |
| PROTO-AT-17 | `portalCurrentPublication` | Cuenta A sin ámbito A2 recibe 404 |
| PROTO-AT-18 | `createPublicationVersion;submitPublicationVersion;decidePublicationVersion` | Nueva versión exige nueva aprobación |

La matriz editable también se entrega en `API-TRZ-AT-001.csv`. Ninguna AT se declara ejecutada.

## 3. Pruebas HTTP negativas adicionales

| ID | Dado / cuando | Resultado esperado |
|---|---|---|
| API-N01 | Sin Authorization en lectura protegida | 401 sin datos |
| API-N02 | Bearer inválido, revocado, expirado | 401 genérico |
| API-N03 | Contraseña/usuario erróneo | 401 genérico; no enumerar |
| API-N04 | Ráfaga login > límite configurado | 429, sin detalles de cuentas |
| API-N05 | Cuenta externa llama endpoint interno | 403 sin datos de recursos |
| API-N06 | Analista no asignado llama API de novedad A | 404 sin cambio |
| API-N07 | Usuario con rol correcto, sin scope de A2 | 404 mismo cuerpo que inexistente |
| API-N08 | B conoce UUID de publicación A | 404 sin nombre de A ni contenido |
| API-N09 | Alfa suspendido consulta con token expedido antes | 404, historial intacto |
| API-N10 | Seguimiento A finalizado consulta con token válido | 404, historial intacto |
| API-N11 | External intenta enviar `client_id` o `actor_id` no permitido | 422, no lo utiliza |
| API-N12 | Crea proceso con 22/24 dígitos o caracteres | 422 |
| API-N13 | Segunda adquisición FAILED usada para baseline | 409 o 422 documentado, baseline intacta |
| API-N14 | Repetición de comparación mismo par/regla | 200 mismos IDs, conteo estable |
| API-N15 | Dos evaluaciones concurrentes mismo tracking+comparación | Conteo novedad = 1; solo una creación |
| API-N16 | Abogado intenta iniciar revisión operativa | 403 |
| API-N17 | Analista intenta registrar valoración jurídica | 403 |
| API-N18 | Preparador intenta aprobar, incluso con otra cuenta misma persona | 403, aprobación ausente |
| API-N19 | Aprobador intenta publicar DRAFT | 409, ausencia de puntero público |
| API-N20 | Edición de versión sometida por cualquier endpoint | No existe PATCH; nueva versión distinta y no aprobada |
| API-N21 | Versión aprobada modificada de forma forzada en infraestructura | Trigger rechaza; no publicación |
| API-N22 | Error tras marcar versión PUBLISHED pero antes de puntero | Rollback íntegro; portal sin versión parcial |
| API-N23 | request_key adquisición repetida, misma carga | 200 mismo resultado |
| API-N24 | request_key adquisición repetida, distinta carga | 409 |
| API-N25 | Inyección JSON de campos extra/desconocidos | 422 |
| API-N26 | Error no controlado de servidor | 500 problem+json sin stack trace |
| API-N27 | GET portal sobre seguimiento autorizado sin publicada | 200 `available=false`, sin contenido |
| API-N28 | FAILED/INCOMPLETE informado en seguimiento autorizado | `coverage_status` real; nunca NO_CHANGES |
| API-N29 | Token de cuenta DISABLED aunque su sesión no caducó | 401 |
| API-N30 | Request externo con encabezado CORS de origen no permitido | Sin encabezados CORS habilitantes para origen |
| API-N31 | Reinicio del servidor sin borrar volumen PostgreSQL | Persistencia recuperable |
| API-N32 | Contraseñas, tokens y contenido en logs de error | Nunca presentes |
| API-N33 | Aprobador coincide con preparador secundario de misma versión | 403 |
| API-N34 | Id válido pero proceso/fuente no correspondiente | 404 o 409 sin efectos, según dominio |
| API-N35 | Solicitudes concurrentes a suspender y publicar | Acceso externo posterior a commit suspensión denegado |
| API-N36 | No hay publicación pero cuenta está en ámbito y activa | 200 `available=false`, no 404 por ausencia de publicada |

## 4. Evidencia y criterios para desarrollo

Cada prueba debe referenciar la versión de RF, el `operationId`, el escenario, las precondiciones del fixture, HTTP esperado, modificaciones en BD y auditoría. Conservar un reporte de CI (PASA/FALLA/BLOQUEADA), commit, hash de migración, y request_id sanitizado. DDL/Alembic/compose y estas pruebas se ejecutarán **en la fase de desarrollo**, nunca se presentan como ya superadas.

## 5. Pruebas de contrato

- Parsear YAML de OpenAPI 3.1.1, resolver todas las referencias `#/components/...` y verificar `operationId` único.
- Asegurar que cada ruta protegida declare Bearer y que únicamente login y health sean públicas.
- Confirmar error `problem+json` en 401/403/404/409/422 por los endpoints pertinentes.
- Revisar DTO por `additionalProperties:false` y evitar actor/tenant externo.
- Comparar `openapi.json` producido por FastAPI con contratos aprobados; documentar cualquier diferencia explícita, no silenciarla.
