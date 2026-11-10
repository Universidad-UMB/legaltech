---
documento: ARCH-INT-001
version: 0.1-candidata
fecha: 2026-11-10
estado: contratos internos lógicos, NO OpenAPI ni interfaces Python definitivas
---

# ARCH-INT-001 — Contratos entre módulos, flujos y controles

## 1. Regla de composición

Cada caso de uso expone una operación de aplicación al API o a otro caso de uso autorizado. No se llama a otro endpoint HTTP para colaborar internamente. La capa de dominio solo conoce datos de dominio/objetos de valor y no depende de PostgreSQL ni FastAPI. Los repositorios trabajan bajo el mismo UoW cuando una operación requiere una transacción que cruza módulos. Solo el orquestador dueño del caso de uso ordena la operación y realiza `commit` una vez.

## 2. Contratos lógicos mínimos

| Contrato | Produce / devuelve | Consumidor | Regla de seguridad/consistencia | Se concreta en |
|---|---|---|---|---|
| `ResolvePrincipal(session_token)` | cuenta, personaId, roles, cliente externo, vigencia | Todos los casos protegidos | No confiar en claims enviados por cliente, token solo digest | DATA/API/SEC |
| `Authorize(action, principal, resourceRef)` | decisión deny-by-default, motivo de categoría | Casos de uso / portal | Resolve tenant y ámbito desde DB, no de cuerpo HTTP | SEC/API |
| `GetTracking(ref)` | id, clientId, processId, estado, baseline | Observations, Novelties, Portal | Acceso interno contextual; lecturas externas filtradas | DATA |
| `AcceptObservation(result)` | snapshot comparable o error de cobertura | Tracking/Comparison | Instantánea completa, provenance/time/version | DATA |
| `CompareSnapshots(old,new,ruleVersion)` | cambios técnicos/reason no-comparable | Novelties | Misma causa genera mismo cambio lógico | DATA/TEST |
| `EvaluateChange(tracking,change)` | elegible/no elegible e identificador de novedad | Novelties | Baseline del seguimiento; unicidad seguimiento+cambio | DATA |
| `RecordReview(novelty,actor,decision)` | nuevo estado e historial | Publications | Operativa vs jurídica, no cruzar roles | DATA/SEC |
| `ApproveVersion(version,principal)` | resultado de decisión | Publications | Snapshot congelado, abogado previo, persona distinta | DATA/SEC |
| `PublishLocal(version)` | versión vigente confirmada | Portal | Estado y puntero vigente en mismo commit | DATA |
| `ReadPublishedForPrincipal(ref,principal)` | publicación vigente o denegación | API externa | Verifica cliente/estado/ámbito al leer, no solo en login | API/SEC |

Son nombres conceptuales. La API pública, errores y firmas reales deben describirse en `API-001`. Los modelos SQL no se importan como salida pública.

## 3. Flujo de baseline y comparación

1. Aplicación solicita la lectura sintética; `ObservationSource` no se conecta a Internet.
2. `observations` valida resultado/procedencia, normalización de ACT y cobertura; guarda estado. Fallida/incompleta no reemplaza baseline ni devuelve «sin cambios».
3. En transacción, `tracking` adopta primera observación comparable de un seguimiento sin crear novedades retrospectivas; referencia observable y corte quedan registrados.
4. Comparación técnica de `OBS-001` y `OBS-002` por `ACT-XX` produce `ACT-06` una sola vez para ese par de snapshots y versión de reglas.
5. `novelties` comprueba `SEG-A-001` activo y elegible respecto a su baseline; inserta única `(seguimiento,cambio)` o devuelve existente. `SEG-B-001` adopta OBS-002 como baseline inicial y no recibe novedad retroactiva por esa diferencia.
6. Si el mismo par se procesa repetidamente o dos entregas concurrentes coinciden, la base de datos impide duplicados. El conflicto de unicidad se traduce a resultado idempotente; **no hacer rollback de toda la sesión y seguir reutilizándola sin nueva transacción**.
7. Un fallo de adquisición o de integridad invalida la comparación; no se interpreta como certeza de ausencia de actuaciones.

## 4. Flujo de revisión, aprobación y publicación

1. `novelties` registra la verificación operativa por analista con estado, identidad y evidencia; el abogado autorizado registra valoración jurídica. La regla conservadora de revisión obligatoria sigue siendo **propuesta de demo**, no DEC-08 ratificada.
2. El preparador interno autorizado selecciona una novedad revisada de su ámbito y crea `PublicationVersion` con contenido textual y destinatario del seguimiento; guarda preparadores por `personaId`.
3. Someter congela el snapshot. Se prohíbe modificarlo en sitio; un cambio crea versión nueva y vuelve a someter/aprobar.
4. La aprobación verifica persona jurídica/humana distinta de todos los preparadores de esa versión, permiso de coordinador y estado de revisión. Se conserva actor y decisión sobre la **versión exacta**. Esta salvaguarda de segregación sigue siendo propuesta DEC-09.
5. `PublishLocal` solo admite versión aprobada, registra transición y selecciona versión vigente atómicamente. Ante fallo de persistencia, no existe respuesta exitosa ni versión parcialmente visible. No se hace notificación externa.
6. `portal` al consultar aplica `ResolvePrincipal`, `Authorize` y una lectura acotada para la versión `Publicada` y vigente. Suspensión de cliente o finalización de seguimiento deniega lectura incluso si la versión conserva estado interno Publicada.

## 5. Autorización: dos controles que se complementan

**A. Control por acción**: rol/permiso de operación, cuenta habilitada, persona adecuada, asignación interna explícita o ámbito externo. No implementar `is_superuser=True` como bypass universal de reglas del dominio.

**B. Control por objeto**: el proceso puede ser compartido, **la referencia seguida en el recurso es la raíz del aislamiento**. Los repositorios públicos deben tener consultas de selección que incluyan relación `cliente → seguimiento → ámbito de cuenta` para externo; verificar cliente y seguimiento actuales; seleccionar solo versión publicada vigente. No hacer `SELECT publication by id` y confiar únicamente en ocultarlo del DTO.

La falta de ámbito devuelve denegación genérica; la elección entre `403` y `404` y formato del error pertenece a API/SEC. Prohibido filtrar contenido, nombre del cliente ajeno o existencia precisa del recurso en errores. La auditoría de denegaciones registra datos mínimos sanitizados. CORS no sustituye la autorización. Un test de cliente A sin SEG-A-002 comprueba que compartir cliente tampoco significa ámbito completo.

## 6. Contrato de errores de dominio (no HTTP aún)

- `AuthenticationFailed`: token inválido/expirado/revocado o credenciales incorrectas.
- `ForbiddenOperation`: carece de rol/asignación/ámbito/estado actual.
- `NotFoundInScope`: recurso fuera del alcance de la consulta autorizada (no revelar pertenencia).
- `InvalidStateTransition`: guarda de estado no satisfecha.
- `NotComparableObservation`: fuente, completitud o corte inválidos; nunca silencio.
- `OptimisticConflict` / `UniquenessConflict`: operación concurrente no compatible; si es exactamente la misma operación idempotente, recuperar el resultado ya confirmado.
- `VersionNotImmutable` / `ApprovalConflict`: intento de editar o aprobar una versión congelada, o aprobar por preparador.
- `PersistenceFailure`: fallo técnico, no éxito parcial ni resultado público.

La traducción a RFC 9457 / `problem+json` se evaluará en API-001. No exponer detalles internos de SQL o tracebacks.

## 7. Concurrencia: escenarios que no se delegan al criterio del agente

| Caso | Resultado exigible | Decisión posterior |
|---|---|---|
| Dos entregas de mismo cambio a A | Una novedad, resultados compatibles | DATA define UNIQUE + manejo de conflicto |
| Dos solicitudes de baseline A simultáneas | Una sola primera baseline; no generar histórica | DATA define fila bloqueada/versionada |
| Dos aprobaciones en estado pendiente | Como máximo una transición válida, sin sobrescribir identidad | DATA y API definen versión esperada |
| Publicación fallida tras actualizar estado pero antes del puntero | Rollback íntegro, ninguna lectura externa de nueva versión | Integration test PostgreSQL |
| Suspensión entre solicitud y lectura | Verificar al momento del acceso bajo política consistente; no confiar en cache de login | SEC/DATA define nivel concreto de concurrencia y aceptación |
| Recuperar novedad tras conflicto UNIQUE | Nuevo UoW / rollback adecuado y consulta de existente | Tests integración concurrente |

## 8. Matriz mínima de lecturas

| Actor / contexto | Proceso común | Seguimiento A | OBS compartida | NOV-A-001 | PUB-A-001 vigente |
|---|---:|---:|---:|---:|---:|
| Analista interno asignado a A | Contextual | Permitido | Contextual y auditoría | Permitido por permiso | Solo permiso interno |
| Abogado asignado a A | Contextual | Permitido | Contextual | Valoración permitida | Solo permiso interno |
| Cuenta externa A con SEG-A-001 | No se expone referencia global en portal | Proyección limitada | No directamente | Solo información comunicada | Sí, si cliente/seg activa |
| Cuenta externa A sin ámbito SEG-A-002 | No concede ámbito | Denegado para SEG-A-002 | No | No | No |
| Cuenta externa B intentando ID A | Sin autorización cruzada | Denegado | No | No | Denegado |
| Cuenta externa A con cliente suspendido o seguimiento finalizado | Denegado lectura ordinaria | Denegado | No | No | Denegado pese a estado Publicada |

*Una celda "Contextual" no concede privilegio universal: la matriz de permisos completa debe construirse en Fase 4.*

## 9. Restricciones de evolución

- Integración real de fuentes judiciales requiere autorización y estrategia de errores/cobertura, nunca una sustitución de fixture que oculte fallos.
- LLM multimodal requiere políticas legales, privacidad, validación humana y contratos por definir; no es punto de entrada del incremento.
- Un futuro envío externo o PDF requerirá separar «versión disponible localmente» de «entrega confirmada» y diseñar confiabilidad (outbox si aplica), sin alterar retroactivamente la semántica de demo.
