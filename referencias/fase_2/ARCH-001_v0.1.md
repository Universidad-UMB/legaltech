---
documento: ARCH-001
version: 0.1-candidata
fecha: 2026-11-10
estado: propuesta de arquitectura para revisión de autores; no aprobada para V1 ni producción
alcance: backend persistente y demostrativo con datos sintéticos
fuentes: [SCOPE-001 v0.1, DEC-F0-001 v0.1, BACKLOG-F0-001 v0.1, DOMAIN-001 v0.1, DOM-ME-001 v0.1, DEC-F1-001 v0.1, PROTO-001 v0.1]
---

# ARCH-001 — Arquitectura candidata del backend LegalTech

## 1. Propósito y alcance

Esta especificación traslada el dominio de Fase 1 a una solución implementable mediante Python, FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, Pytest y Docker Compose. Es **diseño de arquitectura**, no contrato OpenAPI definitivo, esquema DDL ni evidencia de código funcional. Los requisitos del prototipo no se deben equiparar a cumplimiento completo de 150 RF de V1.

Escenario: organización operadora ficticia, clientes Alfa y Beta, proceso judicial compartido `00000000000000000000001`; seguimientos `SEG-A-001`, `SEG-B-001` y `SEG-A-002` sin ámbito externo; `OBS-001` (ACT-01..05), `OBS-002` (ACT-01..06); cambio técnico ACT-06, solo novedad `NOV-A-001`, revisión operativa/jurídica humana y versión textual `PUB-A-001` publicada localmente. Consulta exterior denegada por cliente cruzado, ausencia de ámbito, suspensión de Alfa o finalización del seguimiento. Fuente **DEMO-FIXTURE**, ninguna extracción judicial real ni LLM.

Normas de referencia (prácticas orientadoras, no certificaciones): ISO/IEC/IEEE 29148 (trazabilidad de requisitos), ISO/IEC 25010 (atributos de calidad), OWASP API Security Top 10 / ASVS y C4 para comunicar la arquitectura. La semántica del dominio tiene primacía sobre el framework.

## 2. Impulsores y atributos de calidad

| Impulsor | Decisión arquitectónica | Cómo se verificará |
|---|---|---|
| Aislamiento cliente/seguimiento | Autorización contextual por recurso + consultas acotadas al ámbito | AT-12/13/14/17, acceso directo a ID ajeno denegado |
| Idempotencia de comparación/novedad | Funciones deterministas + unicidad DB + manejo de conflicto bajo transacción | AT-05/06, dos solicitudes concurrentes |
| Consistencia de publicación | Transacción única: estado de versión y selección de vigente | AT-09/10/11/18 y fallo forzado |
| Rastreabilidad | Evidencias de observación, decisiones humanas, eventos de dominio/auditoría | AT-03/07/08/15 y lectura interna |
| Evolucionabilidad sin sobreingeniería | Monolito modular y adaptadores explícitos en bordes externos | Tests de dependencias e intercambio de fixture |
| Reproducibilidad | Compose + migraciones Alembic + fixture determinístico solo local | AT-16 y ejecución sobre DB vacía |
| Seguridad del prototipo | Autenticación server-side, contraseñas con Argon2id, sesión revocable, mínimos privilegios | Tests credenciales inválidas, sesión revocada, roles y ámbitos |

**No se atribuyen SLA, throughput, volúmenes o cumplimiento regulatorio de producción sin medición y validación.**

## 3. Vistas de arquitectura (diagramas en `diagramas/`)

- **C4 L1 / contexto (`C4-L1-CONTEXTO.mmd`):** analista, abogado, preparador, coordinador, cliente externo, API LegalTech; DEMO-FIXTURE dentro del sistema, sin fuentes externas reales.
- **C4 L2 / contenedores (`C4-L2-CONTENEDORES.mmd`):** consumidores HTTP (Swagger/cliente de prueba y futuro frontend), aplicación FastAPI, PostgreSQL; un proceso lógico de backend y una base de datos. No se muestran módulos de Python como contenedores.
- **C4 L3 / componentes (`C4-L3-BACKEND.mmd`):** módulos de dominio y servicios de aplicación dentro del contenedor FastAPI.
- **Secuencia (`SEQ-001-PUBLICACION-SEGURA.mmd`):** validación de revisión, aprobación por otra persona, publicación y acceso externo bajo política vigente.

C4 aquí es una convención de niveles y descripciones; se usan diagramas Mermaid editables en lugar de herramientas C4 específicas. Fuentes oficiales: https://c4model.com/introduction ; https://fastapi.tiangolo.com/tutorial/bigger-applications/ .

## 4. Estilo y estructura

**Selección candidata ADR-001:** monolito modular desplegado en una aplicación; PostgreSQL única; interacción síncrona en proceso; sin cola, broker, service mesh, motor BPMN o microservicios. La modularidad evita importar ORM ajeno a ciegas y hace verificables los límites de negocio.

**Arquitectura interna candidata ADR-002:** organización por funcionalidades (package-by-feature), con separación lógica:

1. `api`: `APIRouter`, DTO Pydantic, traducción de errores y extracción de principal; **sin lógica de negocio**.
2. `application`: casos de uso, coordinación de módulos, política de autorización, transacciones/UoW y puertos requeridos; **no llama HTTP a su propia API**.
3. `domain`: entidades y objetos de valor, reglas puras, invariantes, estados y excepciones de negocio; **sin FastAPI, SQLAlchemy, Pydantic HTTP ni acceso a red**.
4. `infrastructure`: modelos/consultas SQLAlchemy, adaptadores externos, reloj, autenticador y auditoría persistida; los detalles SQL se encapsulan tras contratos de aplicación.

No crear un framework genérico de CQRS, mensajería o repositorios universales. Separar archivos adicionales solo cuando aporten claridad. La inyección de dependencias sucede en composición de FastAPI (`bootstrap.py`, `api/dependencies.py`).

## 5. Módulos, propiedad y contratos

| Módulo | Propietario de decisiones | Colaboraciones permitidas | Regla crítica | Prioridad |
|---|---|---|---|---|
| `identity` | Persona, cuenta, credenciales/sesiones, roles y ámbitos | Provee `Principal` y autorización contextual | D1-06, DOM-R02 | INC-00 |
| `clients` | Cliente y estado de suspensión/reactivación | Consultas seguras para seguimiento/portal | DOM-R04/R19 | INC-01/06 |
| `tracking` | Proceso compartido, seguimiento privado, línea base | Consume observación comparable; aporta estado y `clienteId` | DOM-R05/R06 | INC-01/02 |
| `observations` | Ejecución, fuente, observación inmutable y cobertura | Expone resultado comparable, nunca «sin cambios» a partir de error | DOM-R07/R24 | INC-02 |
| `comparison` | Diferencias deterministas y cambio técnico | Consume datos de observación; no crea publicaciones | DOM-R08..10 | INC-03 |
| `novelties` | Elegibilidad por seguimiento, revisión, valoración y decisión | Consulta seguimiento y cambio, produce contenido revisado | DOM-R11..14 | INC-03/04 |
| `publications` | Versión textual, preparación, aprobación, vigente | Consulta revisión, identidad y seguimiento | DOM-R15..18/R23 | INC-05 |
| `portal` | Composición de lecturas externas autorizadas | Consulta identity, clients, tracking, publications mediante puertos/servicios | DOM-R19/R22 | INC-06 |
| `audit` | Registro de decisiones y denegaciones | Servicio transversal, no autoridad sobre estado de negocio | DOM-R20 | INC-00+ |

**Invariante estructural:** un `ProcesoJudicial` puede ser compartido. `Seguimiento`, baseline, elegibilidad, novedad, revisión, versión de publicación y ámbitos son específicos por cliente/seguimiento. Nunca exponer entidades `comparison` u `observations` compartidas directamente al portal externo.

**Dependencias dirigidas:** rutas → casos de uso → contratos de dominio/puertos. Repositorios implementan puertos; composición conecta implementaciones. Entre módulos se accede por contrato público de consulta/caso de uso, no por importación de sus tablas ni actualización directa de su estado. `portal` es un **orquestador de lectura**, no propietario de políticas ni tablas. No circularidad y no mantener transacciones abiertas mientras se hace I/O externo.

## 6. Consistencia, concurrencia e idempotencia

**Selección candidata ADR-003:** SQLAlchemy 2 *síncrono*, driver PostgreSQL `psycopg` 3, rutas síncronas `def` cuando usan DB; una `Session` por caso de uso/request, `UnitOfWork` explícito para mutaciones. El caso de uso controla el límite de `commit` y `rollback`; ni controladores ni repositorios hacen `commit`. Se usa `with session.begin():` o equivalente documentado, con transacciones cortas. Las sesiones no se almacenan en singleton ni se comparten entre requests/hilos. El diseño debe evitar conflictos entre transacciones implícitas y explícitas: abrir/gestionar la sesión desde UoW una sola vez para cada caso de uso. Ref: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html .

| Operación | Límite de atomicidad requerido | Estrategia de concurrencia propuesta |
|---|---|---|
| Activar seguimiento / adoptar baseline | Verificación de validez + actualización del seguimiento + auditoría exitosa | Bloqueo o versión de fila del seguimiento; no retroceder baseline |
| Incorporar observación | Estado, instantánea y metadatos juntos | Identificador de intento y referencias consistentes |
| Comparar observaciones | Resultado y conjunto de cambios de par | Unicidad por `(par, regla, tipo, clave_ACT)`; `get-or-create` fiable |
| Entregar cambio a A | Comprobación de elegibilidad + novedad única por seguimiento/cambio | Restricción UNIQUE + conflicto concurrente recuperable |
| Revisar novedad | Decisión humana, actor, estado e historial | Comprobar estado esperado y permisos en misma transacción |
| Someter/aprobar versión | Snapshot/versionado + guardas y persona natural | Inmutabilidad desde sometimiento; rechazar doble aprobación |
| Publicar local | Versión `Publicada` y referencia vigente de seguimiento | Una transacción; si falla, no queda parcialmente visible |
| Suspender/finalizar | Estado y trazas | Lecturas externas reevalúan autorización actual, no estado cacheado |

En Fase 3 se decidirán PK/FK, índices, claves compuestas y mecanismo puntual de `SELECT FOR UPDATE` / control optimista. `READ COMMITTED` puede ser la base de ensayo; no suponer que ese aislamiento, por sí solo, evita todas las carreras. Las restricciones de unicidad constituyen última línea contra duplicados.

**Auditoría:** decisiones exitosas y su evento se insertan en la misma transacción. Denegaciones o acciones rechazadas necesitan registro independiente, saneado y sin datos de otro cliente; **no se guardan dentro de una transacción que será revertida**. Para la demo se documentará una política explícita de fallo del registro de denegaciones (no prometer no repudio), en Fase 4. Evitar emitir eventos auditables desde `except` que puedan generar bucles de fallo.

## 7. Autenticación y autorización

**Selección candidata ADR-004:** credenciales ficticias y personas diferentes; contraseñas protegidas con Argon2id, sesión bearer opaca aleatoria, almacenada solo como digest en DB, expiración corta y revocación inmediata mediante consulta por petición; ninguna credencial fija en código o Git. Se puede sustituir más adelante por IdP/OpenID Connect según necesidad. El token de demo se retorna a cliente de prueba en login, no se debe aconsejar almacenarlo en `localStorage` del navegador; antes de construir SPA productiva se seleccionará flujo/cookie segura y defensa CSRF/CORS según arquitectura final.

**Autorización:** verificación por operación y recurso en la capa de aplicación/consultas, no únicamente por decorador de rol. Para externo: cuenta activa, cliente único y activo, seguimiento activo, pertenencia de seguimiento al mismo cliente, concesión explícita de ámbito vigente, versión Publicada/vigente. Para internos: rol *y* asignación/permiso de operación del fixture; sin privilegio global por defecto. IDs provistos por el solicitante no otorgan acceso por sí solos. `personaId` estable para impedir aprobación por misma persona que preparó. Al leer datos deben omitirse detalles de recursos ajenos; política HTTP 403/404 en API-001. Deben ejecutarse pruebas IDOR/BOLA y de acceso a propiedades. OWASP: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/ .

**No equivalencia:** que una versión siga internamente `Publicada` no da acceso externo tras suspensión de cliente/finalización de seguimiento. La API consulta la autorización vigente **en el momento de la solicitud**. No se promete seguridad de despliegue público con este diseño de demo.

## 8. Puertos hacia futuro sin código especulativo

| Interfaz conceptual | Implementación del incremento | Futuro posible, NO implementado |
|---|---|---|
| `ObservationSource` / `FuenteJudicialPort` | `DemoFixtureObservationSource` retorna estados completa/incompleta/fallida y actuaciones sintéticas | SAMAI/Publicaciones/CPNU si existe autorización y compatibilidad |
| `Clock` | Reloj sistema + fake de test si lo requiere | Servicio temporal externo no previsto |
| `AuditRecorder` | Persistencia PostgreSQL para eventos de demo | Centralización/retención formal posterior |
| `PublicationAvailability` | Escritura y lectura local de versión textual vigente | PDF final, canal externo/confirmación fiable |

No implementar ahora conectores a fuentes ni LLM, ni almacenar datos reales. Los puertos son **contratos mínimos usados por INC**; no generar clases para integraciones fuera de alcance salvo punto de extensión necesario para el fixture.

## 9. Despliegue local y operaciones

**ADR-007:** `docker compose` con dos servicios persistentes: `api` y `db` (PostgreSQL), volumen para DB y healthcheck; puerto DB no expuesto al host por defecto. `api` responde `/health/live` y `/health/ready` sin información sensible; documentación OpenAPI local. Ejecutar Alembic explícitamente antes de usar la API (`docker compose run --rm api alembic upgrade head` o comando equivalente); los seeds se ejecutan mediante comando CLI separado habilitado exclusivamente en `APP_ENV=local/test`, con confirmación de que la base solo contiene datos ficticios. No eliminar datos al reiniciar el contenedor. Definir `.env.example`, `.gitignore`, un `Dockerfile` no root, versiones/dependencias fijadas mediante lock, logs JSON/sanitizados, horas UTC, `request_id` sin secretos. Sin credenciales incluidas en la imagen.

El README del backend deberá especificar requisitos, arranque, health, migraciones, carga de fixture, pruebas, rollback de desarrollo y limpieza segura. Un `docker compose down -v` solo podrá usarse expresamente en una instancia demo descartable, nunca como paso genérico de mantenimiento.

## 10. Árbol objetivo de código (orientativo, no scaffolding ya implementado)

```text
backend/
├── pyproject.toml
├── uv.lock                         # si se selecciona uv como gestor de dependencias
├── alembic.ini
├── migrations/                    # revisiones versionadas, ejecutadas explícitamente
├── src/legaltech/
│   ├── main.py                    # aplicación FastAPI + routers
│   ├── bootstrap.py               # composición de casos de uso y adaptadores
│   ├── shared/
│   │   ├── config.py              # configuración validada por entorno
│   │   ├── db.py                  # engine/session maker y UoW
│   │   ├── errors.py              # errores de dominio y traducción HTTP
│   │   └── security.py            # utilidades sin permisos específicos de negocio
│   └── modules/
│       ├── identity/
│       ├── clients/
│       ├── tracking/
│       ├── observations/
│       ├── comparison/
│       ├── novelties/
│       ├── publications/
│       ├── portal/
│       └── audit/
│           # por módulo: api.py, application.py, domain.py, repository.py
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── acceptance/
├── scripts/seed_demo.py
├── Dockerfile
└── README.md
compose.yaml
.env.example
.gitignore
```

`repository.py` contendrá los adaptadores SQL de cada módulo y puede separarse en `infrastructure/` cuando crezca; no es obligatorio crear cuatro archivos vacíos por módulo. `api.py` no instancia `Session` fuera de dependencias, ni llama `repository.py` directamente. Los tests unitarios no requieren PostgreSQL; tests integración/seguridad deben ejecutarse contra PostgreSQL descartable para probar comportamiento real de constraints y transacciones.

## 11. Dependencias prohibidas y reglas de implementación

1. `domain.py` **no** importa FastAPI, SQLAlchemy, `requests/httpx`, env vars ni modelos de otros módulos.
2. `api.py` no modifica SQL directamente, no implementa política de negocio, no hace `commit`.
3. Repositorios no autorizan por sí solos una solicitud: aplican filtro por tenant/seguimiento **derivado de contexto verificado** y casos de uso aplican guardas.
4. No realizar consultas que devuelvan publicaciones A sin filtro de ámbito en el punto de lectura; evitar `get(id)` global + filtrado únicamente en serialización.
5. No regresar ORM models a los esquemas HTTP. DTO de aplicación/representación sin información compartida ajena.
6. No llamar API a sí misma ni abrir transacciones a través de solicitudes HTTP internas.
7. No usar `async def` para sesiones/operaciones SQL síncronas; elegir un modelo de I/O consistente.
8. No desplegar tareas recurrentes, scrapers ni endpoints de demo destructivos públicos.
9. No introducir microservicios, Redis, Celery, Kafka, Kubernetes, event sourcing, CQRS completo ni repositorio genérico sin ADR nuevo.
10. Todo cambio a política de dominio requiere referencia a DEC/ADR/RF y prueba que evidencie el comportamiento.

## 12. Estrategia de calidad y pruebas arquitectónicas

| Clase | Qué verificar | Ejemplo verificable |
|---|---|---|
| Unitarias | Diferencias ACT, reglas/estados, elegibilidad y versión | OBS-001→002 = `{ACT-06}`; OBS fallida no compara |
| Integración PostgreSQL | Constraints, transacciones, unicidad, rollback, migraciones | Dos entregas simultáneas crean una sola novedad |
| API | Login, errores, respuesta mínima, validaciones, versiones | Cuenta B intenta ID de publicación A: no contenido |
| Seguridad | Recursos ajenos, roles, ámbitos, tokens expirados, personaID | Dos cuentas de una persona no permiten aprobar |
| Aceptación | PROTO-AT-01..18 con fixture sintético | Mapeo en `ARCH-TRZ-001.csv` |
| Estructura | Dependencias autorizadas, importaciones circulares, lint y typecheck | Test AST/import-linter para domain no importa infra |
| Operación | DB vacía→migración→seed→API y reinicio | Datos persisten, fixture se restablece solo por acción local explícita |

Recomendación CI: Ruff (lint/format), Pyright o Mypy (elegir uno en INC-00), Pytest y chequeos de dependencias/imports; integración con PostgreSQL desechable. No declarar pruebas ejecutadas: en Fase 2 **solo hay diseño**.

## 13. Amenazas y condiciones no cubiertas (vista preliminar)

| Amenaza / falla | Control arquitectónico previsto | Riesgo pendiente |
|---|---|---|
| BOLA/IDOR entre clientes | Autorizar recurso en aplicación y proyecciones filtradas | Matriz endpoint×acción en SEC-NFR/API |
| `mass assignment` de tenant/actor | Resolver actor/cliente de identidad y relaciones de DB, DTO allowlist | Esquema exacto en API-001 |
| Aprobación indebida | Comparar `personaId` con preparadores congelados | Datos de identidad ficticios confiables solo en demo |
| Race: novedad duplicada | UNIQUE + transacción + retry controlado de conflicto | Claves e índices en DATA |
| Exponer borrador o versión antigua | Referencia vigente solo a versión `Publicada` | Política de reemplazo parcial fuera alcance |
| Publicación visible tras suspensión/finalización | Reevaluación estado/ámbito en lectura | Condición de carrera con cambio concurrente por validar |
| Fallo de adquisición interpretado como silencio | Estados de cobertura y no-comparabilidad explícitos | Integraciones reales no caracterizadas |
| Secretos, tokens y datos en logs | Token digests, logs sanitizados, env secrets | Hardening/operación real no definidos |

## 14. Fronteras entre Fase 2 y fases siguientes

**Queda fijado como diseño candidato:** estilo modular, composición y dependencias, DB única, sincronía, puertos mínimos, operaciones transaccionales, garantía de aislamiento como exigencia, publicación local, despliegue Compose y estrategia de pruebas.

**NO se adelanta al agente:** DDL, constraints exactas, catálogo de endpoints/DTO, formato de credenciales y expiración definitiva, códigos de error, matriz completa de permisos internos, política formal de denegación auditada, dataset JSON definitivo, umbrales no funcionales y scripts completos de CI. Estos se cerrarán en DATA-001, API-001, SEC-NFR-001 y TEST-001.

**Decisiones que deben aceptar los autores antes de implementación:** D1-02, D1-07, D1-08, D1-09/10, DR-F2-01..04 (`DEC-F2-001`), más aceptación de SCOPE/DOMAIN; ninguna selección equivale a ratificación jurídica/organizacional para V1.

## 15. Criterios de salida de Fase 2

- [x] Estilo candidato y alternativas justificados en ADR.
- [x] C4 L1/L2/L3 y secuencia editables.
- [x] Módulos/ownership y reglas de importación explícitos.
- [x] Fronteras transaccionales, idempotencia y concurrencia diseñadas.
- [x] Integraciones externas diferidas con límites seguros.
- [x] Despliegue local y estrategia de pruebas diseñados.
- [x] Trazabilidad de 18 AT y relación con DOM/ADR documentada.
- [ ] Aprobación de autores y decisiones pendientes registrada.
- [ ] Modelo físico de datos y migraciones Fase 3.
- [ ] Contratos y matriz de permisos Fase 4.

**Dictamen:** Fase 2 **preparada para revisión**, suficientemente concreta para comenzar Fase 3, no es un permiso de implementación autónoma integral hasta cerrar Fases 3–5 y decisiones de autores.
