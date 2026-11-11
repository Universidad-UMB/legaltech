---
documento: PROTO-DAT-001
version: 0.1-candidata
fecha: 2026-11-10
---
# PROTO-DAT-001 — Especificación y semilla de datos ficticios

## Fuente estructurada
- `../fixtures/PROTO-DAT-001.json`: clientes, procesos, seguimientos, identidades, cuentas, roles, ámbitos y orden de operaciones; **contrato de seed para implementar, no un seed ejecutable**.
- `../fixtures/adquisiciones/{OBS_001,OBS_002,FAILED,INCOMPLETE}.json`: resultados del adaptador offline.
- `../fixtures/PROTO-EXPECTED-001.json`: resultados verificables para pruebas y demo.

## Datos y coherencia
| Recurso | Configuración |
|---|---|
| Proceso compartido PROC-001 | Radicado `00000000000000000000001` (23 dígitos), SEG-A-001 Alfa y SEG-B-001 Beta |
| Proceso PROC-002 | Radicado `00000000000000000000002`, solo SEG-A-002 de Alfa para AT-17; evita contradicción con índice parcial propuesto |
| OBS-001 | Fecha 2026-10-15 UTC, ACT-01..05, comparable y sellada |
| OBS-002 | Fecha 2026-10-16 UTC, ACT-01..06, comparable y sellada |
| FAILED | Adquisición fallida sin snapshot comparable; cobertura NOT_VERIFIED |
| INCOMPLETE | Adquisición incompleta; no concluir NO_CHANGES |
| SEG-A-001 | Primera baseline OBS-001; luego comparación/novelty ACT-06, publicación v1 |
| SEG-B-001 | Primera baseline OBS-002, cero novedades retrospectivas |
| Lector Alfa | Ámbito solo SEG-A-001; sin SEG-A-002 aunque sean del mismo cliente |
| Lector Beta | Ámbito solo SEG-B-001; no puede leer publicaciones de Alfa |

## Identidad por persona
Personas preparadora `P-PREP` con cuentas `preparer.demo` y `preparer.alt.demo`, una con rol PREPARER y otra COORDINATOR: este último rol **no** debe servir para autoaprobar una versión que preparó la misma persona. `coordinator.demo` pertenece a `P-COORD` diferente y puede decidir cuando estado, rol y ámbito lo permiten.

## Credenciales y UUID
- Identificadores UUIDv5 **solo para datos de prueba y determinismo de fixtures**, no estrategia general de IDs de aplicación. Las cuentas no contienen contraseñas.
- El script real de bootstrap y asignación deberá validar que la cuenta externa tenga su cliente y que los seguimientos ya existan; la fase local **no precrea procesos ni seguimientos**. Deberá **exigir** `DEMO_SEED_PASSWORD` o entrada segura, validar entorno desechable y hashear con Argon2id. No incluir contraseñas reales ni tokens en Git, logs, screenshots o documentación.
- La repetición de seed en entorno demo debe hacer upsert con claves sintéticas estables y no duplicar. El reset destructivo será **comando local exclusivo para DB de demostración**, con comprobación explícita de nombre/entorno y sin endpoint REST.
- Todas las descripciones de actuaciones y valoraciones son ficticias. El agente no añadirá documentos judiciales, datos personales reales ni fuentes externas.

## Secuencia mínima antes de las pruebas
1. Ejecutar bootstrap local de identidades, clientes Alfa/Beta y roles (sin procesos/seguimientos); crear procesos/seguimientos mediante API y activar. Aplicar después comando local de ámbitos para A/B/A2.
2. Adquirir OBS_001, adoptar como baseline A y comprobar cero novedades.
3. Adquirir OBS_002 y comparar con OBS_001; resultado solo ACT-06 ADDED.
4. Evaluar para A y adoptar OBS_002 **después** de evaluar; repetir para demostrar idempotencia.
5. Adoptar OBS_002 como **primera baseline** de B, sin novedad retrospectiva.
6. Registrar revisión operativa y jurídica (textos ficticios), preparar v1, someter, rechazar autoaprobación por misma persona y aprobar con otra.
7. Publicar local y verificar portal de Alfa, 404 para Beta y Alfa→A2.
8. Suspender Alfa, comprobar denegación con versión conservada; reactivar si se requiere y finalizar SEG-A-001, comprobar denegación. Restaurar por reset de DB demo antes del siguiente ciclo AT.

No presupone que todas las filas de negocio existan en el seed antes del guion: **bootstrap prepara solo identidades, cuentas, roles y clientes; procesos y seguimientos se crean por API durante AT-01/02; los ámbitos se cargan por CLI solo después de existir seguimientos; observaciones/novedades/publicaciones también se crean por API**. Si el desarrollador necesita pre-seeds separados para tests unitarios, debe aislarlos sin contaminar el flujo E2E.
