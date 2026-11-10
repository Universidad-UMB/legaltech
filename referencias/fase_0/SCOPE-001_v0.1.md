---
documento: SCOPE-001
version: "0.1-candidata"
fecha: "2026-11-10"
estatus: "Propuesta de alcance técnico para ratificación de autores; NO aprobación organizacional ni especificación de producción"
fuentes:
  - "RF-CAT-001 v0.8"
  - "RF-DEC-001 v0.4"
  - "PROTO-001 v0.1"
  - "TOBE-001 v0.2 y BPMN-01..04"
---

# SCOPE-001 — Fase 0: alcance implementable del backend LegalTech

## 1. Dictamen y objetivo

**Dictamen Fase 0:** alcance **estructurado y propuesto**, apto como entrada a la Fase 1 (modelado del dominio) tras revisión de autores. **NO APTO todavía para entregar una instrucción única de desarrollo integral al agente**; faltan dominio detallado, arquitectura formalizada, modelo de datos, contratos API, RNF y protocolo de pruebas automatizadas.

**Objetivo verificable:** ejecutar localmente un ciclo sintético completo por API y PostgreSQL: registrar un proceso y dos seguimientos independientes, fijar línea base, incorporar observación 2, detectar ACT-06, crear solo NOV-A-001, obtener revisión operativa y jurídica, congelar una publicación v1, aprobarla por persona distinta, publicarla y comprobar acceso de A frente a B y el cierre externo al finalizar A.

**Diferencia con PROTO-001 original:** PROTO-001 v0.1 autorizaba una demostración Vue con estado local y autorización emulada. En esta propuesta se **amplía** a un backend ejecutable con persistencia y autorización aplicada en servidor. Se mantiene el alcance de datos exclusivamente ficticios y la declaración de no estar listo para producción. **Esta ampliación requiere que los autores acepten SCOPE-001**; la aceptación general del stack técnico no ratifica decisiones jurídicas pendientes.

## 2. Decisiones y límites que gobernarán el incremento

| Código | Determinación Fase 0 | Clasificación |
|---|---|---|
| F0-01 | Backend ejecutable, PostgreSQL y API HTTP, no únicamente interfaces de demostración. | Dirección de implementación aceptada en conversación, formalización pendiente en documento |
| F0-02 | Python + FastAPI, SQLAlchemy 2, Alembic, Pytest, Docker Compose como stack de referencia para el incremento. | Selección técnica de trabajo de autores; validar versiones y ADR en Fase 2 |
| F0-03 | Monolito modular con fronteras internas claras. | Candidato; justificar en Fase 2 antes de congelarlo |
| F0-04 | No se conectará a CPNU, SAMAI, Publicaciones Procesales ni proveedor LLM; adaptación fuente `DEMO-FIXTURE`. | Restricción explícita de PROTO-001 |
| F0-05 | Autenticación de identidades de prueba y denegación por recurso implementadas **en backend**, no mero selector de rol frontend. | Nueva decisión técnica propuesta por Fase 0 |
| F0-06 | Borrador y publicación **textuales y locales vía API**, sin PDF ni correo. | Acotación del prototipo; no satisfacer íntegramente RF de PDF de V1 |
| F0-07 | Para la comunicación ficticia se exige abogado, y preparador ≠ aprobador por persona natural. | Salvaguarda de demostración; **DEC-08/09 siguen PR sin adopción definitiva** |
| F0-08 | Solo clave estable ACT-XX en fixture; no afirmar resolución de identidades judiciales ambiguas reales. | Limitación del comparador del prototipo |
| F0-09 | Reinicio de datos vía comando local de desarrollo o seed idempotente, nunca endpoint público de producción. | Diseño de reproducibilidad propuesto |
| F0-10 | Publicar significa que la versión autorizada queda disponible mediante API local protegida y verificable. | Definición de emisión local propuesta |

## 3. Inventario, selección y cobertura

- Catálogo maestro: **150 RF activos candidatos**, de los que **57 están reconstruidos** y pendientes de cotejo histórico; ninguno está formalmente aprobado. Esta cifra de **57 reconstruidos** es independiente de la cifra de **57 RF trazados** para el backend que se indica después.
- Recorrido `PROTO-001 §5.1`: **47 RF seleccionados**, en G01 (2), G02 (5), G03 (3), G04 (11), G05 (9), G08 (1), G09 (9), G10 (7).
- Dependencias habilitantes propuestas en esta Fase 0: **10 RF adicionales** = `RF-V1-001,005,006,008,014,022,041,042,067,114`. No se los declara implementados ni se interpreta que deban cubrirse en toda su amplitud de V1.
- Total de referencias para el incremento: **57 RF únicos = 47 del prototipo + 10 habilitantes**. El detalle fila a fila, con enunciados originales, procedencia, cobertura, casos de prueba y prioridad, está en `TRZ-F0-001_v0.1.csv`.
- Criterios de aceptación diseñados por PROTO-001: **18**, de `PROTO-AT-01` a `PROTO-AT-18`; no ejecutados. Hay que derivar pruebas nuevas de seguridad, concurrencia, errores y persistencia sin confundirlas con AT ya ejecutados.

**Semántica de cobertura:** `R = conducta real, acotada al fixture y flujo`; `P = implementación parcial del RF`; `S = ejecución externa emulada con registro auténtico de su resultado`. Ninguna significa cumplimiento total de V1.

## 4. Capacidades obligatorias de este backend de demostración

### C01. Identidad y aislamiento de la información

- Cuentas internas ficticias para analista, abogado, preparador y coordinador; cuentas externas ficticias A y B.
- Autenticación y autorización **en API**; no tomar cliente_id o rol enviado por cliente HTTP como fuente de autoridad.
- Cuenta externa vinculada a un solo cliente; ámbito explícito por seguimiento; no acceso implícito a toda la cartera (DEC-01/02).
- Acceso denegado por cuenta deshabilitada, cliente suspendido, seguimiento finalizado, falta de ámbito o publicación no disponible; comprobar también accesos directos por ID.
- En la muestra, la identidad única de **persona** permite detectar autoaprobación por cuentas distintas (salvaguarda DEC-09, todavía PR).

### C02. Proceso y seguimiento

- Registrar proceso judicial sintético identificado por radicado `00000000000000000000001` de 23 dígitos; clientes Alfa y Beta con un seguimiento independiente cada uno.
- `SEG-A-001` y `SEG-B-001` comparten identidad judicial pero no línea base, novedades, revisión, versiones, destinatarios ni ámbito externo.
- Activar y finalizar A de forma controlada; la finalización preserva histórico y bloquea acceso externo **sin** cambiar automáticamente publicación Publicada a Retirada (DEC-04).

### C03. Adquisición ficticia y observación

- Registrar petición y ejecución `DEMO-FIXTURE` como operación sintética, sin afirmar consulta a fuentes reales.
- `OBS-001` (2026-10-15) contiene ACT-01..ACT-05; establece línea base de A sin novedad retrospectiva.
- `OBS-002` (2026-10-16) contiene ACT-01..ACT-06 y es comparable con OBS-001 bajo las reglas explícitas del fixture.
- Persistir observaciones y procedencia sin sobrescribir OBS-001; un resultado fallido o incompleto no autoriza una conclusión de «sin cambios».

### C04. Comparación y elegibilidad por seguimiento

- Identidad ficticia de actuación por clave `ACT-XX`; diferencia de conjuntos reproducible.
- Una incorporación ACT-06 persistida con referencia de ambas observaciones; repetición idempotente sin cambio duplicado.
- Determinar elegibilidad de ACT-06 **por seguimiento**, no por proceso global. A es elegible; B puede iniciar línea base sobre OBS-002 y no debe heredar NOV-A-001.
- No deducir ausencia de actuaciones si observación es insuficiente; cualquier identidad ambigua sale a revisión como indeterminada, nunca como coincidencia inventada.

### C05. Novedad y tratamiento humano

- Crear solo NOV-A-001 para A, con unicidad lógica `(seguimiento, cambio)`; repetición de entrega no duplica novedad.
- Analista verifica hechos y escala; abogado ficticio introduce valoración expresa asociada a evidencia; el sistema conserva identidad, hora, decisión y estado.
- La valoración jurídica de la muestra no es dictamen jurídico real; no procesar documentos vía LLM real.

### C06. Publicación y portal

- Preparar borrador textual v1 destinado a A. La versión sometida a autorización queda inmutable; cambiar contenido/destinatario exige nueva versión y autorización.
- Coordinador distinto del preparador por identidad de persona autoriza; autorización no significa todavía Publicada.
- Publicada solo tras registro y disponibilidad efectiva en la API local; B y cuenta A sin ámbito no pueden acceder aun con ID conocido.
- Suspendido (cliente A) y Finalizado (SEG-A-001) bloquean consultas ordinarias de portal sin destruir historiales ni alterar automáticamente estados de publicación.
- El portal diferencia «no hay publicaciones disponibles» de «no existen cambios» y advierte brechas de cobertura.

### C07. Auditoría mínima y reinicio reproducible

- Registrar actor, recurso, operación, instante y resultado de modificaciones del flujo y denegaciones de acceso sensibles, con persistencia de eventos de demostración; no declarar auditoría inviolable ni política de retención definitiva.
- Proporcionar semilla de fixtures y comando de reinicio **solo local** para repetir los 18 casos de prueba sin editar manualmente tablas.

## 5. Fuera del alcance del primer incremento, aunque corresponda al producto V1

Adquisición judicial autorizada real y sus POC; consultas masivas o cron recurrente; OCR independiente (además **excluido de V1** por `RF-V1-078`), extractor nativo independiente y entrenamiento/fine-tuning; proveedor LLM multimodal real; análisis de PDFs; cálculo automático de términos procesales y conclusiones jurídicas autónomas; correos/SMS/WhatsApp; PDF e informes consolidados; cargas masivas; administración completa de usuarios; dashboards analíticos; gestión avanzada de tareas, rectificación jurídica y todas las ramas de máquinas de estados; operación productiva y SLA; microservicios y buses de eventos no justificados.

**No confundir exclusión del incremento con exclusión de V1.** RF-V1-078 sí está excluido de V1; la mayoría de los restantes están diferidos.

## 6. Casos de uso priorizados (backend)

| UC-F0 | Nombre | Actor | Inicio | Éxito mínimo | RF de referencia | Prueba |
|---|---|---|---|---|---|---|
| UC-F0-01 | Autenticar y autorizar operación | Interno / externo | Credenciales de demostración | API rechaza acción ajena y acceso directo por ID | 001, 005, 009, 010, 114 | AT-12,13,17 |
| UC-F0-02 | Gestionar proceso y seguimiento | Interno autorizado | Cliente/proceso ficticios | Dos seguimientos independientes; A activo | 006, 011, 015, 016, 021, 023 | AT-01,02,14 |
| UC-F0-03 | Incorporar y validar observación | Analista | Adquisición fixture | Baseline OBS-001; OBS-002 y resultado persistidos | 028,032,033,040–042,045,046 | AT-03,04,15 |
| UC-F0-04 | Comparar y registrar elegibilidad | Sistema bajo acción autorizada | Dos observaciones comparables | ACT-06, sin duplicados; novedad solo A | 047–050,052–058 | AT-04,05,06 |
| UC-F0-05 | Revisar novedad | Analista / abogado | NOV-A-001 | Escalamiento y valoración con histórico | 059,062,065–069,110 | AT-07,08 |
| UC-F0-06 | Preparar, aprobar, publicar | Preparador / coordinador | Tratamiento revisado | v1 aprobada por otra persona, publicada localmente | 120–122,125–129,134 | AT-09,10,11,18 |
| UC-F0-07 | Consultar portal externo | Cuenta A / B | Identidad y ámbito establecidos | Acceso A condicionado; B denegado; suspensión/finalización | 008–010,021,134,138,140,142–146 | AT-11–15,17 |
| UC-F0-08 | Reiniciar muestra | Desarrollador local | Semilla sintética | Estado y log de prueba reiniciados reproduciblemente | PROTO-001 §6, §9 | AT-16 |

## 7. Invariantes (no negociables dentro de la muestra)

**INV-01** La identidad global de un proceso judicial no determina acceso a novedades de un cliente.

**INV-02** Línea base y elegibilidad de cambio pertenecen a cada seguimiento.

**INV-03** Primera observación comparable no genera novedad histórica automáticamente.

**INV-04** Resultado fallido/incompleto no se representa como observación comparable ni «sin cambios».

**INV-05** Dos ejecuciones equivalentes no producen dos cambios ni dos novedades para el mismo seguimiento/cambio.

**INV-06** Novedad revisada no equivale a versión publicada; autorización no equivale a disponibilidad externa.

**INV-07** El servidor verifica autorización contextual en **cada** solicitud protegida; conocer el ID no confiere acceso.

**INV-08** Al suspender A se preserva B; al finalizar seguimiento A se preserva B y el histórico de A.

**INV-09** Contenido y destinatario aprobados son inmutables; cambios posteriores crean otra versión y aprobación.

**INV-10** Preparador y aprobador son identidades de persona distintas **en la muestra**, bajo DEC-09 todavía propuesto.

**INV-11** No usar datos judiciales reales ni crear una dependencia de servicios judiciales/LLM externos.

**INV-12** Acceso externo solo a la versión vigente Publicada del recurso autorizado; publicación histórica interna puede quedar inaccesible externamente por DEC-04.

## 8. Matriz de aceptación: escenario → prueba → evidencia exigible

| Caso | Verificación principal | Evidencia futura (no ejecutada) |
|---|---|---|
| PROTO-AT-01 | Registrar radicado | Respuesta API + fila de proceso |
| PROTO-AT-02 | Crear seguimiento A y activarlo | Respuesta + vinculación cliente/proceso |
| PROTO-AT-03 | OBS-001 establece línea base sin novedades | Referencia a OBS-001 + contador 0 |
| PROTO-AT-04 | OBS-002 descubre ACT-06 | Diferencia única + referencias |
| PROTO-AT-05 | Idempotencia cambios | Reejecución + mismo ID/cantidad |
| PROTO-AT-06 | Idempotencia novedades | Reentrega + mismo ID/cantidad |
| PROTO-AT-07 | Revisión operativa | Actor analista, motivo, transición |
| PROTO-AT-08 | Valoración jurídica | Actor abogado, evidencia, estado |
| PROTO-AT-09 | Borrador no visible | Versión borrador + rechazo de lectura externa |
| PROTO-AT-10 | Aprobador distinto autoriza | IDs de persona + versión Autorizada |
| PROTO-AT-11 | Publicación efectiva | API de consulta externa A + Publicada |
| PROTO-AT-12 | B bloqueado frente A | Acceso por ID sin fuga de datos |
| PROTO-AT-13 | Cliente suspendido bloqueado | Acceso denegado; publicación no alterada |
| PROTO-AT-14 | Seguimiento finalizado bloqueado | Acceso denegado; histórico interno existente |
| PROTO-AT-15 | Fallo no equivale a sin cambios | Estado de cobertura no verificada |
| PROTO-AT-16 | Reinicio demo | Semilla y estado inicial determinístico |
| PROTO-AT-17 | Misma empresa sin ámbito | Denegación de SEG-A-002 pese a pertenecer a A |
| PROTO-AT-18 | Aprobación no sobrevive modificación | Nuevo ID/versión y nueva aprobación |

**Comprobaciones adicionales obligatorias antes de declarar backend funcional:** autenticación inválida, permiso de rol insuficiente, intento de autoaprobación incluso con dos cuentas de una misma persona, observación no comparable, transiciones inválidas, persistencia tras reinicio del proceso del servidor, comportamiento de errores HTTP y rechazo de datos ajenos en inserciones.

## 9. Definición de listo / Definition of Ready para el agente

Antes de habilitar implementación por agente de un incremento, se debe contar con:

1. Alcance y prioridades del incremento aceptados por los autores, con RF y PROTO-AT identificados.
2. Reglas y transiciones del subconjunto fijadas en `DOMAIN-001`, señalando hipótesis y pendientes.
3. ADR(s) de arquitectura y tecnología, contratos de dependencias y restricciones.
4. Esquema de datos y migraciones planificadas, incluyendo claves de ámbito/tenencia, unicidad e historial.
5. Contrato OpenAPI y política de autorización por operación/recurso.
6. Fixtures sintéticos consistentes, estrategia de reinicio y escenarios positivos/negativos.
7. RNF mínimos y estrategia de pruebas/CI definidos; no exigir cifras de producción no justificadas.
8. Criterios de terminación por incremento: migraciones reproducibles, pruebas automatizadas, README ejecutable, resultado de AT trazable, sin secretos ni datos reales.

**Estado actual:** fase de análisis; se dispone de un SCOPE-001 propuesto y matriz trazable, pero todavía faltan los elementos 2–8. Pasar a Fase 1 **sí**; entregar el proyecto al agente para implementación autónoma integral **todavía no**.

## 10. Estándares y prácticas aplicadas como referencia (no certificaciones)

- **ISO/IEC/IEEE 29148:2018:** atributos, consistencia, trazabilidad y gestión de requisitos (vigente/confirmada según ISO en 2024).
- **ISO/IEC/IEEE 12207:2026:** procesos del ciclo de vida de software; seleccionar prácticas proporcionales al alcance.
- **ISO/IEC 25010:2023:** calidad del producto, especialmente adecuación funcional, seguridad, mantenibilidad y fiabilidad.
- **OWASP ASVS 5.0.0:** verificación de requisitos de seguridad; control de acceso del lado servidor.
- **OpenAPI:** contrato futuro de interfaz (versión y compatibilidad concretas por ADR).
- **BPMN 2.0 y C4:** modelos de procesos existentes y vistas arquitectónicas posteriores; no tratar diagramas como pruebas o diseño ejecutable.

Referencias oficiales:
- https://www.iso.org/standard/72089.html
- https://www.iso.org/standard/90219.html
- https://www.iso.org/standard/78176.html
- https://asvs.owasp.org/
- https://spec.openapis.org/oas/

## 11. Registro de cambios de Fase 0

| Cambio | Motivo | Aprobación pendiente |
|---|---|---|
| Backend funcional y persistente | Objetivo de implementación por agente y demostración de lógica real | Formalizar alcance SCOPE por autores |
| Seguridad de API con cuentas ficticias | Evitar equiparar selector frontend con autorización real | Modelo de identidad Fase 1/4 |
| Publicación textual local | Mantener versión inmutable sin PDF fuera de alcance | Política textual provisional de demostración |
| 10 RF habilitantes | Necesarios para sostener pruebas backend de los 47 RF principales | Revisar coste y prioridad |
| Salvaguardas DEC-08/09 en muestra | Conservar guion de PROTO-001 sin fingir ratificación institucional | Selección de autores y revisión por interesados competentes |

---
**Conclusión:** alcance propuesto **suficiente para iniciar modelado de dominio**, no para codificación integral sin especificaciones adicionales. El inventario detallado está en `TRZ-F0-001_v0.1.csv`; bloqueos y dudas en `DEC-F0-001_v0.1.md` y planificación en `BACKLOG-F0-001_v0.1.md`.
