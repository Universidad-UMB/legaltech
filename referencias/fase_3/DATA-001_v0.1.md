---
documento: DATA-001
version: 0.1-candidata
fecha: 2026-11-10
estado: diseño de persistencia sujeto a revisión de autores; NO migración aprobada ni ejecutada
alcance: backend funcional de demostración con datos exclusivamente sintéticos
fuentes: SCOPE-001 v0.1, DOMAIN-001 v0.1, DOM-ME-001 v0.1, ARCH-001 v0.1, ARCH-INT-001 v0.1, ADR-003/004/006, GATE-F3-001
---

# DATA-001 — Diseño de persistencia PostgreSQL para LegalTech

## 1. Objetivo y criterio de calidad

Transformar el modelo de dominio de Fases 0–2 en un modelo relacional implementable para un prototipo **real** con PostgreSQL; garantizar relaciones correctas, ausencia de duplicados, preservación de evidencia sintética, autorización contextual y publicación atómica. **No es el diseño completo de la V1** ni implica que las políticas jurídicas pendientes hayan sido ratificadas.

Se acompaña de un DDL **candidato de referencia**, tres vistas ER y una estrategia de pruebas/migraciones. No hay esquema aplicado, migraciones Alembic ejecutadas, ni pruebas de integración reales en esta fase.

## 2. Principios y decisiones de diseño

1. Una base PostgreSQL para el monolito. Tablas en esquema `public` inicialmente; propiedad lógica del dato documentada por módulo.
2. Clave interna `uuid` suministrada por aplicación; código humano/radicado no será PK. Uso de UUID aleatorio de buena calidad en backend, no considerado control de autorización.
3. Para el fixture: `radicado` `varchar(23)` con regex `^[0-9]{23}$` y unicidad global. **No inferir unicidad jurídica universal** entre todas las fuentes reales; revisar en V1.
4. `judicial_processes`, `observations` y `technical_changes` son datos técnicos **compartidos internamente**, mientras `trackings`, `tracking_evaluations`, `novelties`, revisiones y publicaciones son contextuales/privados.
5. Duplicar `client_id`/`process_id` en determinadas relaciones solo si existe FK **compuesta** que imposibilita una combinación contradictoria. No se usa el identificador de proceso como ámbito externo.
6. `timestamptz` para instantes; app y conexión DB trabajan en UTC. `observed_at` describe el momento que pretende cubrir la fuente; `received_at` cuándo llegó; `occurred_on` solo es fecha de actuación. No confundirlos.
7. `status` y `decision` con `varchar` + `CHECK` nombrable en migración: facilitan evolución controlada; migraciones explícitas para agregar estados de V1. No `ENUM` PostgreSQL en esta etapa.
8. JSONB no es necesario para invariantes del prototipo. Contenido textual y hashes se guardan en columnas tipadas; extensiones futuras de metadatos por fuente requerirán revisión.
9. Borrado cascada **prohibido por defecto**; usar `ON DELETE RESTRICT` y conservación histórica. Reiniciar la demo es una acción local destructiva explícita sobre una DB descartable, no una API.
10. Restricciones SQL y triggers protegen parte de la integridad. La **autorización, elegibilidad temporal, cambios de estado de negocio y control de rol** siguen en casos de uso bajo una transacción y se prueban en PostgreSQL real.
11. No se utiliza Row Level Security en el primer incremento. La aplicación aplica autorización por recurso y consultas filtradas; se registra el riesgo residual y la opción de RLS para V1.

## 3. Relaciones y cardinalidades fundamentales

| Relación | Cardinalidad | Invariante / implementación |
|---|---|---|
| `clients` → `trackings` | 1:N | Seguimiento pertenece a un único cliente |
| `judicial_processes` → `trackings` | 1:N | Un proceso puede pertenecer a seguimientos de A y B |
| `judicial_processes` → `observations` | 1:N | Instantánea de una fuente/consulta; no cliente |
| `acquisition_runs` → `observations` | 1:0..1 | Fallo no crea observación comparable |
| `observations` → `observed_actions` | 1:N | ACT-01..06 como claves estables **solo de fixture** |
| `trackings` → `observations` | N:0..1 baseline, N:0..1 último adoptado | Ambos deben referir al **mismo proceso** |
| `comparisons` → `technical_changes` | 1:0..N | Diferencia del par ordenado y versión de regla |
| `trackings` → `tracking_evaluations` | 1:N | Evaluación independiente de A y B |
| `trackings` → `novelties` | 1:N | `UNIQUE(tracking_id, change_id)` |
| `novelties` → `novelty_reviews` | 1:N | Verificación operativa y jurídica con autor humano |
| `trackings` → `publications` | 1:N | Comunicación asociada a seguimiento |
| `publications` → `publication_versions` | 1:N | Versión exacta y destinatario congelado |
| `publications` → `publication_versions` vigente | 1:0..1 | FK compuesta del puntero a su propia versión |
| `publication_versions` → `novelties` | N:M por tabla puente | Ambas en **igual seguimiento** |
| `publication_versions` → preparadores | 1:N | Persona natural estable, aunque tenga varias cuentas |
| `publication_versions` → approvals | 1:0..1 | Solo una decisión terminal por versión en demo |
| `accounts` → `external_tracking_scopes` | 1:N | Solo cuenta EXTERNAL, mismo cliente y ámbito explícito |

Los diagramas `diagramas/DATA-ER-001-*.mmd` contienen las relaciones editables y no sustituyen las constraints del SQL.

## 4. Inventario físico: 24 tablas

| # | Tabla | Contexto propietario | PK / claves e integridad destacada |
|---:|---|---|---|
| 01 | `persons` | Identidad | `id`; nombre para identidad humana |
| 02 | `clients` | Clientes | `id`; `client_code UNIQUE`; estado |
| 03 | `accounts` | Identidad | `id`; `person_id`; tipo interna/externa, EXTERNAL exige cliente |
| 04 | `account_roles` | Identidad | `(account_id,role_code)`; roles según tipo de cuenta |
| 05 | `auth_sessions` | Identidad | `id`; `token_digest UNIQUE`; expiración/revocación |
| 06 | `judicial_processes` | Seguimientos | `id`; `radicado UNIQUE`; 23 dígitos |
| 07 | `acquisition_runs` | Observaciones | `id`; `request_key UNIQUE`; resultado y cobertura |
| 08 | `observations` | Observaciones | `id`; un resultado por intento; pertenencia al proceso |
| 09 | `observed_actions` | Observaciones | `(observation_id,action_key)`; hash del elemento |
| 10 | `trackings` | Seguimientos | `id`; cliente/proceso; baseline y último observado con FK de proceso |
| 11 | `external_tracking_scopes` | Identidad | `(account_id,tracking_id,permission_code)`; ámbito mismo cliente |
| 12 | `internal_tracking_assignments` | Identidad | `(account_id,tracking_id)`; cuenta INTERNAL y asignación explícita por seguimiento |
| 13 | `comparisons` | Comparación | `id`; `UNIQUE(old,new,rule_version)` |
| 14 | `technical_changes` | Comparación | `id`; `UNIQUE(comparison,action_key,kind)`; ACT existente en observación nueva |
| 15 | `tracking_evaluations` | Novedades | `id`; `UNIQUE(tracking,comparison)`; decisión contextual |
| 16 | `novelties` | Novedades | `id`; `UNIQUE(tracking,change)`; FKs compuestas a evaluación/cambio/proceso |
| 17 | `novelty_reviews` | Novedades | `id`; tipo, secuencia, actor y evidencia |
| 18 | `publications` | Publicaciones | `id`; seguimiento/cliente, `current_version_id` opcional |
| 19 | `publication_versions` | Publicaciones | `id`; `UNIQUE(publication,version_number)`; destinatario y snapshot |
| 20 | `publication_preparers` | Publicaciones | `(version_id,person_id)`; persona ligada a cuenta |
| 21 | `publication_version_novelties` | Publicaciones | `(version_id,novelty_id)`; mismo seguimiento |
| 22 | `publication_approvals` | Publicaciones | `id`; `version_id UNIQUE`; veredicto y digest |
| 23 | `state_transitions` | Auditoría de dominio | `id`; una FK tipada por evento y actor |
| 24 | `audit_events` | Auditoría técnica | `id`; `request_id` y resultado sanitizado |

Descripción exhaustiva de columnas y nulabilidad: `DATA-DIC-001_v0.1.md`; DDL completo: `ddl/DATA-DDL-001_CANDIDATO.sql`.

## 5. Decisiones sobre seguridad y límites de acceso

- `accounts.account_kind` y `accounts.client_id` garantizan que una cuenta externa sea de **un solo cliente**. `external_tracking_scopes` fuerza mediante **dos FKs compuestas** que el seguimiento pertenezca al mismo cliente que la cuenta externa. Esto impide guardar asignación A→B, aunque la aplicación se equivoque.
- `internal_tracking_assignments` restringe la actuación de personal interno a seguimientos asignados y vigentes; tener rol no concede acceso a todos los clientes.
- Los roles internos `ANALYST`, `LAWYER`, `PREPARER`, `COORDINATOR`, `ADMIN` no son privilegios universales. Asignación interna por recurso, políticas de administración y atributos del principal se terminan de cerrar en SEC/API; nunca extrapolar `ADMIN` a bypass de toda guarda.
- El portal solo mostrará `publications.current_version_id`, si la versión está `PUBLISHED`, y solo después de verificar la cuenta, ámbito explícito no revocado, cliente `ACTIVE`, seguimiento `ACTIVE` y autorización por caso de uso. **Una FK válida no concede acceso**.
- Sesiones: `auth_sessions.token_digest bytea(32)` lógico (BYTEA+CHECK), no almacenar token en claro ni loguearlo. El backend debe comprobar expiración, revocación, cuenta habilitada y estado vigente cada vez. Duración de sesión y uso bearer/cookie se cierran en Fase 4.
- RLS: descartado **solo para demo local** por costo vs beneficio; usar consultas por contexto y tests BOLA/IDOR. Un futuro despliegue real deberá reconsiderar defensa en profundidad, permisos mínimos y separación de identidades DB.

## 6. Datos técnicos y baseline sin falsos negativos

Secuencia sintética esperada:

1. Proceso `00000000000000000000001` en `judicial_processes`. Dos seguimientos independientes: A y B.
2. `acquisition_runs` registra `SUCCESS`, `INCOMPLETE` o `FAILED`, con causa cuando corresponda. `observations` solo acepta fuentes finalizadas compatibles y registra `quality` propia. El servicio inserta observación y actuaciones en un mismo UoW y establece `sealed_at`; después de ese punto no se permiten nuevas actuaciones ni mutar el snapshot. Una adquisición con error puede quedar **sin observación**; ninguna de las dos se traduce en «sin cambios».
3. `OBS-001` incluye ACT-01..05. Con una transacción que bloquea fila `trackings` A (`FOR UPDATE`), A fija `baseline_observation_id` y `last_adopted_observation_id` a OBS-001 sin crear novedades.
4. `OBS-002` incluye ACT-01..06. La comparación de OBS-001 → OBS-002 por `rule_version=demo-v1` produce un `technical_change` ACT-06. Repetir mismo par y versión devuelve la comparación existente.
5. A evalúa esa comparación como `ELIGIBLE` y crea la novedad, con constraint que exige evaluación **ELIGIBLE** y par/cambio/proceso consistentes. A actualiza último adoptado a OBS-002 en el caso de uso correspondiente.
6. B se activa **después de OBS-002** y fija OBS-002 como primera baseline; no se crea novedad histórica en B. Esto es una regla del fixture, no una comparación global que ignore el seguimiento.

**Control de regresión temporal:** baseline no se reemplaza silenciosamente. La decisión de aceptar un nuevo `last_adopted_observation_id` exige verificación de orden, calidad y pertenencia al mismo proceso; se hace en aplicación bajo lock y se prueba en PostgreSQL. `CHECK` no compara marcas temporales en filas distintas.

## 7. Unicidad, concurrencia y transacciones

| Comando | Control DB | Control de aplicación/UoW | Resultado |
|---|---|---|---|
| Adoptar baseline | FK `(observation_id,process_id)` | `SELECT tracking FOR UPDATE`, `baseline IS NULL`, calidad/orden | Una sola primera baseline |
| Comparar | `UNIQUE(old,new,rule_version)` | Resultado determinista; al conflicto rollback/nueva transacción y leer ya existente | Una comparación por par+regla |
| Crear cambio | `UNIQUE(comparison,action_key,kind)` | ACT-XX debe corresponder a observación nueva | Cambio idempotente |
| Evaluar cambio por seguimiento | `UNIQUE(tracking,comparison)` | Solo para tracking activo/comparable | No duplicar evaluaciones |
| Crear novedad | `UNIQUE(tracking,change)` + FK de evaluación elegible | Estado tracking, versión y causa | Una novedad por seguimiento+cambio |
| Revisar novedad | FK `(actor_account,actor_person)` + historial | Rol, asignación y guarda de transición; UoW | Actuación atribuida y consistente |
| Someter versión | Trigger bloquea edición posterior, exige preparador y novedad relacionada | Valorar estado de novedad, digest, persona y roles | Versión congelada |
| Aprobar | `publication_approvals.version_id UNIQUE`; trigger no autor y digest coincidente | Rol coordinador, versión pendiente, misma persona por cuentas | No autoaprobación ni doble decisión |
| Publicar | FK `(current_version_id,id)`; trigger puntero publicado | Lock publicación y versión; cambiar estado+puntero+evento en **un commit** | Nada parcialmente disponible |
| Leer portal | Índices de scopes/trackings/publications | Consulta filtrada por tenant/ámbito/estados actuales | Sin lectura cruzada |

**Nivel de aislamiento inicial:** `READ COMMITTED` más bloqueos explícitos en mutaciones sensibles y constraints. Las transacciones se abren después de resolver datos no transaccionales; jamás se deja una transacción abierta durante llamadas externas. Si hay conflicto de unicidad, hacer rollback y **nuevo UoW** o savepoint correctamente aislado; no continuar con Session fallida.

**Carrera de suspensión vs lectura:** el estado se valida en la consulta autorizada; la garantía «ninguna lectura cuya comprobación de acceso ocurra después del commit de suspensión» es razonable para demo. La revocación de respuestas ya emitidas o lecturas que comenzaron antes no se garantiza; si negocio exige linealización más estricta hay que diseñar lock/protocolo adicional en SEC.

## 8. Versionado y preservación de evidencia

- `publications` es el contenedor. `publication_versions` almacena el texto exacto, `content_sha256`, `recipient_tracking_id`, `recipient_client_id`, `version_number`, estado y marcas temporales. `publication_preparers` congela la identidad **de persona** de todos los preparadores.
- Una vez solicitada autorización, no se cambia cuerpo, destinatario ni listas de novedades/preparadores; los triggers del DDL candidato protegen la inmutabilidad de esos componentes. Una corrección material crea **v2** con aprobación independiente.
- `publication_approvals` conserva veredicto, actor persona/cuenta, razón y hash de contenido. Un trigger prototipo prohíbe aprobación por cualquiera de los preparadores y valida que apunta al digest congelado. La habilitación de rol se comprueba en caso de uso.
- `publications.current_version_id` es FK compuesta a **versión de esa misma publicación**; trigger solo deja apuntar a `PUBLISHED`. Cambiar estado de versión y puntero en la **misma transacción** garantiza atomicidad. Sin puntero, aunque estado interno sea `PUBLISHED`, no hay versión externa vigente.
- Suspender A o finalizar su seguimiento solo bloquea consulta externa; **no cambia `publication_versions.status`** ni elimina historial.
- Datos de entrada `DEMO-FIXTURE` y contenido textual son ficticios. No hay entregas reales, archivos PDF, OCR, scraping ni implicaciones jurídicas automáticas.

## 9. Índices y costos

Se crean índices en columnas útiles para lecturas previstas: `(client_id,status)` en seguimientos, `(process_id,observed_at)` en observaciones, `(tracking_id,status,created_at)` en novedades, `(tracking_id)` en publicaciones, scope activo `(client_id,tracking_id) WHERE revoked_at IS NULL` y `request_id` en auditoría. `PRIMARY KEY` y `UNIQUE` ya generan índices; no duplicarlos. No se estima rendimiento de producción a partir de datos demo. Verificar planes con `EXPLAIN (ANALYZE, BUFFERS)` solo si hay volumen representativo, sin inventar umbrales.

## 10. Integridad cubierta y límites explícitos

**Protegido en DB:** forma de radicado, tipos de cuenta, pertenencia scope/cliente, proceso de baseline/cambio, unicidad de pares/novedades, decisión elegible de evaluación, destinatario de versiones, misma publicación para puntero, append-only de snapshots/auditoría, congelamiento de versión, segregación del aprobador a nivel persona en el DDL candidato.

**Protegido por servicio y pruebas, no por FK sola:** permisos por rol y asignación interna, identidad autenticada derivada de sesión, cronología de observaciones, precondiciones de revisión, cadena completa de transiciones de novedad/seguimiento/cliente, hashes calculados de contenido, obligación de un evento de auditoría en el commit, tratamiento jurídico admisible y filtrado externo de toda lectura. Un actor con acceso SQL administrativo puede saltarse controles; no hay afirmación de cumplimiento productivo.

**Riesgos pendientes:** semántica real de múltiples seguimientos del mismo cliente/proceso, radicados de múltiples fuentes/jurisdicciones, revocación bajo concurrencia fuerte, modificación/rectificación jurídica, flujos de reemplazo-retirada, retención legal, políticas de RLS y respaldo, envíos externos de comunicaciones.

## 11. Trazabilidad y puerta de salida

| Objetivo | Tablas / garantías | Aceptaciones |
|---|---|---|
| Compartido judicial vs privado | `judicial_processes`, `trackings`, `novelties` | AT-01,02,06,12,17 |
| Baseline y diferencia | `observations`, `observed_actions`, `comparisons`, `technical_changes` | AT-03,04,05,15 |
| Novedad y revisión | `tracking_evaluations`, `novelties`, `novelty_reviews` | AT-06,07,08 |
| Publicación vigente | `publications`, `publication_versions`, `publication_approvals` | AT-09,10,11,18 |
| Acceso contextual | `accounts`, `external_tracking_scopes`, `internal_tracking_assignments`, `auth_sessions` | AT-12,13,14,17 |
| Reinicio / reproducibilidad | scripts y esquema versionado, seeds local | AT-16 |

**Dictamen:** suficiente como **diseño candidato** para pasar a Fase 4 (API/seguridad), pero antes de delegar migraciones definitivas se deben aceptar D-F3 y ejecutar pruebas de esquema en PostgreSQL real. Ver `DEC-F3-001`, `DATA-TEST-001`, `DATA-MIG-001` y `GATE-F4-001`.
