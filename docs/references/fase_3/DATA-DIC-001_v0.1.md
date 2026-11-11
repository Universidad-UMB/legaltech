---
documento: DATA-DIC-001
version: 0.1-candidata
fecha: 2026-11-10
estado: diccionario físico propuesto, tipos y nulabilidad definidos con referencia a DDL candidato
---
# DATA-DIC-001 — Diccionario de datos (primer incremento)

**Convenciones:** `PK` clave primaria; `FK` foránea; `UK` unicidad; `NN` no nulo; `?` nullable; `ts` = `timestamptz`; `uuid` asignado en aplicación. El DDL manda respecto a la sintaxis de constraints. Todos los `created_at`/`updated_at` son `ts` UTC. No hay información judicial real.

## A. Identidad y clientes

| Tabla | Columnas y tipos | Restricciones y significado |
|---|---|---|
| `persons` | `id uuid PK`, `display_name varchar(160) NN`, `created_at ts NN` | Identidad humana; no se infiere de alias de cuenta |
| `clients` | `id uuid PK`, `client_code varchar(32) NN UK`, `name varchar(180) NN`, `status varchar(12) NN`, `created_at ts NN`, `updated_at ts NN` | ACTIVE/SUSPENDED; no borrado histórico |
| `accounts` | `id uuid PK`, `person_id uuid NN`, `username varchar(120) NN`, `password_hash text NN`, `account_kind varchar(10) NN`, `client_id uuid ?`, `status varchar(10) NN`, `created_at ts NN` | Username normalizado único; EXTERNAL exige cliente; INTERNAL lo prohíbe; FK persona |
| `account_roles` | `account_id uuid NN`, `account_kind varchar(10) NN`, `role_code varchar(24) NN` | PK cuenta+rol, FK tipo; externos solo EXTERNAL_READER; internos roles operativos |
| `auth_sessions` | `id uuid PK`, `account_id uuid NN`, `token_digest bytea NN UK`, `issued_at ts NN`, `expires_at ts NN`, `revoked_at ts ?` | SHA-256 digest bytes/32; token no persistido; fecha de expiración posterior a inicio |
| `internal_tracking_assignments` | `account_id uuid NN`, `account_kind varchar(10) NN`, `tracking_id uuid NN`, `assigned_at ts NN`, `revoked_at ts ?` | PK cuenta+seguimiento; cuenta INTERNAL; alcance interno explícito por recurso, no rol global |
| `external_tracking_scopes` | `account_id uuid NN`, `account_kind varchar(10) NN`, `client_id uuid NN`, `tracking_id uuid NN`, `permission_code varchar(32) NN`, `granted_at ts NN`, `revoked_at ts ?` | PK cuenta+seguimiento+permiso; dos FK compuestas; revocación sin borrar. Solo READ_PUBLICATIONS en demo |

## B. Judicial y adquisición

| Tabla | Columnas y tipos | Restricciones y significado |
|---|---|---|
| `judicial_processes` | `id uuid PK`, `radicado varchar(23) NN UK`, `label varchar(180) ?`, `created_at ts NN` | Regex 23 dígitos; único en demo |
| `acquisition_runs` | `id uuid PK`, `process_id uuid NN`, `source_code varchar(32) NN`, `status varchar(12) NN`, `request_key varchar(100) NN UK`, `requested_at ts NN`, `finished_at ts ?`, `error_code varchar(64) ?`, `coverage_note text ?` | PENDING/SUCCESS/INCOMPLETE/FAILED; DEMO-FIXTURE; fallo requiere causa; terminal no reescribible |
| `observations` | `id uuid PK`, `process_id uuid NN`, `acquisition_run_id uuid NN UK`, `quality varchar(16) NN`, `observed_at ts NN`, `received_at ts NN`, `sealed_at ts ?`, `payload_sha256 varchar(64) NN`, `provenance varchar(80) NN`, `coverage_note text ?` | quality COMPARABLE/INCOMPLETE/INDETERMINATE; FK adquisición+proceso; se completa con actuaciones, luego `sealed_at` hace inmutable todo el snapshot |
| `observed_actions` | `observation_id uuid NN`, `action_key varchar(64) NN`, `content_sha256 varchar(64) NN`, `description text NN`, `occurred_on date ?` | PK observación+ACT-XX; append-only; no declarar clave ACT como identificador judicial global |
| `trackings` | `id uuid PK`, `tracking_code varchar(40) NN UK`, `client_id uuid NN`, `process_id uuid NN`, `status varchar(12) NN`, `baseline_observation_id uuid ?`, `last_adopted_observation_id uuid ?`, `created_at ts NN`, `updated_at ts NN` | PENDING/ACTIVE/FINISHED; ambas obs pertenecen al mismo proceso; ambas presentes/ausentes juntas; máximo un seguimiento no finalizado por cliente+proceso según PR-F3 |

## C. Comparación y novedades

| Tabla | Columnas y tipos | Restricciones y significado |
|---|---|---|
| `comparisons` | `id uuid PK`, `process_id uuid NN`, `old_observation_id uuid NN`, `new_observation_id uuid NN`, `rule_version varchar(32) NN`, `result varchar(16) NN`, `created_at ts NN` | Par ordenado diferente, misma causa+versión única; se completa con actuaciones, luego `sealed_at` hace inmutable todo el snapshot |
| `technical_changes` | `id uuid PK`, `comparison_id uuid NN`, `process_id uuid NN`, `new_observation_id uuid NN`, `action_key varchar(64) NN`, `change_kind varchar(12) NN`, `evidence text NN`, `created_at ts NN` | ACT introducida debe existir en observación nueva; solo ADDED en demo; UNIQUE (comparación, acción, tipo) |
| `tracking_evaluations` | `id uuid PK`, `tracking_id uuid NN`, `process_id uuid NN`, `comparison_id uuid NN`, `decision varchar(12) NN`, `reason text NN`, `evaluated_at ts NN` | ELIGIBLE/SKIPPED; UNIQUE seguimiento+comparación; mismo proceso |
| `novelties` | `id uuid PK`, `novelty_code varchar(40) NN UK`, `tracking_id uuid NN`, `client_id uuid NN`, `process_id uuid NN`, `comparison_id uuid NN`, `change_id uuid NN`, `evaluation_id uuid NN`, `evaluation_decision varchar(12) NN`, `status varchar(32) NN`, `created_at ts NN`, `updated_at ts NN` | Mismo seguimiento/proceso/cambio/evaluación, ELIGIBLE obligatoria; UNIQUE seguimiento+cambio |
| `novelty_reviews` | `id uuid PK`, `novelty_id uuid NN`, `review_kind varchar(16) NN`, `review_sequence int NN`, `actor_account_id uuid NN`, `actor_person_id uuid NN`, `decision text NN`, `evidence_note text NN`, `reviewed_at ts NN` | OPERATIVE/LEGAL; actor cuenta y persona ligados; reviews append por secuencia; transiciones en `state_transitions` |

## D. Publicaciones y auditoría

| Tabla | Columnas y tipos | Restricciones y significado |
|---|---|---|
| `publications` | `id uuid PK`, `tracking_id uuid NN`, `client_id uuid NN`, `current_version_id uuid ?`, `created_at ts NN` | Contenedor privado; puntero opcional solo a versión propia publicada |
| `publication_versions` | `id uuid PK`, `publication_id uuid NN`, `version_number int NN`, `recipient_tracking_id uuid NN`, `recipient_client_id uuid NN`, `status varchar(24) NN`, `content_text text NN`, `content_sha256 varchar(64) NN`, `created_at ts NN`, `frozen_at ts ?`, `approved_at ts ?`, `published_at ts ?` | DRAFT→PENDING_APPROVAL→APPROVED/REJECTED→PUBLISHED; UK publicación+versión; snapshot inmutable al someter |
| `publication_preparers` | `version_id uuid NN`, `person_id uuid NN`, `account_id uuid NN`, `recorded_at ts NN` | PK versión+persona; impedir cambio tras someter |
| `publication_version_novelties` | `version_id uuid NN`, `tracking_id uuid NN`, `novelty_id uuid NN` | PK versión+novedad; FK misma pertenencia al seguimiento |
| `publication_approvals` | `id uuid PK`, `version_id uuid NN UK`, `approver_account_id uuid NN`, `approver_person_id uuid NN`, `verdict varchar(8) NN`, `snapshot_sha256 varchar(64) NN`, `justification text NN`, `decided_at ts NN` | APRUEBA/RECHAZA según `APPROVE`/`REJECT`; distinto de todo preparador; se completa con actuaciones, luego `sealed_at` hace inmutable todo el snapshot |
| `state_transitions` | `id uuid PK`, `resource_type varchar(24) NN`, `client_id uuid ?`, `tracking_id uuid ?`, `novelty_id uuid ?`, `version_id uuid ?`, `from_state varchar(40) ?`, `to_state varchar(40) NN`, `actor_account_id uuid ?`, `actor_person_id uuid ?`, `actor_kind varchar(8) NN`, `reason text NN`, `request_id uuid NN`, `occurred_at ts NN` | Exactamente 1 FK tipada, cuenta-persona coherente o SYSTEM; se completa con actuaciones, luego `sealed_at` hace inmutable todo el snapshot |
| `audit_events` | `id uuid PK`, `request_id uuid NN`, `event_code varchar(64) NN`, `result varchar(10) NN`, `actor_account_id uuid ?`, `resource_kind varchar(32) ?`, `resource_id uuid ?`, `sanitized_reason varchar(100) ?`, `created_at ts NN` | SUCCESS/DENIED/ERROR; sin credenciales, tokens ni datos judiciales sensibles; se completa con actuaciones, luego `sealed_at` hace inmutable todo el snapshot |

## E. Notas de integridad

- Columnas redundantes `client_id`, `process_id` en las tablas privadas deben tener **FK compuestas**, no confiar en que la aplicación las mantenga iguales.
- `content_sha256` y hashes técnicos son SHA-256 hexadecimal en minúsculas suministrados/verificados por la aplicación, con validación sintáctica en DB; no es una firma digital.
- Una nueva revisión de novedad usa `review_sequence` ascendente; la aplicación decide si está autorizada. No modificar una revisión anterior.
- El DDL candidato contiene además triggers de append-only y snapshot; deben ser revisados y replicados explícitamente en Alembic.
- Roles de acceso a la **base** se implementan en despliegue; `account_roles` describe usuarios de la **aplicación**, no roles PostgreSQL.
