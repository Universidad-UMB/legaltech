---
documento: DATA-TEST-001
version: 0.1-candidata
fecha: 2026-11-10
estado: casos de prueba ESPECIFICADOS; NO EJECUTADOS
---
# DATA-TEST-001 — Plan de validación de persistencia en PostgreSQL

## 1. Enfoque

Ejecutar pytest + SQLAlchemy/psycopg sobre PostgreSQL real desechable en Compose, sin sustituir transacciones por mocks o SQLite. Cada caso prepara solo datos sintéticos, comprueba valor exacto y repite con DB limpia cuando corresponde. Separar tests SQL/DB (constraints, triggers) de tests UoW de aplicación (roles, estado, orden y acceso HTTP). El DDL es candidato: primero convertir y revisar migraciones Alembic.

## 2. Tests DB positivos y negativos (39 escenarios)

| ID | Escenario | Resultado esperado DB / aplicación | Referencia |
|---|---|---|---|
| DT-01 | Insertar radicado de 22, 24 caracteres o letras | `CHECK` rechaza | AT-01 |
| DT-02 | Repetir mismo radicado de 23 dígitos | `UNIQUE` rechaza o el caso de uso recupera el mismo proceso | AT-01 |
| DT-03 | Crear A y B sobre mismo proceso con clientes distintos | Dos seguimientos válidos; datos privados separados | AT-02 |
| DT-04 | Intentar asignar scope de cuenta A a seguimiento B | FK compuesta rechaza | AT-12 |
| DT-05 | Intentar asignar scope a cuenta INTERNAL | FK compuesta + CHECK rechazan | AT-17 |
| DT-06 | Repetir scope activo A a un mismo seguimiento | PK rechaza; operación puede ser idempotente | AT-17 |
| DT-07 | Adoptar en A observación de otro proceso | FK compuesta rechaza | AT-03 |
| DT-08 | Adoptar observación incompleta o sin `sealed_at` | Trigger rechaza; baseline queda sin cambios | AT-15 |
| DT-09 | Dos asignaciones concurrentes de primera baseline | Lock sobre fila; solo OBS-001 elegible como primera baseline | AT-03 |
| DT-10 | Insertar run FAILED y luego observación COMPARABLE | Trigger rechaza; error no equivale a no-cambio | AT-15 |
| DT-11 | Agregar ACT después de sellar observación | Trigger rechaza, snapshot intacto | AT-03/04 |
| DT-12 | Cambiar/eliminar snapshot sellado | Trigger rechaza | AT-04 |
| DT-13 | Comparar observaciones de diferentes procesos | FK compuesta rechaza | AT-04 |
| DT-14 | Comparar observaciones invertidas temporalmente o no selladas | Trigger rechaza | AT-04/15 |
| DT-15 | Reinsertar par OBS-001→OBS-002 con misma regla | `UNIQUE` rechaza; servicio devuelve comparación ya persistida | AT-05 |
| DT-16 | Reinsertar ACT-06 en misma comparación | `UNIQUE` rechaza; una fila definitiva | AT-05 |
| DT-17 | Cambio ACT-06 que no existe en snapshot nuevo | FK compuesta rechaza | AT-04 |
| DT-18 | Crear novedad con cambio de otro proceso o seguimiento | FK compuesta rechaza | AT-06/12 |
| DT-19 | Crear novedad con evaluación SKIPPED | FK compuesta decisión='ELIGIBLE' rechaza | AT-06 |
| DT-20 | Dos UoW insertan misma novedad A/ACT-06 a la vez | Una fila; perdedor recupera existente en nuevo UoW | AT-06 |
| DT-21 | Cuenta B consulta información interna A por ID | Caso de uso deniega; DB conserva ambas correctamente | AT-12 |
| DT-22 | Analista intenta insertar valoración jurídica por API | Caso de uso deniega, sin nueva review | AT-08 |
| DT-23 | Insertar preparador con person_id que no coincide con account_id | FK compuesta rechaza | AT-10 |
| DT-24 | Someter versión sin preparador o novedad vinculada | Trigger rechaza | AT-09 |
| DT-25 | Editar cuerpo, destinatario o enlaces de versión sometida | Trigger rechaza; requiere nueva versión | AT-18 |
| DT-26 | Preparador intenta aprobar usando otra cuenta misma persona | Trigger rechaza | AT-10 |
| DT-27 | Aprobar con hash distinto de versión congelada | Trigger rechaza | AT-10/18 |
| DT-28 | Publicación A apunta a versión de publicación B | FK compuesta rechaza | AT-11/12 |
| DT-29 | Publicación apunta a versión no PUBLISHED | Trigger rechaza | AT-09/10 |
| DT-30 | Falla tras actualizar versión a PUBLISHED, antes del puntero vigente | Rollback deja estado APPROVED/puntero anterior, sin fuga | AT-11 |
| DT-31 | Intentar consulta de versión A vigente con B, o A sin scope | Caso de uso retorna denegación sin contenido | AT-12/17 |
| DT-32 | Suspender A con versión publicada | Consulta denegada; pub/historial preservados | AT-13 |
| DT-33 | Finalizar SEG-A-001 con versión publicada | Consulta denegada; pub/historial preservados | AT-14 |
| DT-34 | Reiniciar API y DB sin reset | Datos existentes siguen disponibles | AT-16 + persistencia |
| DT-35 | Ejecutar seed sintético dos veces en mismo entorno demo | Resultado determinista; sin duplicados, sin reset implícito | AT-16 |
| DT-36 | Transición válida con actor; denegación auditada sin contraseña/token | Audit y estado correctos; información sanitizada | AT-07/08/13 |
| DT-37 | Dos cuentas de persona preparadora y una de aprobador distinto | El segundo puede aprobar si rol/scope/estado cumplen | AT-10 |
| DT-38 | Revisión operativa→jurídica y publicación de novedad de B en A | La inclusión cruzada falla por FK del seguimiento | AT-08/12 |

| DT-39 | Cuenta interna sin asignación a A intenta revisar novedad A | Servicio deniega aunque tenga rol ANALYST | AT-07/12 + negativo |

## 3. Matriz de 18 AT vs persistencia

| AT | Evidencia mínima persistente | Tests DT |
|---|---|---|
| AT-01 | Registro de proceso de 23 dígitos | 01–02 |
| AT-02 | A/B en mismo proceso | 03 |
| AT-03 | Baseline A=OBS001 sin novedades | 07–09 |
| AT-04 | Observación2 ACT06 y comparación | 11–14,17 |
| AT-05 | Un cambio idempotente | 15–16 |
| AT-06 | Una novedad A; B sin histórica | 18–20 |
| AT-07 | Review OPERATIVE de analista asignado | 36,39 |
| AT-08 | Review LEGAL de abogado, distinta responsabilidad | 22,36,38 |
| AT-09 | Borrador sin acceso externo | 24,29 |
| AT-10 | Aprobación persona diferente | 23,26–27,37 |
| AT-11 | Publicación atómica y acceso a vigente | 28–30 |
| AT-12 | B nunca accede a A | 04,18,21,28,31,38 |
| AT-13 | Suspensión bloquea portal sin borrar datos | 32 |
| AT-14 | Finalización bloquea portal sin borrar datos | 33 |
| AT-15 | Fuente fallida no significa silencio | 08,10,14 |
| AT-16 | Entorno demo reproducible | 34–35 |
| AT-17 | Cuenta A sin ámbito SEG-A-002 denegada | 05–06,31 |
| AT-18 | Cambio material exige nueva versión y aprobación | 25,27 |

## 4. Pruebas de transacciones y seguridad: condiciones

- `DT-09` y `DT-20` deben usar **dos conexiones y dos transacciones independientes**, barrera controlada de simultaneidad y asserts del conteo al finalizar. Las pruebas secuenciales no demuestran resistencia a carrera.
- `DT-30` inyecta excepción **después de actualizar estado y antes de actualizar puntero**; el rollback de UoW debe restaurar ambos y no emitir éxito. Validar consulta externa desde otra conexión tras rollback.
- `DT-21`, `DT-22`, `DT-31`, `DT-32`, `DT-33` requieren servicio/API; una FK no verifica autorización ni rol.
- En lectura concurrente de suspensión, medir la garantía elegida en DATA-001: solicitudes cuyo control de permiso se ejecute luego de commit de suspensión son rechazadas. No prometer revocación retroactiva de respuestas emitidas.
- Registro de denegación separado: si la transacción principal se revierte, emitir evento sanitizado en UoW nuevo sin guardar payload/token ni revelar IDs ajenos. Precisar política si auditoría fallara en Fase 4.
- Un error `IntegrityError` obliga a rollback o savepoint; una nueva consulta de resultado idempotente no debe realizarse en una transacción abortada.

## 5. Validación de migraciones y operación

- DB vacía→head, schema introspección constraints/triggers, `alembic current` correcto.
- `alembic upgrade head` repetido no genera tablas/índices duplicados.
- Seed local es explícito, identifica DB demo y no incluye credenciales reales.
- Tests se ejecutan tras reinstalar/levantar contenedores; la configuración/versión PostgreSQL queda registrada.
- No usar `drop_all()`/`down -v` en entornos con datos; pruebas destructivas solo DB efímera.

## 6. Criterio de salida

Los casos anteriores **no están ejecutados**. Después de migraciones revisadas, la aceptación requiere evidencia de los casos aplicables (incluidos negativos y concurrencia), no solamente ejecutar `CREATE TABLE` sin error. Registrar resultados PASA/FALLA/BLOQUEADA con logs sanitizados y versión exacta de código/migración.
