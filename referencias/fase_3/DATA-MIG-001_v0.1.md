---
documento: DATA-MIG-001
version: 0.1-candidata
fecha: 2026-11-10
estado: plan de migración, NO ejecutado
---
# DATA-MIG-001 — Estrategia de migración y evolución

## 1. Herramientas y entornos

- SQLAlchemy 2 + Alembic y PostgreSQL real (versión del servidor fijada y probada en INC-00); no utilizar `create_all()` como mecanismo de evolución.
- Una cadena lineal inicial de revisiones para evitar ramas de migraciones; no incluir seeds de negocio en revisiones.
- El archivo `ddl/DATA-DDL-001_CANDIDATO.sql` es **referencia revisable**, no ejecutar como migración ni como sustituto de Alembic. Tras aceptación, trasladar en revisiones controladas, especialmente índices parciales, FK compuestas, triggers y restricciones `CHECK`.

## 2. Orden por dependencias

| Revisión candidata | Alcance | Notas |
|---|---|---|
| `0001_identity_clients_process` | `persons`, `clients`, `accounts`, `account_roles`, `auth_sessions`, `judicial_processes` | Roles humanos ≠ roles DB; sin datos sintéticos aún |
| `0002_acquisition_tracking` | `acquisition_runs`, `observations`, `observed_actions`, `trackings`, `external_tracking_scopes`, `internal_tracking_assignments` | FK baseline a observations sin ciclo; triggers estado adquisición/append-only |
| `0003_comparison_novelties` | `comparisons`, `technical_changes`, `tracking_evaluations`, `novelties`, `novelty_reviews` | FKs compuestas y restricciones idempotentes |
| `0004_publication_audit` | `publications`, `publication_versions`, `publication_preparers`, `publication_version_novelties`, `publication_approvals`, `state_transitions`, `audit_events` | Crear FK puntero `current_version_id` tras versions y triggers de aprobación/publicación |

Todas las revisiones fijan nombres estables de constraints e índices según convención `pk_`, `fk_`, `uq_`, `ck_`, `ix_` / `ux_`. El agente debe revisar migración autogenerada **manualmente**: Alembic no detecta de forma universal `CHECK`, triggers y todos los cambios de objetos. No añadir dependencias de red a `upgrade`.

## 3. Procedimiento mínimo de aceptación de migraciones

1. Crear PostgreSQL descartable aislado en Compose, `TZ=UTC` o timezone de sesión establecida UTC.
2. Instalar dependencias fijadas; ejecutar `alembic upgrade head` desde DB vacía.
3. Verificar `alembic current`, tablas/constraints/índices/triggers y `alembic check` si el proyecto/configuración lo soporta. La ausencia de drift detectado no sustituye pruebas de triggers.
4. Ejecutar pruebas negativas de FK/UNIQUE/CHECK/rol por persona, transacciones concurrentes y rollback real.
5. Ejecutar una **segunda vez** `alembic upgrade head`; debe ser idempotente como operación de actualización.
6. Ejecutar seed sintético por comando explícito local/test; validar 18 AT al terminar su implementación.
7. Para reversión de prototipo **descartable** probar downgrade de la cadena en DB aislada y reconstrucción desde cero. Para entornos con datos, preferir restauración de respaldo + plan específico, **no downgrade destructivo automático**.
8. Registrar hashes, versión de servidor, versión de migraciones y resultados de tests en CI. No reutilizar DB de pruebas que contenga datos reales.

## 4. Cambio de schema durante evolución

- Cambio de nombre de columna con usuarios activos: patrón expandir → desplegar código compatible → migrar datos → contraer; diseño y control de downtime cuando haya despliegue real.
- Cualquier cambio en la relación cliente-proceso/seguimiento, política de baseline, `DEC-08/09` o identidad debe motivar actualización de `DOMAIN/DEC/ADR/DATA/API/TEST` y revisión de migración.
- Cambiar el comparador requiere `rule_version` nueva; no reescribir comparaciones técnicas pasadas.
- Nuevos conectores: abandonar `CHECK (source_code='DEMO-FIXTURE')` mediante migración explícita, agregar metadatos/versionado de fuente sin contaminar reglas judiciales con JSON irrestricto.
- Nunca almacenar secretos/sesiones como parte del fixture publicado en repositorio; hashes de contraseñas demo se generan localmente desde credenciales de prueba no reales.

## 5. Control de aprobación

No se crea ni ejecuta Alembic hasta que los autores acepten el modelo propuesto y se resuelvan las políticas críticas registradas en `DEC-F3-001`. El agente no debe prometer rollback o compatibilidad productiva sin probarlos.
