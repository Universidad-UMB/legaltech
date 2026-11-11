---
documento: RF-CAT-001
proyecto: Plataforma LegalTech de vigilancia de carteras de procesos judiciales
version: "0.8-candidata"
fecha_corte: "2026-11-08"
estado: "En consolidación; sin aprobación formal"
requisitos_activos: 150
requisitos_recuperados: 93
reconstrucciones_pendientes_de_cotejo: 57
requisitos_excluidos: 1
requisitos_absorbidos: 2
casos_aceptacion_diseno: 150
casos_aceptacion_ejecutados: 0
trazabilidad_individual_filas: 150
---

# RF-CAT-001 — Catálogo maestro funcional de la plataforma LegalTech

> **Estado del artefacto v0.8:** versión candidata con 150/150 fichas de aceptación y trazabilidad individual precisada, a falta de ratificación de negocio y cotejo de textos. Contiene 150 requisitos activos, pero **no es una línea base aprobada**. Los 57 enunciados identificados como **RECONSTRUIDO / COTEJO PENDIENTE** son propuestas editoriales basadas en las capacidades acordadas; no se presentan como transcripciones de la formulación original. Los criterios de aceptación son provisionales salvo ratificación por el dominio.

## 1. Identidad, propósito y contexto

Proyecto de grado de Ingeniería de Software en Colombia. Objetivo: apoyar la vigilancia sistemática, trazable y escalable de una cartera de procesos judiciales, desde la adquisición autorizada de información y comparación de observaciones hasta la gestión de novedades, intervención humana, publicación controlada y consulta del cliente.

La tesis académica disponible contiene los capítulos I–III y establece investigación aplicada con DSRM y una secuencia de caracterización → requisitos → arquitectura → desarrollo → verificación/validación. La CPNU se menciona como fuente judicial principal de referencia; no se da por verificada la viabilidad de integración automatizada. Los requisitos detallados provienen de las etapas de conversación G01–G10 y RT-RF-001/002/003, no del contenido literal del documento de tesis.

### 1.1 Restricciones vigentes

- Un proceso judicial puede ser común a varios clientes, pero cada seguimiento conserva su ámbito privado y línea base.
- La adquisición debe utilizar exclusivamente mecanismos habilitados y autorizados; el resultado fallido o incompleto no equivale a ausencia de cambios.
- La comparación y detección judicial es **determinística**, separada de interpretación documental con IA.
- El análisis automatizado de PDF digitales, escaneados e imágenes se realiza **directamente mediante LLM multimodal**; sin OCR independiente, extracción nativa separada ni fine-tuning propio.
- Las propuestas de IA requieren validación humana; el abogado conserva la responsabilidad sobre valoraciones jurídicas.
- Completar una tarea no cierra automáticamente la novedad; cancelar una tarea obligatoria no equivale a cumplirla.
- La publicación exige autorización sobre la **versión exacta**; el PDF final candidato debe existir antes de solicitarla.
- El portal del cliente solo expone datos administrativos permitidos y resultados/documentos efectivamente publicados o habilitados.
- Sin cálculo automático de términos procesales, decisiones jurídicas autónomas ni importación masiva obligatoria en V1.

## 2. Control y cobertura de identificadores

| Grupo | Dominio | IDs | Activos | Enunciado recuperado | Cotejo pendiente |
|---|---|---|---:|---:|---:|
| G01 | Identidad, clientes y autorización | 001–010 | 10 | 3 | 7 |
| G02 | Procesos judiciales y seguimientos | 011–024 | 14 | 4 | 10 |
| G03 | Fuentes y adquisición judicial | 025–039 | 15 | 5 | 10 |
| G04 | Observaciones y detección de cambios | 040–055 | 16 | 6 | 10 |
| G05 | Gestión y rectificación de novedades | 056–070; 153 | 16 | 6 | 10 |
| G06 | Documentos y LLM multimodal | 071–077; 079–090 | 19 | 9 | 10 |
| G07 | Tareas y avisos internos | 091–104 | 14 | 14 | 0 |
| G08 | Expediente, auditoría e indicadores | 105–119 | 15 | 15 | 0 |
| G09 | Publicaciones e informes | 120–137 | 18 | 18 | 0 |
| G10 | Portal del cliente | 138–150 | 13 | 13 | 0 |
| **Total** | | | **150** | **93** | **57** |

### 2.1 IDs no activos

| ID | Estado | Motivo / destino |
|---|---|---|
| RF-V1-078 | EXCLUIDO | OCR independiente. Eliminado expresamente del alcance V1; no reutilizar ID. |
| RF-V1-151 | ABSORBIDO | Su obligación de vigencia/revocación externa se cubre por RF-V1-134, con pruebas de portal conservadas. |
| RF-V1-152 | ABSORBIDO | Auditoría externa se integra en RF-V1-114; consultas de auditoría se rigen por RF-V1-112/113. |

### 2.2 Convenciones de ficha

| Campo | Convención |
|---|---|
| Estado funcional | ACTIVO CANDIDATO; no significa implementado ni aprobado. |
| Recuperación de texto | RECUPERADO EN CONTEXTO o RECONSTRUIDO / COTEJO PENDIENTE. |
| Prioridad G01–G06 | **Por ratificar**, con sugerencia P0 en la reconstrucción cuando aplica; no se presume aprobada. |
| Criterios de aceptación | Criterio inicial asociado al RF. Pendiente de convertir a caso de prueba con precondiciones/datos/pasos/evidencia. |
| Modelo | Máquina de estados o modelo relevante, no necesariamente una traza ya aprobada. |
| CU-29 y CU-30 | Casos de uso propuestos, pendientes de formalización. |

## 3. Catálogo normativo completo por grupo

### G01 — Identidad, clientes y autorización

#### RF-V1-001 — Autenticar usuarios

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado de la formulación original G01 en conversación previa  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Usuario / sistema de autenticación  
**Caso(s) de uso:** CU-01  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá autenticar a los usuarios internos y externos mediante el mecanismo de autenticación configurado, antes de permitirles acceder a funcionalidades protegidas.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Credenciales válidas permiten sesión; credenciales inválidas no conceden acceso.  
**Procedencia:** Formulación original G01 recuperada para RF-V1-001; revisar metadatos y criterios antes de aprobación.  

**AT-V1-001 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Entorno de identidad con cuentas, clientes y políticas de autorización de prueba; todos los actores están identificados y no se utilizan datos personales reales.
- **Datos de entrada:** Usuario interno habilitado y externo habilitado, más identidad inválida.
- **Procedimiento:** Solicitar autenticación con mecanismo configurado en los tres casos.
- **Resultado esperado:** Solo se crean sesiones para identidades válidas; la identidad inválida no accede a recursos protegidos.
- **Evidencia de verificación:** Respuesta de autorización, estado persistido y evento de seguridad/auditoría relevante.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-002 — Gestionar sesiones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Usuario / sistema de autenticación  
**Caso(s) de uso:** CU-01  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá administrar las sesiones de usuarios autenticados y verificar su vigencia antes de permitir operaciones protegidas.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Una sesión vigente permite las operaciones autorizadas; una sesión inválida se rechaza.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-002 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Usuario habilitado con sesión vigente y otra revocada.
- **Datos de entrada:** Token vigente; token revocado.
- **Procedimiento:** Solicitar la misma operación protegida con cada sesión.
- **Resultado esperado:** Se atiende solo la solicitud autorizada con sesión vigente.
- **Evidencia de verificación:** Resultados HTTP, identificador de sesión anonimizado y evento de revocación.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-003 — Recuperar acceso

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Usuario / sistema de autenticación  
**Caso(s) de uso:** CU-01  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir restablecer el acceso a una cuenta mediante un procedimiento controlado que verifique la identidad o legitimidad del solicitante y no revele ni modifique credenciales sin dicha verificación.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** La recuperación autorizada permite restablecer acceso; una solicitud no verificable no altera la cuenta.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-003 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Cuenta existente y canal verificable configurado.
- **Datos de entrada:** Solicitud legítima y solicitud sin prueba de identidad.
- **Procedimiento:** Ejecutar procedimiento de recuperación para ambas.
- **Resultado esperado:** Solo la solicitud verificada puede restablecer acceso; ninguna revela secretos.
- **Evidencia de verificación:** Eventos de recuperación, comprobación de identidad y estado posterior.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-004 — Gestionar usuarios internos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-02  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un administrador autorizado registrar, consultar, actualizar y deshabilitar usuarios internos conservando el historial relevante.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Se puede deshabilitar una cuenta autorizadamente; la cuenta deshabilitada no puede operar.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-004 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Administrador habilitado; usuario interno de prueba.
- **Datos de entrada:** Datos válidos, actualización y orden de deshabilitación.
- **Procedimiento:** Registrar, modificar y deshabilitar el usuario.
- **Resultado esperado:** El usuario mantiene trazabilidad y, deshabilitado, no opera.
- **Evidencia de verificación:** Ficha de usuario, auditoría y respuesta de acceso denegado.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-005 — Administrar roles y permisos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-02  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir asignar y revocar roles y permisos de usuarios mediante operaciones administrativas autorizadas y trazables.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** La revocación de un permiso impide operaciones posteriores que dependan de él.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-005 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos usuarios internos y matriz temporal de permisos.
- **Datos de entrada:** Asignación y revocación de un permiso de revisión.
- **Procedimiento:** Asignar permiso, probar operación, revocarlo y repetir.
- **Resultado esperado:** La operación se permite solo mientras el permiso sea vigente.
- **Evidencia de verificación:** Registro de permisos, decisiones de autorización y eventos.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-006 — Registrar clientes

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-17  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a los responsables autorizados registrar organizaciones cliente con los datos de identificación requeridos y evitar duplicaciones incompatibles con las reglas de negocio.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Se registra un cliente válido; un registro duplicado incompatible se rechaza.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-006 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Esquema de identidad de cliente propuesto.
- **Datos de entrada:** Cliente válido y duplicado conforme a la clave definida.
- **Procedimiento:** Registrar ambos clientes.
- **Resultado esperado:** El registro válido se crea; el duplicado se rechaza según regla ratificada.
- **Evidencia de verificación:** Identificadores, validación de duplicidad y respuesta.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-007 — Gestionar datos de clientes

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-17  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a los responsables autorizados consultar y actualizar los datos administrativos de los clientes sin modificar indebidamente sus historiales de vigilancia.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Un cambio de datos autorizado queda registrado sin alterar decisiones históricas.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-007 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Cliente con historial judicial existente.
- **Datos de entrada:** Cambio permitido de datos administrativos.
- **Procedimiento:** Actualizar ficha de cliente y consultar historial.
- **Resultado esperado:** Datos administrativos se actualizan sin alterar observaciones, decisiones o publicaciones históricas.
- **Evidencia de verificación:** Comparación de ficha e historial y evento de actualización.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-008 — Gestionar estado de cliente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-17  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un administrador autorizado modificar el estado de un cliente, registrar la causa y aplicar las restricciones de acceso y operación previstas en la política vigente, sin modificar automáticamente los estados individuales de sus seguimientos.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** RF-V1-010; política de suspensión y acceso histórico  
**Criterio de aceptación inicial:** Suspender un cliente aplica sus restricciones, sin cambiar masivamente los estados individuales de sus seguimientos.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-008 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Entorno de identidad con cuentas, clientes y políticas de autorización de prueba; todos los actores están identificados y no se utilizan datos personales reales.
- **Datos de entrada:** Cliente A Activo, razón documentada de suspensión; seguimientos Activo y Suspendido.
- **Procedimiento:** Suspender al cliente A con administrador y consultar estado de sus dos seguimientos.
- **Resultado esperado:** Se aplica restricción de cliente y se conserva estado propio de cada seguimiento e historial de causa.
- **Evidencia de verificación:** Respuesta de autorización, estado persistido y evento de seguridad/auditoría relevante.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-009 — Gestionar cuentas externas de clientes

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador autorizado  
**Caso(s) de uso:** CU-17  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir habilitar, consultar y deshabilitar cuentas externas vinculadas a un único cliente en V1, verificando los permisos administrativos y conservando trazabilidad de la vinculación.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** G01: permisos y política de identidad  
**Criterio de aceptación inicial:** Una cuenta externa de V1 no puede operar simultáneamente bajo dos clientes.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-009 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos clientes y operador autorizado para cuentas externas.
- **Datos de entrada:** Cuenta vinculada al cliente A; solicitud de reasociación no permitida a B.
- **Procedimiento:** Consultar ámbito, deshabilitar cuenta e intentar acceso.
- **Resultado esperado:** La cuenta de V1 permanece en un solo cliente y no opera estando deshabilitada.
- **Evidencia de verificación:** Vinculación, decisión de autorización y resultado de inicio de sesión.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-010 — Aplicar autorización contextual

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Servicio de autorización  
**Caso(s) de uso:** CU-01, CU-02, CU-17  
**Modelo(s):** Política de identidad/autorización  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá autorizar o denegar las operaciones protegidas considerando la identidad y estado del usuario, sus permisos, el cliente y recurso involucrados, la operación solicitada y las restricciones del estado vigente del recurso.

**Reglas/invariantes:** Autorización contextual; segregación y estado de cliente  
**Dependencias:** RF-V1-001 a RF-V1-009; matriz de permisos  
**Criterio de aceptación inicial:** Un usuario autorizado realiza la operación; otro usuario sin permiso no accede al recurso aunque conozca su ID.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-010 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Entorno de identidad con cuentas, clientes y políticas de autorización de prueba; todos los actores están identificados y no se utilizan datos personales reales.
- **Datos de entrada:** Usuario de cliente A con permiso de lectura; documento habilitado A; documento restringido B.
- **Procedimiento:** Consultar ambos documentos por sus identificadores directos.
- **Resultado esperado:** Solo documento autorizado A es accesible; consulta de B se deniega sin revelar información privada.
- **Evidencia de verificación:** Respuesta de autorización, estado persistido y evento de seguridad/auditoría relevante.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G02 — Procesos judiciales y seguimientos

#### RF-V1-011 — Registrar procesos judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-03  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un usuario autorizado registrar un proceso judicial mediante su radicado y los metadatos judiciales disponibles, conservando la procedencia de la información.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Proceso con identificación válida se registra con procedencia; datos inválidos se rechazan.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-011 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Usuario autorizado y fuente de datos de prueba.
- **Datos de entrada:** Radicado de 23 dígitos válido y metadatos; caso de identificador inválido.
- **Procedimiento:** Registrar proceso y repetir con dato inválido.
- **Resultado esperado:** Solo se registra el proceso identificable con procedencia.
- **Evidencia de verificación:** Registro de proceso, fuente y error de validación.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-012 — Validar identidad judicial

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-03  
**Modelo(s):** ME-01  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá validar la identidad del proceso judicial mediante el radicado y los atributos de contexto necesarios según las fuentes habilitadas, identificando coincidencias y casos ambiguos antes de confirmar un registro equivalente.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** Radicado y reglas de identidad judicial por fuente  
**Criterio de aceptación inicial:** La identidad ambigua no se fusiona automáticamente con un proceso existente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-012 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Procesos de ejemplo y seguimientos controlados con cliente, responsable y estados iniciales conocidos; decisiones de identidad/suspensión aplicables identificadas.
- **Datos de entrada:** Dos registros con radicado igual y atributos contradictorios de despacho/fuente.
- **Procedimiento:** Registrar segundo proceso y ejecutar validación de equivalencia.
- **Resultado esperado:** El registro se marca ambiguo; no se fusiona automáticamente con el primero.
- **Evidencia de verificación:** Registros de seguimiento antes/después, referencias de línea base y log de transición.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-013 — Consultar proceso judicial

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-03  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar la identificación, metadatos y relaciones disponibles de un proceso judicial.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Se consultan datos autorizados sin exponer seguimientos privados de otros clientes.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-013 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Proceso asociado a seguimientos privados de A y B.
- **Datos de entrada:** Consulta interna desde usuario autorizado solo para A.
- **Procedimiento:** Solicitar ficha general y relaciones del proceso.
- **Resultado esperado:** Se ofrecen metadatos judiciales permitidos sin revelar el seguimiento privado de B.
- **Evidencia de verificación:** Respuesta filtrada y registro de control de acceso.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-014 — Consultar cartera interna

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-04  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar y filtrar la cartera de seguimientos judiciales dentro del ámbito de clientes que les corresponde.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Los filtros y conteos se restringen a seguimientos autorizados.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-014 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Carteras de clientes A y B y analista limitado a A.
- **Datos de entrada:** Filtro por estado y radicado.
- **Procedimiento:** Consultar cartera con filtros.
- **Resultado esperado:** Resultados y contadores incluyen solo seguimientos autorizados de A.
- **Evidencia de verificación:** Parámetros de consulta, IDs retornados y conteos.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-015 — Vincular proceso a cliente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir vincular un proceso judicial existente con un cliente mediante un seguimiento independiente, sin duplicar indebidamente la identidad judicial común.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Un proceso puede tener seguimientos separados de distintos clientes sin compartir sus novedades privadas.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-015 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Proceso X existente y dos clientes autorizados.
- **Datos de entrada:** Solicitud de seguimiento para A y B sobre el mismo radicado.
- **Procedimiento:** Crear seguimientos y registrar una novedad de A.
- **Resultado esperado:** Existe una sola identidad judicial compatible; seguimientos y novedad permanecen separados.
- **Evidencia de verificación:** IDs de proceso, dos seguimientos y permisos de novedad.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-016 — Activar seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir activar un seguimiento pendiente cuando su cliente, proceso, responsables, política y mecanismo de vigilancia cumplan las condiciones vigentes, diferenciando la activación administrativa de la obtención de una primera observación válida.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-017, 018, 023, 026; política de cliente  
**Criterio de aceptación inicial:** La activación administrativa no se presenta como adquisición satisfactoria.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-016 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Procesos de ejemplo y seguimientos controlados con cliente, responsable y estados iniciales conocidos; decisiones de identidad/suspensión aplicables identificadas.
- **Datos de entrada:** Seguimiento Pendiente de cliente habilitado, política válida y ninguna observación todavía.
- **Procedimiento:** Activar seguimiento y consultar estado de cobertura.
- **Resultado esperado:** El seguimiento queda administrativamente Activo sin declarar adquisición ni línea base satisfactoria.
- **Evidencia de verificación:** Registros de seguimiento antes/después, referencias de línea base y log de transición.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-017 — Configurar política de vigilancia

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-06  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir registrar y modificar políticas de vigilancia de seguimientos autorizados, incluyendo su periodicidad, intensidad o condiciones aplicables conforme a parámetros habilitados.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** La política autorizada determina las solicitudes programables de adquisición.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-017 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento elegible y parámetros de política habilitados.
- **Datos de entrada:** Cambio de periodicidad e intensidad permitido.
- **Procedimiento:** Configurar política y generar próximas solicitudes elegibles.
- **Resultado esperado:** La programación refleja la versión de política sin reescribir ejecuciones pasadas.
- **Evidencia de verificación:** Versiones de política y solicitudes calculadas.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-018 — Asignar responsables al seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-19  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un coordinador autorizado designar y modificar responsables operativos y jurídicos del seguimiento, verificando su habilitación y conservando los cambios.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** La reasignación conserva responsable anterior y nuevo.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-018 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento existente y dos responsables internos habilitados.
- **Datos de entrada:** Solicitud de reasignación operativa.
- **Procedimiento:** Reasignar responsable y consultar historial.
- **Resultado esperado:** Se verifica habilitación y se conservan ambos responsables con fecha.
- **Evidencia de verificación:** Historial de asignaciones y control de permisos.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-019 — Suspender seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir suspender un seguimiento mediante una decisión autorizada y justificada, impidiendo nuevas operaciones ordinarias de vigilancia mientras no sea elegible.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Un seguimiento suspendido no origina consultas programadas ordinarias.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-019 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento Activo con programación futura.
- **Datos de entrada:** Solicitud de suspensión autorizada con motivo.
- **Procedimiento:** Suspender y ejecutar planificador.
- **Resultado esperado:** No se inicia vigilancia ordinaria para ese seguimiento suspendido.
- **Evidencia de verificación:** Evento ME-01, motivo y cola de ejecución sin nuevas solicitudes.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-020 — Reactivar seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir reactivar un seguimiento suspendido cuando se satisfagan sus condiciones de elegibilidad, registrando el periodo de suspensión y la necesidad de evaluar la cobertura no observada antes de declarar continuidad de vigilancia.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-019, 023; reglas de cobertura y recuperación  
**Criterio de aceptación inicial:** Reactivar sin cobertura recuperada no declara vigilancia continua.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-020 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Procesos de ejemplo y seguimientos controlados con cliente, responsable y estados iniciales conocidos; decisiones de identidad/suspensión aplicables identificadas.
- **Datos de entrada:** Seguimiento suspendido 4–10 de noviembre con último dato válido anterior.
- **Procedimiento:** Reactivar el seguimiento y consultar intervalo sin cobertura.
- **Resultado esperado:** Se registra la discontinuidad y no se declara vigilancia continua sin datos verificables.
- **Evidencia de verificación:** Registros de seguimiento antes/después, referencias de línea base y log de transición.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-021 — Finalizar seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir finalizar un seguimiento por decisión autorizada, conservando el historial y evitando nuevas adquisiciones ordinarias asociadas a él.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Un seguimiento finalizado conserva historial y no genera nuevas adquisiciones ordinarias.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-021 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento en estado finalizable.
- **Datos de entrada:** Decisión autorizada de finalización.
- **Procedimiento:** Finalizar y solicitar consulta programada posterior.
- **Resultado esperado:** Se conserva historial y no se origina nueva adquisición ordinaria.
- **Evidencia de verificación:** Transición ME-01, historial y registro del planificador.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-022 — Consultar estado y antecedentes del seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Coordinador / analista autorizado  
**Caso(s) de uso:** CU-18  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar el estado actual, historial de transiciones y responsables de un seguimiento judicial.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Se consulta el estado vigente y su historial autorizado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-022 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento con dos transiciones y reasignación.
- **Datos de entrada:** Usuario interno con permiso de consulta.
- **Procedimiento:** Consultar detalle e historial.
- **Resultado esperado:** El estado vigente, responsables y eventos aparecen dentro del ámbito autorizado.
- **Evidencia de verificación:** Respuesta con transiciones, responsables y auditoría.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-023 — Establecer línea base por seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-06  
**Modelo(s):** ME-01  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá establecer y conservar una referencia inicial específica de cada seguimiento, identificando su fecha efectiva, observación utilizada y condiciones de cobertura, sin generar automáticamente novedades correspondientes a antecedentes anteriores a dicha referencia.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-040 a 047; referencia y cobertura comparable  
**Criterio de aceptación inicial:** Las actuaciones de la línea base inicial no originan novedades históricas por defecto.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-023 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Procesos de ejemplo y seguimientos controlados con cliente, responsable y estados iniciales conocidos; decisiones de identidad/suspensión aplicables identificadas.
- **Datos de entrada:** Seguimiento nuevo; primera observación válida con cinco actuaciones previas.
- **Procedimiento:** Establecer línea base inicial y ejecutar evaluación de cambios.
- **Resultado esperado:** La referencia pertenece al seguimiento y las cinco actuaciones iniciales no originan novedades históricas automáticas.
- **Evidencia de verificación:** Registros de seguimiento antes/después, referencias de línea base y log de transición.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-024 — Comprobar cumplimiento de política de vigilancia

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-04, CU-06  
**Modelo(s):** ME-01  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir determinar la condición de cumplimiento de una política de vigilancia mediante registros de programación, adquisiciones y cobertura, diferenciando programación de ejecución satisfactoria.

**Reglas/invariantes:** RG04-19 a RG04-24; seguimiento independiente por cliente  
**Dependencias:** RF-V1-010; seguimiento y política de cliente  
**Criterio de aceptación inicial:** Un seguimiento activo con adquisiciones fallidas no se reporta automáticamente actualizado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-024 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento Activo con dos adquisiciones fallidas y ninguna observación válida reciente.
- **Datos de entrada:** Periodo y política de vigilancia de prueba.
- **Procedimiento:** Calcular cumplimiento y cobertura.
- **Resultado esperado:** Se distingue ejecución programada de adquisición satisfactoria; no indica actualizado.
- **Evidencia de verificación:** Indicadores, entradas, periodo y denominador.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

### G03 — Fuentes y adquisición judicial

#### RF-V1-025 — Registrar fuentes judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador de fuentes  
**Caso(s) de uso:** CU-30 (propuesto)  
**Modelo(s):** ME-07 (mecanismo de fuente, propuesta)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un usuario autorizado registrar fuentes judiciales y sus mecanismos disponibles, conservando su identificación, alcance y estado de habilitación.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-026; RF-V1-027
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Se identifica la fuente y su estado antes de intentar usarla.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-025 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Administrador de fuente autorizado.
- **Datos de entrada:** Datos de fuente, mecanismo y estado inicial no habilitado.
- **Procedimiento:** Registrar fuente y solicitar su uso antes de habilitarla.
- **Resultado esperado:** Fuente queda registrada, pero no se ejecuta consulta sin habilitación.
- **Evidencia de verificación:** Registro de fuente, estado y resultado de bloqueo.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-026 — Habilitar mecanismos por fuente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador de fuentes  
**Caso(s) de uso:** CU-30 (propuesto)  
**Modelo(s):** ME-07 (mecanismo de fuente, propuesta)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir habilitar o deshabilitar mecanismos de adquisición por fuente únicamente conforme a decisiones documentadas de autorización, cobertura y restricciones aplicables, conservando su historial y bloqueando operaciones no habilitadas.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-030
**Dependencias:** Decisión documentada y mecanismo de fuente autorizado  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un mecanismo deshabilitado no ejecuta adquisiciones.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-026 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Fuente simulada o habilitada identificada, con condiciones de uso y política de adquisición configuradas; el caso no acredita acceso real si se usa simulador.
- **Datos de entrada:** Fuente registrada con modalidad no habilitada y expediente permitido de prueba.
- **Procedimiento:** Intentar ejecutar adquisición por modalidad deshabilitada.
- **Resultado esperado:** La operación es bloqueada y se registra motivo y decisión de habilitación aplicable.
- **Evidencia de verificación:** Solicitud e intento de adquisición, resultado clasificado, registro de validación y traza técnica redactada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-027 — Configurar mecanismos de fuente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Administrador de fuentes  
**Caso(s) de uso:** CU-30 (propuesto)  
**Modelo(s):** ME-07 (mecanismo de fuente, propuesta)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir administrar los parámetros técnicos y funcionales autorizados de cada mecanismo de adquisición, incluyendo las modalidades de consulta y restricciones de uso.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-026; RF-V1-030
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un cambio de configuración queda asociado a la versión del mecanismo utilizado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-027 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Fuente habilitada y configuración v1.
- **Datos de entrada:** Parámetros autorizados de nueva modalidad y límites.
- **Procedimiento:** Crear configuración v2 y consultar ejecución asociada a v1.
- **Resultado esperado:** La ejecución previa conserva referencia a v1; nuevas usan versión aplicable.
- **Evidencia de verificación:** Configuraciones versionadas y metadatos de adquisición.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-028 — Solicitar consulta individual

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista o responsable autorizado / sistema  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir solicitar una consulta judicial individual por radicado cuando exista un mecanismo de fuente habilitado y un seguimiento o finalidad autorizada.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-030; RF-V1-032
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una solicitud individual válida puede registrarse; una sin finalidad o fuente elegible se rechaza.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-028 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Seguimiento elegible y mecanismo habilitado.
- **Datos de entrada:** Radicado válido y otro sin finalidad autorizada.
- **Procedimiento:** Solicitar consulta individual para ambos.
- **Resultado esperado:** Se acepta la solicitud elegible y se deniega la no autorizada.
- **Evidencia de verificación:** Solicitudes, decisión de elegibilidad y estado.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-029 — Programar adquisiciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá generar solicitudes de adquisición conforme a las políticas de seguimientos elegibles, respetando la periodicidad configurada, las capacidades de las fuentes y sus condiciones de habilitación vigentes.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-017; RF-V1-030
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** No se programan consultas fuera de políticas elegibles o fuente habilitada.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-029 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Fuente simulada o habilitada identificada, con condiciones de uso y política de adquisición configuradas; el caso no acredita acceso real si se usa simulador.
- **Datos de entrada:** Dos seguimientos: uno activo/elegible y otro suspendido; fuente habilitada.
- **Procedimiento:** Ejecutar programación de adquisiciones en una ventana configurada.
- **Resultado esperado:** Solo se crean solicitudes permitidas para seguimientos elegibles y dentro de la política.
- **Evidencia de verificación:** Solicitud e intento de adquisición, resultado clasificado, registro de validación y traza técnica redactada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-030 — Validar elegibilidad de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá comprobar antes de cada intento de adquisición la habilitación de la fuente, compatibilidad de la operación, parámetros requeridos, restricciones de uso y elegibilidad del seguimiento o solicitud asociada.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-026; INV-RF-03
**Dependencias:** RF-V1-016, 017, 026, 029; factibilidad de fuente  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Se bloquea el intento cuando la fuente no está habilitada o el seguimiento no es elegible.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-030 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Fuente simulada o habilitada identificada, con condiciones de uso y política de adquisición configuradas; el caso no acredita acceso real si se usa simulador.
- **Datos de entrada:** Adquisición programada; fuente deshabilitada y seguimiento activo.
- **Procedimiento:** Intentar iniciar adquisición y revisar validación previa.
- **Resultado esperado:** Se bloquea el intento antes de contactar fuente y se registra causa.
- **Evidencia de verificación:** Solicitud e intento de adquisición, resultado clasificado, registro de validación y traza técnica redactada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-031 — Ejecutar adquisición judicial

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá ejecutar adquisiciones mediante mecanismos autorizados y habilitados, conservar la procedencia del resultado y registrar las condiciones de operación correspondientes.

**Reglas/invariantes y referencias precisadas v0.8:** DG03-02; RF-V1-030; RF-V1-039
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La ejecución válida registra la fuente y resultado; ninguna operación usa mecanismos no autorizados.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-031 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Conector simulado habilitado bajo contrato de prueba.
- **Datos de entrada:** Respuesta válida con procedencia y respuesta fallida.
- **Procedimiento:** Ejecutar solicitudes individuales y almacenar resultados.
- **Resultado esperado:** Cada ejecución registra fuente y estado real sin atribuir integración real a la simulación.
- **Evidencia de verificación:** Contrato simulado, solicitud/respuesta, fuente y resultado.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-032 — Clasificar resultados de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá clasificar los resultados de adquisición conforme a ME-02, diferenciando respuestas exitosas, incompletas, sin coincidencia verificable, fallidas, bloqueadas y canceladas, sin inferir inexistencia judicial o ausencia de cambios a partir de resultados insuficientes.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-03; RF-V1-042; RF-V1-143
**Dependencias:** ME-02; contrato de resultado de adquisición  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una consulta fallida no se clasifica como proceso sin actuaciones.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-032 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Fuente simulada o habilitada identificada, con condiciones de uso y política de adquisición configuradas; el caso no acredita acceso real si se usa simulador.
- **Datos de entrada:** Respuestas simuladas completa, incompleta, fallida y sin coincidencia.
- **Procedimiento:** Clasificar cada resultado mediante ME-02.
- **Resultado esperado:** Las categorías quedan diferenciadas; fallida o incompleta no equivale a ausencia de cambios judiciales.
- **Evidencia de verificación:** Solicitud e intento de adquisición, resultado clasificado, registro de validación y traza técnica redactada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-033 — Registrar intentos y resultados

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar cada intento de adquisición con identificador, fuente, solicitud, instantes relevantes, resultado y referencias a los seguimientos autorizados asociados cuando corresponda, sin asumir una relación exclusiva con un único cliente.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-039; RF-V1-110
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Los reintentos pueden reconstruirse sin sobrescribir el intento original.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-033 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos seguimientos elegibles y adquisición compartible.
- **Datos de entrada:** Una consulta de fuente, dos seguimientos y un reintento.
- **Procedimiento:** Registrar intento e identificar asociaciones permitidas.
- **Resultado esperado:** Se conserva un intento histórico y referencias múltiples sin exponer datos privados.
- **Evidencia de verificación:** IDs de intento, seguimientos permitidos, marcas temporales.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-034 — Gestionar reintentos de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir reintentos controlados de adquisiciones fallidas cuando la política y la fuente lo permitan, evitando resultados duplicados y conservando el historial de intentos.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-033; RF-V1-039; RF-V1-053
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un reintento no crea observaciones duplicadas por el mismo resultado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-034 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Adquisición fallida con reintento autorizado.
- **Datos de entrada:** Misma solicitud y resultado técnico repetido.
- **Procedimiento:** Ejecutar reintento controlado.
- **Resultado esperado:** Los intentos se conservan, sin duplicación de observación idéntica.
- **Evidencia de verificación:** Dos intentos, clave de idempotencia y observaciones resultantes.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-035 — Gestionar errores de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar errores y restricciones detectados durante una adquisición y proporcionar información suficiente para diagnóstico y tratamiento autorizado.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-03; RF-V1-032; RF-V1-038
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un fallo registra su causa y no produce un resultado exitoso aparente.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-035 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Fuente simulada con error conocido.
- **Datos de entrada:** Error temporal y resultado parcial.
- **Procedimiento:** Ejecutar adquisición.
- **Resultado esperado:** Se registra causa, restricción y estado correspondiente sin éxito ficticio.
- **Evidencia de verificación:** Incidencia, diagnóstico sin secretos y clasificación ME-02.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-036 — Incorporar información manual

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista o responsable autorizado / sistema  
**Caso(s) de uso:** CU-05, CU-28  
**Modelo(s):** Incorporación manual G03 y ME-02 (solo trazabilidad; no resultado automático)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir incorporar información judicial mediante un procedimiento manual autorizado, registrando su procedencia, responsable y condición de verificación, sin presentarla como resultado de una adquisición automatizada.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-041; RF-V1-042; RF-V1-110
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una observación manual conserva responsable y tipo de procedencia manual.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-036 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Fuente simulada o habilitada identificada, con condiciones de uso y política de adquisición configuradas; el caso no acredita acceso real si se usa simulador.
- **Datos de entrada:** Archivo de observación aportado por analista autorizado y fecha/procedencia manual.
- **Procedimiento:** Incorporar información al expediente y consultar origen.
- **Resultado esperado:** Queda identificada como incorporación manual, sin etiquetarse como adquisición automática real.
- **Evidencia de verificación:** Solicitud e intento de adquisición, resultado clasificado, registro de validación y traza técnica redactada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-037 — Consultar ejecuciones de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista o responsable autorizado / sistema  
**Caso(s) de uso:** CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar el estado, resultado e intentos de las adquisiciones pertinentes a sus seguimientos, sin exponer solicitudes ni tratamientos privados de otros clientes que compartan información judicial de origen.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-010; RF-V1-114
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La consulta muestra el resultado real y sus errores si existen.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-037 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Una adquisición técnicamente compartida por seguimientos A y B.
- **Datos de entrada:** Operador habilitado solo para A.
- **Procedimiento:** Consultar detalles e intentos relacionados.
- **Resultado esperado:** Se presentan datos autorizados, sin revelar solicitudes o tratamientos exclusivos de B.
- **Evidencia de verificación:** Salida filtrada, ámbitos autorizados y registro de auditoría.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-038 — Registrar y atender incidencias de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista o responsable autorizado / sistema  
**Caso(s) de uso:** CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir registrar incidencias de adquisición, asociarlas a ejecuciones o fuentes afectadas y conservar su estado de tratamiento.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-035; RF-V1-111; RF-V1-115
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una incidencia se relaciona con la ejecución afectada y puede consultarse hasta su resolución.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-038 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Adquisición con fallo y operador autorizado.
- **Datos de entrada:** Incidencia nueva con estado inicial y resolución.
- **Procedimiento:** Registrar incidencia, cambiar estado y consultar historial.
- **Resultado esperado:** Incidencia vinculada a ejecución/fuente y con evolución trazable.
- **Evidencia de verificación:** Ticket, estados, ejecución y actor responsable.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-039 — Conservar trazabilidad de adquisición

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de adquisición  
**Caso(s) de uso:** CU-28  
**Modelo(s):** ME-02 (adquisición)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá relacionar las adquisiciones con su fuente, configuración, solicitud, evidencias y seguimientos autorizados asociados cuando correspondan, conservando referencias de auditoría sin atribuir la adquisición de forma exclusiva a un único cliente.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-033; RF-V1-041
**Dependencias:** Fuente habilitada; G02 y ME-02  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una observación puede rastrearse hasta la adquisición que la originó.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-039 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Resultado de adquisición usado por A y B cuando esté permitido.
- **Datos de entrada:** Identificadores de solicitud, fuente, configuración y observación.
- **Procedimiento:** Navegar trazabilidad desde observación hasta origen.
- **Resultado esperado:** Se reconstruye procedencia y múltiples asociaciones permitidas sin atribución única falsa.
- **Evidencia de verificación:** Cadena de IDs y referencias de fuente/versión.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

### G04 — Observaciones y detección de cambios

#### RF-V1-040 — Registrar observaciones judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar las observaciones judiciales obtenidas de adquisiciones válidas, vinculándolas con el proceso y la fuente correspondiente.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-031; RF-V1-041; RG04-17
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La observación conserva proceso y procedencia de origen.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-040 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Adquisición válida con respuesta completa.
- **Datos de entrada:** Resultado judicial y proceso identificable.
- **Procedimiento:** Registrar observación.
- **Resultado esperado:** Observación persistida con proceso y fuente, sin duplicar por reintento equivalente.
- **Evidencia de verificación:** Observación, adquisición asociada y marcas temporales.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-041 — Conservar procedencia de observaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar la procedencia y las referencias originales disponibles de cada observación, distinguiendo datos judiciales obtenidos de tratamientos internos.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-040; RF-V1-045
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una observación puede rastrearse a su fuente original o incorporación manual.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-041 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Observación de fuente y registro de revisión interna.
- **Datos de entrada:** Referencia original, modalidad y actor de incorporación.
- **Procedimiento:** Consultar procedencia de observación.
- **Resultado esperado:** Se distingue información obtenida de fuente de tratamiento manual posterior.
- **Evidencia de verificación:** Metadatos de procedencia, referencia a evidencia y auditoría.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-042 — Evaluar calidad y cobertura de observación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá evaluar la suficiencia, identidad, integridad y cobertura de cada observación conforme a su modalidad de origen, registrando las condiciones que impidan utilizarla en una comparación determinada.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RG04-23; INV-RF-03
**Dependencias:** RF-V1-031, 032, 040; esquema de cobertura  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una observación incompleta queda marcada como no apta para la comparación incompatible.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-042 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Observación incompleta y observación completa sobre la misma fuente.
- **Procedimiento:** Evaluar identidad, integridad y cobertura de ambas.
- **Resultado esperado:** La incompleta se registra con limitación y no se utiliza en comparación que exija cobertura completa.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-043 — Normalizar representaciones judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá normalizar los datos judiciales mediante reglas identificables y conservando sus valores de origen, a fin de facilitar comparaciones reproducibles.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RF-V1-041; RF-V1-047
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Las normalizaciones no borran el valor fuente y pueden reproducirse.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-043 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Reglas de normalización versionadas.
- **Datos de entrada:** Valor judicial original con variación de formato.
- **Procedimiento:** Normalizar en dos ejecuciones iguales.
- **Resultado esperado:** Resultado reproducible y original inalterado.
- **Evidencia de verificación:** Valor original, versión de regla y salida normalizada.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-044 — Identificar actuaciones judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá identificar las actuaciones u otros registros comparables contenidos en una observación, vinculándolos con el proceso, fuente y evidencia correspondiente.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RF-V1-048
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Cada actuación reconocida conserva referencia a su observación.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-044 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Observación judicial con dos actuaciones.
- **Datos de entrada:** Datos de identidad y evidencia de cada actuación.
- **Procedimiento:** Identificar registros de actuación.
- **Resultado esperado:** Cada actuación mantiene relación con observación, proceso, fuente y evidencia.
- **Evidencia de verificación:** Actuaciones y referencias observacionales.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-045 — Conservar historial inmutable de observaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema de observaciones / responsable autorizado  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar el historial de observaciones sucesivas sin sobrescribirlas mediante actualizaciones ordinarias, para permitir reconstruir sus diferencias en el tiempo.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-040; RF-V1-046; RF-V1-106
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una segunda observación no elimina la anterior.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-045 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Proceso con observación anterior válida.
- **Datos de entrada:** Nueva observación posterior distinta.
- **Procedimiento:** Registrar y consultar ambas.
- **Resultado esperado:** La observación anterior permanece y puede compararse.
- **Evidencia de verificación:** IDs inmutables, contenido de ambas y secuencia temporal.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-046 — Establecer referencia técnica

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá establecer una referencia técnica inicial para un conjunto de observaciones compatibles cuando no exista una referencia previa válida, sin clasificar sus antecedentes iniciales como nuevas actuaciones detectadas.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-18; RF-V1-045; INV-RF-04
**Dependencias:** RF-V1-042, 045; reglas de comparabilidad  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La primera observación comparable crea referencia y no novedades retrospectivas.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-046 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Primera observación comparable de proceso sin referencia técnica.
- **Procedimiento:** Crear referencia inicial y ejecutar detector de diferencias.
- **Resultado esperado:** Se registra referencia sin producir novedades por las actuaciones preexistentes.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-047 — Verificar comparabilidad

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-07  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá verificar la compatibilidad de las observaciones en identidad judicial, modalidad, fuente, cobertura, temporalidad y reglas de transformación antes de compararlas, identificando expresamente los casos no comparables.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RG04-23; RF-V1-042
**Dependencias:** RF-V1-042, 043, 044; fuente y cobertura  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Observaciones con cobertura incompatible no producen un resultado de ausencia de cambios.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-047 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Observaciones con el mismo radicado pero coberturas de fuentes distintas e incompatibles.
- **Procedimiento:** Solicitar comparación entre ambas.
- **Resultado esperado:** Se declara no comparable y no se concluye que no hubo cambios.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-048 — Determinar identidad de actuaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá evaluar mediante reglas determinísticas la correspondencia entre actuaciones de observaciones comparables, distinguiendo coincidencias verificables de identidades ambiguas.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RF-V1-044; RF-V1-047
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Actuaciones ambiguas no se fusionan automáticamente como iguales.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-048 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos observaciones compatibles con identidades coincidentes y ambiguas.
- **Datos de entrada:** Actuaciones con campos insuficientes en un caso.
- **Procedimiento:** Aplicar reglas de correspondencia.
- **Resultado esperado:** Las coincidencias verificables se vinculan; la identidad ambigua no se fusiona automáticamente.
- **Evidencia de verificación:** Resultado por actuación y versión de reglas determinísticas.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-049 — Comparar observaciones sucesivas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá comparar de manera determinística observaciones judiciales compatibles para obtener diferencias identificables y reproducibles.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RG04-23; RF-V1-047
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Con entradas equivalentes se obtiene el mismo resultado de diferencias.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-049 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos observaciones comparables con referencia válida.
- **Datos de entrada:** Mismo par de entradas en dos ejecuciones.
- **Procedimiento:** Comparar ambas veces.
- **Resultado esperado:** Se obtiene idéntico conjunto de diferencias con el mismo algoritmo y configuración.
- **Evidencia de verificación:** Entradas, versión del comparador y resultados reproducibles.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-050 — Detectar incorporaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá identificar incorporaciones de actuaciones judiciales mediante reglas determinísticas y correspondencias suficientemente verificadas, conservando su fecha judicial y primera detección e identificando la incertidumbre de los registros retrospectivos.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-21; RG04-23; RF-V1-048
**Dependencias:** RF-V1-047, 048, 049; evidencias de identidad  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una actuación retrospectiva se distingue de una nueva actuación judicial del periodo.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-050 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Actuación detectada el 8 de noviembre con fecha judicial del 30 de octubre.
- **Procedimiento:** Comparar con observación anterior y clasificar incorporación.
- **Resultado esperado:** Se conserva fecha judicial y primera detección diferenciadas; no se presenta automáticamente como actuación nueva del periodo.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-051 — Detectar modificaciones entre observaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá distinguir las modificaciones verificables de registros judiciales previamente conocidos respecto a las incorporaciones realmente nuevas, conforme a las reglas de comparación.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-17; RG04-21; RF-V1-049
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Una corrección de metadatos no se contabiliza como actuación nueva sin evidencia.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-051 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Observaciones con una actuación nueva y una corrección de metadatos.
- **Datos de entrada:** Par de estados judiciales sintéticos.
- **Procedimiento:** Comparar registros.
- **Resultado esperado:** Se distinguen incorporación y modificación sin contar la modificación como actuación nueva.
- **Evidencia de verificación:** Tipos de diferencia y evidencia comparada.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-052 — Registrar diferencias detectadas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar los cambios detectados con referencias a las observaciones comparadas, el tipo de diferencia y la evidencia que sustenta su identificación.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-045; RF-V1-049; RF-V1-108
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Toda diferencia puede rastrearse a las observaciones que la produjeron.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-052 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Comparador produce una incorporación verificable.
- **Datos de entrada:** Referencias de observaciones anterior y posterior.
- **Procedimiento:** Persistir cambio detectado.
- **Resultado esperado:** El cambio identifica tipo, origen, destino y evidencia.
- **Evidencia de verificación:** Registro de cambio y referencias originales.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-053 — Evitar duplicación de cambios

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá impedir que el reprocesamiento equivalente de observaciones genere cambios duplicados, conservando una identidad estable o relación idempotente del resultado.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-048; RF-V1-052; RF-V1-058
**Dependencias:** G03; observaciones y reglas determinísticas  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Repetir comparación equivalente no agrega un cambio duplicado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-053 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Comparación de observaciones idénticas previamente ejecutada.
- **Datos de entrada:** Reprocesamiento con misma identidad de datos y reglas.
- **Procedimiento:** Ejecutar comparación otra vez.
- **Resultado esperado:** No se crea segundo registro lógico de cambio equivalente.
- **Evidencia de verificación:** Clave idempotente y recuento antes/después.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-054 — Evaluar elegibilidad por seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de elegibilidad G04 por ME-01 (seguimiento) y salida hacia ME-03
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá determinar la elegibilidad de cada cambio respecto a cada seguimiento, considerando su línea base, periodo efectivo, estado, cobertura y condiciones de temporalidad, sin atribuirle automáticamente antecedentes históricos no elegibles.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-19; RG04-20; RG04-22; RG04-23; RG04-24
**Dependencias:** RF-V1-023, 046, 047, 050; estado del seguimiento  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Dos clientes con distintas líneas base pueden obtener distinta elegibilidad.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-054 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Mismo cambio técnico; seguimiento A iniciado antes y B iniciado después de la actuación.
- **Procedimiento:** Evaluar elegibilidad del cambio para A y B.
- **Resultado esperado:** Las decisiones de elegibilidad se calculan por seguimiento y pueden diferir de forma justificada.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-055 — Entregar cambios elegibles a G05

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Motor determinístico / sistema  
**Caso(s) de uso:** CU-08  
**Modelo(s):** Modelo de elegibilidad G04 por ME-01 (seguimiento) y salida hacia ME-03
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar y entregar a G05 los cambios cuya elegibilidad para un seguimiento haya sido determinada, conservando su evidencia y evitando entregas duplicadas, sin tratar resultados indeterminados como novedades confirmadas.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-23; RG04-24; RF-V1-054; RF-V1-058
**Dependencias:** RF-V1-053, 054; idempotencia G05  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La entrega repetida no crea una nueva novedad equivalente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-055 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Dos o más observaciones controladas con identidad, procedencia, cobertura y diferencias esperadas definidas mediante datos de referencia.
- **Datos de entrada:** Cambio elegible para A y cambio temporalmente indeterminado para B.
- **Procedimiento:** Enviar resultados al gestor de novedades y repetir entrega elegible.
- **Resultado esperado:** Solo el elegible crea entrada tratable; la repetición no duplica y el indeterminado conserva limitación.
- **Evidencia de verificación:** Observaciones de referencia, salida del comparador, razones de comparabilidad y registro de cambios.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G05 — Gestión y rectificación de novedades

#### RF-V1-056 — Crear novedad candidata

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar una novedad candidata a partir de un cambio elegible para un seguimiento, conservando su referencia técnica de origen.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Un cambio elegible origina una candidata vinculada al seguimiento correcto.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-056 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Cambio elegible para seguimiento A.
- **Datos de entrada:** Evento de cambio validado por G04.
- **Procedimiento:** Crear novedad candidata.
- **Resultado esperado:** La novedad se asocia con A y referencia el cambio sin declararse conclusión jurídica.
- **Evidencia de verificación:** ID de novedad, seguimiento y cambio.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-057 — Asociar novedad y seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá vincular cada novedad con un seguimiento y cliente identificables, conservando la relación con el cambio y la evidencia judicial correspondiente.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Dos seguimientos del mismo proceso no comparten automáticamente novedades privadas.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-057 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Proceso compartido por A y B.
- **Datos de entrada:** Cambio de fuente y seguimientos de dos clientes.
- **Procedimiento:** Crear o consultar relaciones de novedad.
- **Resultado esperado:** La novedad de A no queda vinculada automáticamente como novedad privada de B.
- **Evidencia de verificación:** Relaciones cliente-seguimiento-novedad y pruebas de acceso.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-058 — Evitar duplicación de novedades

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá impedir que entregas repetidas de un mismo cambio elegible creen novedades equivalentes duplicadas dentro del mismo seguimiento.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Reprocesar una entrega ya consumida no duplica la novedad.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-058 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad previa creada desde cambio elegible.
- **Datos de entrada:** Entrega repetida del mismo cambio para el mismo seguimiento.
- **Procedimiento:** Consumir dos veces el evento.
- **Resultado esperado:** Existe una novedad lógica única para ese seguimiento y cambio.
- **Evidencia de verificación:** Clave idempotente y registros de consumo.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-059 — Iniciar revisión operativa

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a analistas autorizados iniciar y registrar la revisión operativa de novedades pendientes dentro de su ámbito.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Una novedad pendiente puede pasar a revisión solo por un actor autorizado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-059 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad Pendiente de revisión operativa y analista habilitado.
- **Datos de entrada:** Petición de iniciar revisión y otra por usuario ajeno.
- **Procedimiento:** Aplicar ambas transiciones.
- **Resultado esperado:** Solo el analista autorizado inicia revisión y deja registro de responsable.
- **Evidencia de verificación:** Estados ME-03, permisos y evento.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-060 — Asignar responsables de novedades

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al coordinador autorizado asignar o reasignar responsables de revisión de novedades, conservando los cambios y verificando su habilitación.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** La reasignación conserva responsable anterior y nuevo.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-060 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad con analista asignado y otro habilitado.
- **Datos de entrada:** Solicitud de reasignación por coordinador.
- **Procedimiento:** Reasignar y consultar historial.
- **Resultado esperado:** Responsables anterior y nuevo quedan auditados.
- **Evidencia de verificación:** Historial de responsables y operación.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-061 — Consultar novedades para revisión

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a los usuarios internos autorizados consultar novedades, estado, prioridad y evidencias relevantes de los seguimientos bajo su responsabilidad.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Un analista consulta solo las novedades autorizadas.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-061 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Dos clientes con novedades y analista limitado a A.
- **Datos de entrada:** Filtro de estado/prioridad.
- **Procedimiento:** Consultar bandeja de revisión.
- **Resultado esperado:** Solo aparecen novedades y evidencias dentro del ámbito A.
- **Evidencia de verificación:** Respuesta filtrada, IDs y actor autorizado.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-062 — Clasificar revisión operativa

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al analista autorizado clasificar el resultado de una revisión operativa, distinguiendo confirmación de hechos verificables, información insuficiente, necesidad de valoración jurídica, falsos positivos y duplicados, conservando la decisión y su evidencia.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** RF-V1-056, 057; política de revisión operativa  
**Criterio de aceptación inicial:** La revisión diferencia hallazgo válido, duplicado y falta de información.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-062 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedades válidas, duplicadas y con evidencia incompleta.
- **Procedimiento:** Clasificar cada una como analista autorizado y guardar su resultado.
- **Resultado esperado:** Quedan categorías, justificaciones y evidencia diferenciadas, sin confirmar las incompletas.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-063 — Registrar observaciones de revisión

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir registrar comentarios, evidencias y resultados de la revisión operativa de una novedad conservando autor y secuencia histórica.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Una revisión deja evidencia y autor sin sobrescribir decisiones anteriores.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-063 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad En revisión operativa.
- **Datos de entrada:** Comentario, evidencia y resultado de analista.
- **Procedimiento:** Registrar revisión y consultar historial.
- **Resultado esperado:** Autor, momento, resultado y evidencia se conservan sin sobrescribir revisiones anteriores.
- **Evidencia de verificación:** Registro de revisión y secuencia de eventos.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-064 — Descartar novedad justificadamente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir descartar una novedad cuando un responsable autorizado registre una causa válida y una justificación verificable, conservando el cambio de origen y el historial de revisión sin eliminarlos.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** RF-V1-067, 068, 153; reglas de descarte  
**Criterio de aceptación inicial:** Descartar requiere motivo; no elimina la observación o diferencia original.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-064 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedad con evidencia de falso positivo y otra sin justificación.
- **Procedimiento:** Solicitar descarte autorizado en ambos casos.
- **Resultado esperado:** Solo el descarte justificado se registra y ninguna acción elimina la evidencia de origen.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-065 — Escalar novedad a revisión jurídica

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Analista / coordinador autorizado  
**Caso(s) de uso:** CU-10  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir derivar una novedad a un abogado habilitado cuando su contenido o tratamiento requiera valoración jurídica, conservando la causa y el responsable del escalamiento.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Una derivación jurídica identifica abogado y motivo.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-065 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad con contenido que requiere criterio jurídico.
- **Datos de entrada:** Motivo de escalamiento y abogado elegible.
- **Procedimiento:** Derivar novedad a abogado.
- **Resultado esperado:** La escalación registra motivo, destinatario y estado, sin validación jurídica automática.
- **Evidencia de verificación:** Transición ME-03, responsable y motivo.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-066 — Registrar valoración jurídica

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Abogado habilitado  
**Caso(s) de uso:** CU-10  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al abogado autorizado registrar una valoración jurídica sobre una novedad, identificando la evidencia examinada, el resultado profesional y las acciones o aclaraciones necesarias, sin confundirla con la validación de campos generados mediante IA.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** RF-V1-065; revisión jurídica y evidencia  
**Criterio de aceptación inicial:** Una valoración jurídica exige abogado habilitado y referencia a evidencia.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-066 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedad que requiere interpretación; usuario abogado y analista.
- **Procedimiento:** Intentar registrar valoración con ambos roles.
- **Resultado esperado:** Solo el abogado habilitado registra valoración con referencias a evidencia y traza de responsable.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-067 — Conservar historial de decisiones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar el historial de revisiones, valoraciones y decisiones sobre novedades, con su responsable, fecha y referencias de evidencia.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Las decisiones anteriores siguen disponibles tras una corrección.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-067 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad con revisión y valoración registrada.
- **Datos de entrada:** Corrección autorizada de decisión.
- **Procedimiento:** Registrar decisión correctiva y consultar historia.
- **Resultado esperado:** La versión anterior sigue disponible y se ve la nueva relación.
- **Evidencia de verificación:** Decisiones con autor, fecha y referencias de evidencia.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-068 — Controlar estados de novedad

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá aplicar las transiciones de ME-03 verificando el estado, permisos, responsables y guardas vigentes, e impedir modificaciones ordinarias que contradigan decisiones terminales o el historial del tratamiento.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** ME-03; criterios de transición  
**Criterio de aceptación inicial:** Una transición inválida se rechaza y no borra el historial.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-068 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedad Cerrada con historia y solicitud de transición ordinaria a En revisión.
- **Procedimiento:** Solicitar transición no permitida por ME-03.
- **Resultado esperado:** La transición se rechaza sin modificar estado ni suprimir historia.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-069 — Definir tratamiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir registrar un tratamiento de novedad con acciones, responsables y seguimiento requerido cuando corresponda, conservando la decisión y su sustento.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** G04; G01 y ME-03  
**Criterio de aceptación inicial:** Cada tratamiento identifica resultado y acciones requeridas, si las hay.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-069 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Novedad con revisión suficiente.
- **Datos de entrada:** Tratamiento y tareas necesarias.
- **Procedimiento:** Registrar decisión de tratamiento.
- **Resultado esperado:** Se conserva decisión, evidencia, responsables y acciones requeridas.
- **Evidencia de verificación:** Tratamiento registrado, vínculos y actor.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-070 — Cerrar novedad

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09  
**Modelo(s):** ME-03  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir cerrar una novedad cuando exista un tratamiento documentado, se hayan completado las revisiones obligatorias y las acciones requeridas estén satisfechas o cuenten con una excepción de cierre autorizada y justificada.

**Reglas/invariantes:** ME-03; frontera analista–abogado; decisiones trazables  
**Dependencias:** RF-V1-069, 101; revisiones obligatorias  
**Criterio de aceptación inicial:** Una tarea obligatoria pendiente bloquea el cierre ordinario.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-070 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedad con tratamiento y tarea obligatoria pendiente; segunda con obligación satisfecha.
- **Procedimiento:** Intentar cerrar ambas novedades.
- **Resultado esperado:** La primera no se cierra; segunda puede cerrarse si también cumple todas las guardas.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-153 — Rectificar decisiones sobre novedades

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0 (propuesto)  
**Actor/responsable:** Sistema / responsable autorizado  
**Caso(s) de uso:** CU-09, CU-10, CU-21  
**Modelo(s):** ME-03 (rectificación vinculada) y ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un responsable autorizado registrar una rectificación relacionada con una novedad previamente cerrada, descartada o sometida a una decisión definitiva, conservando la decisión original, la nueva evidencia, el motivo y el responsable, e identificando las tareas, valoraciones y publicaciones que requieran revisión como consecuencia de la rectificación.

**Reglas/invariantes:** Decisiones correctivas no sobrescribibles; RG09-09 a RG09-12  
**Dependencias:** RF-V1-064, 067, 070, 132, 133; política de rectificación  
**Criterio de aceptación inicial:** Rectificación preserva decisión original, registra motivo y vincula efectos en publicaciones y tareas.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-153 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Seguimiento y novedad de laboratorio con cambios y evidencia de origen, permisos y condiciones de revisión definidas.
- **Datos de entrada:** Novedad descartada con decisión histórica y publicación asociada.
- **Procedimiento:** Registrar rectificación con nueva evidencia y responsable.
- **Resultado esperado:** Se conserva decisión original y se señalan publicaciones/tareas afectadas sin reescribir contenidos autorizados.
- **Evidencia de verificación:** Historial de novedad, decisión, permisos, evidencia asociada y transiciones ME-03.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G06 — Documentos y LLM multimodal

#### RF-V1-071 — Incorporar documentos judiciales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir incorporar documentos judiciales desde fuentes o procedimientos autorizados, conservando su referencia de origen y el contexto de adquisición.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** El documento incorporado conserva procedencia y contexto.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-071 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Documento de fuente o carga manual permitida.
- **Datos de entrada:** PDF documental y referencia de origen.
- **Procedimiento:** Incorporar documento.
- **Resultado esperado:** Se conserva documento y origen; no se publica automáticamente.
- **Evidencia de verificación:** ID documental, fuente/usuario y copia original.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-072 — Verificar procedencia documental

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá comprobar que la incorporación de un documento proviene de una fuente o acción autorizada y registrar su condición de procedencia.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Un documento sin procedencia autorizada no pasa inadvertidamente a procesamiento.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-072 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Documento nuevo con y sin procedencia habilitada.
- **Datos de entrada:** Referencias de fuente confiable y origen desconocido.
- **Procedimiento:** Intentar incorporaciones.
- **Resultado esperado:** La procedencia se comprueba y se marca/bloquea la entrada no verificada según política.
- **Evidencia de verificación:** Resultado de validación, origen y estado de custodia.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-073 — Validar condiciones técnicas del documento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá validar las condiciones técnicas del archivo necesarias para su custodia y presentación, incluyendo formato, tamaño e integridad técnica, registrando incompatibilidades sin ejecutar reconocimiento de texto ni interpretación de su contenido.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Un archivo corrupto o formato no admitido queda identificado sin extraer su contenido.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-073 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Política técnica de archivo definida.
- **Datos de entrada:** PDF íntegro y archivo corrupto.
- **Procedimiento:** Validar formato, tamaño e integridad sin interpretar contenido.
- **Resultado esperado:** Se acepta solo archivo técnicamente apto; no ocurre OCR ni extracción de texto.
- **Evidencia de verificación:** Registro de validaciones técnicas y ausencia de trabajos OCR.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-074 — Asociar documento al expediente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá relacionar cada documento con el proceso, seguimiento, actuación o novedad correspondiente, según los datos autorizados disponibles.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Una relación documental no expone automáticamente el archivo a otros clientes.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-074 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Proceso de A y documento relacionado con actuación.
- **Datos de entrada:** Solicitud de asociación válida y acceso desde B.
- **Procedimiento:** Relacionar documento y consultar como B.
- **Resultado esperado:** La asociación se conserva y no crea por sí sola permiso para B.
- **Evidencia de verificación:** Relaciones documento-recurso y denegación por ámbito.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-075 — Conservar integridad documental

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar el documento original y sus versiones o referencias necesarias, impidiendo sustituciones ordinarias silenciosas y permitiendo verificar su integridad.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** El documento original permanece referenciable después de generar una propuesta de IA.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-075 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Documento original almacenado.
- **Datos de entrada:** Solicitud de procesamiento IA y nueva referencia de versión.
- **Procedimiento:** Procesar y consultar documento original.
- **Resultado esperado:** Original permanece íntegro, verificable y separable del resultado derivado.
- **Evidencia de verificación:** Documento original, identificadores y comprobante de integridad.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-076 — Controlar acceso a documentos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-12  
**Modelo(s):** Gestión documental  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá verificar la autorización contextual para consultar, procesar, presentar o descargar documentos judiciales según usuario, recurso y finalidad.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Un usuario sin permiso de documento no lo descarga por URL directa.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-076 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Documento restringido a A y usuarios de A y B.
- **Datos de entrada:** URL de descarga y solicitud de procesamiento externo.
- **Procedimiento:** Intentar operaciones con identidades distintas.
- **Resultado esperado:** Se autoriza según usuario, recurso y finalidad; B no descarga ni procesa.
- **Evidencia de verificación:** Decisiones de autorización y registros de acceso.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-077 — Solicitar procesamiento multimodal

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir solicitar el procesamiento de documentos PDF digitales, escaneados o imágenes admitidas mediante un LLM multimodal, sin requerir componentes independientes de OCR o extracción de texto nativo.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-079, 081, 082; POC LLM y autorización  
**Criterio de aceptación inicial:** Un PDF escaneado se analiza por el LLM habilitado sin OCR independiente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-077 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** PDF digital válido y PDF escaneado compatible; proveedor multimodal habilitado.
- **Procedimiento:** Solicitar procesamiento de ambos documentos.
- **Resultado esperado:** Las solicitudes se atienden por LLM multimodal y no requieren motor OCR independiente.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-079 — Verificar compatibilidad de modelo

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá verificar la compatibilidad del archivo con los formatos, límites y modalidades de entrada admitidos por el modelo habilitado antes de iniciar su procesamiento.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** Proveedor y tipos documentales habilitados  
**Criterio de aceptación inicial:** El sistema no invoca el modelo con una entrada incompatible.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-079 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** PDF excede tamaño admitido y PDF compatible.
- **Procedimiento:** Validar cada entrada contra restricciones configuradas del proveedor.
- **Resultado esperado:** Solo la compatible puede continuar a la solicitud de procesamiento.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-080 — Conservar referencias de evidencia documental

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar las referencias que vinculan los datos propuestos por el LLM con el documento original y sus evidencias documentales disponibles, diferenciando referencias verificadas de aquellas no comprobables.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-075, 083, 084; referencias de evidencia  
**Criterio de aceptación inicial:** Las referencias no verificables no se presentan como evidencia confirmada.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-080 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Propuesta LLM con campo y referencia de página verificable; segundo campo sin evidencia.
- **Procedimiento:** Registrar propuesta y consultar referencias.
- **Resultado esperado:** Se vinculan los campos al original y se identifica la evidencia no verificable sin presentarla como confirmada.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-081 — Autorizar tratamiento externo

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá verificar la habilitación del proveedor, la finalidad y las condiciones aplicables al tratamiento documental antes de transmitir información a un servicio externo de IA, bloqueando las operaciones no autorizadas.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** Política de tratamiento de datos; proveedor habilitado  
**Criterio de aceptación inicial:** Si falta habilitación no se transmite el archivo al proveedor.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-081 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Proveedor multimodal sin habilitación para finalidad solicitada y documento restringido.
- **Procedimiento:** Intentar transmitir documento al proveedor.
- **Resultado esperado:** Se bloquea el envío y se registra la falta de habilitación sin transmitir datos.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-082 — Ejecutar procesamiento con LLM

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá ejecutar las solicitudes documentales elegibles mediante un LLM multimodal habilitado, utilizando una configuración identificable y registrando el proveedor, modelo y resultado de la operación.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-077, 079, 081; proveedor multimodal  
**Criterio de aceptación inicial:** El procesamiento conserva identificadores de modelo y configuración.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-082 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Documento compatible, proveedor autorizado y configuración identificada.
- **Procedimiento:** Ejecutar una invocación controlada y consultar registro técnico.
- **Resultado esperado:** Se preservan identificador de ejecución, proveedor, modelo, configuración y resultado.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-083 — Obtener propuesta estructurada

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá solicitar al LLM propuestas estructuradas conforme al esquema definido para el tipo documental, admitiendo campos no identificados y evitando tratar valores sin evidencia suficiente como datos confirmados.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-082; esquema de propuesta  
**Criterio de aceptación inicial:** Un campo no encontrado puede representarse sin fabricar valor.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-083 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Documento sin uno de los campos requeridos por el esquema.
- **Procedimiento:** Solicitar propuesta estructurada al LLM.
- **Resultado esperado:** El campo no encontrado queda sin valor confirmado y la respuesta conserva su estructura esperada.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-084 — Validar estructura de respuesta

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá validar la estructura, los tipos de datos y las referencias de evidencia técnicamente comprobables de cada respuesta del LLM antes de admitirla como propuesta pendiente de revisión humana.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-083; validación técnica, no jurídica  
**Criterio de aceptación inicial:** Respuesta con estructura inválida no se convierte en propuesta utilizable.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-084 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Respuestas LLM una válida y otra con tipos incorrectos y referencias ausentes.
- **Procedimiento:** Validar las dos respuestas contra esquema y evidencia comprobable.
- **Resultado esperado:** Solo la estructuralmente válida se admite como propuesta pendiente de revisión humana.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-085 — Registrar trazabilidad de propuesta IA

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar la relación entre documento, solicitud, modelo, configuración, propuesta, intentos y validaciones humanas conforme a la política de auditoría y retención.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Una corrección puede rastrearse a la propuesta y documento originales.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-085 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Documento con propuesta de IA y corrección humana.
- **Datos de entrada:** Identificadores de ejecución, modelo y propuesta.
- **Procedimiento:** Consultar cadena de procedencia.
- **Resultado esperado:** Se reconstruyen versión, propuesta, validación y resultado sin volcar secretos a registros.
- **Evidencia de verificación:** Trazas de documentos, modelo/configuración y validación.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-086 — Gestionar fallos multimodales

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-13  
**Modelo(s):** ME-04A  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar los fallos del procesamiento multimodal y permitir continuar con la revisión humana del documento original, sin ejecutar automáticamente un motor alternativo de OCR o extracción de texto nativo.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** ME-04A; RF-V1-075, 088  
**Criterio de aceptación inicial:** Fallos no activan OCR y el documento original sigue disponible para revisión.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-086 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Error simulado de proveedor durante procesamiento PDF.
- **Procedimiento:** Ejecutar solicitud y consultar alternativa de trabajo.
- **Resultado esperado:** Se registra Fallida, documento original sigue disponible y no se ejecuta OCR alternativo.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-087 — Asignar validación humana

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Abogado habilitado  
**Caso(s) de uso:** CU-14  
**Modelo(s):** ME-04B  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir asignar a un abogado habilitado la revisión de una propuesta multimodal y conservar su estado y responsable.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** G01; documentos autorizados; revisión humana  
**Criterio de aceptación inicial:** Una propuesta pendiente puede asignarse a abogado autorizado.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-087 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Propuesta multimodal Pendiente y dos abogados.
- **Datos de entrada:** Asignación a abogado habilitado y otra a usuario no autorizado.
- **Procedimiento:** Solicitar ambas asignaciones.
- **Resultado esperado:** Solo se permite asignación al abogado habilitado.
- **Evidencia de verificación:** Asignaciones, roles y estado ME-04B.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-088 — Revisar original y propuesta

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Abogado habilitado  
**Caso(s) de uso:** CU-14  
**Modelo(s):** ME-04B  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al abogado autorizado revisar el documento original junto con los campos propuestos por el LLM, sus referencias de evidencia y sus condiciones de verificación.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-080, 083, 087  
**Criterio de aceptación inicial:** El abogado consulta original y propuesta simultáneamente, sin texto OCR independiente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-088 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Documento de prueba autorizado (sintético salvo habilitación), proveedor simulado o aprobado, políticas de custodia y validación definidas.
- **Datos de entrada:** Abogado autorizado y documento con propuesta no validada.
- **Procedimiento:** Abrir tarea de revisión y consultar original junto a propuesta.
- **Resultado esperado:** Se pueden contrastar campos con documento original; los no verificados no aparecen confirmados.
- **Evidencia de verificación:** Documento original de prueba, solicitud/respuesta controlada, estado ME-04 y revisión humana registrada.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-089 — Confirmar, corregir o rechazar propuesta

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Abogado habilitado  
**Caso(s) de uso:** CU-14  
**Modelo(s):** ME-04B  
**Aprobación:** Candidato condicionado  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al abogado autorizado confirmar, corregir, rechazar o solicitar aclaración de los datos propuestos, registrando su decisión y conservando la propuesta original.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-088; condiciones de revisión humana  
**Criterio de aceptación inicial:** Una corrección conserva valor anterior, valor validado y responsable.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-089 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Propuesta multimodal con un campo erróneo.
- **Datos de entrada:** Corrección del dato y justificación jurídica/documental.
- **Procedimiento:** Corregir y confirmar propuesta.
- **Resultado esperado:** Se conserva propuesta original y valor validado con responsable.
- **Evidencia de verificación:** Original, corrección, autor y estado de revisión.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

#### RF-V1-090 — Entregar datos validados al tratamiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** **RECONSTRUIDO — COTEJO LITERAL PENDIENTE**  
**Prioridad:** Por ratificar (P0 sugerida)  
**Actor/responsable:** Sistema documental / responsable autorizado  
**Caso(s) de uso:** CU-14  
**Modelo(s):** ME-04B  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir poner a disposición del tratamiento de novedades los resultados documentales validados por el responsable humano, sin publicarlos automáticamente al cliente.

**Reglas/invariantes:** DG06-01; sin OCR/extracción nativa independientes; validación humana  
**Dependencias:** RF-V1-089; G05; sin autopublicación  
**Criterio de aceptación inicial:** Solo datos validados se exponen a G05; no existe autopublicación.  
**Procedencia:** Reconstrucción editorial v0.4; literalidad pendiente de cotejo.

**AT-V1-090 — Caso de aceptación propuesto (sin ejecución ni validación de dominio)**

- **Precondiciones:** Resultado documental validado y otra propuesta pendiente.
- **Datos de entrada:** Dos conjuntos de datos y solicitud de entrega a G05.
- **Procedimiento:** Solicitar transferencia al tratamiento.
- **Resultado esperado:** Solo los validados se entregan; ninguna transferencia produce publicación automática.
- **Evidencia de verificación:** Registro de validación, contrato G05 y ausencia de publicación.
- **Estado:** diseñado de forma preliminar; pendiente de datos definitivos y aprobación.

### G07 — Tareas y avisos internos

#### RF-V1-091 — Crear tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios autorizados crear tareas relacionadas con una novedad y su seguimiento, cuando el estado de revisión o tratamiento permita la acción, sin exigir que toda tarea se origine después de finalizar la valoración jurídica.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** RF-V1-057; ME-03 / ME-06  
**Criterio de aceptación inicial:** La tarea se crea para novedad elegible; una novedad cerrada no admite alta ordinaria.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-091 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Novedad En revisión y novedad Cerrada; analista habilitado.
- **Procedimiento:** Intentar crear tarea ordinaria en ambos contextos.
- **Resultado esperado:** Se crea tarea vinculada a la primera y se bloquea alta ordinaria en novedad terminal.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-092 — Vincular tareas al seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá relacionar cada tarea con su novedad de origen y el seguimiento correspondiente, conservando el contexto de cliente y evitando asociaciones con recursos no autorizados.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** La tarea conserva seguimiento y novedad; no se asocia al seguimiento privado de otro cliente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-092 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Dos seguimientos del mismo proceso pertenecientes a clientes distintos.
- **Procedimiento:** Crear tarea de novedad de A y forzar asociación con seguimiento de B.
- **Resultado esperado:** Se conserva la relación correcta novedad-seguimiento-cliente y se rechaza asociación cruzada.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-093 — Asignar y reasignar tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador / responsable autorizado  
**Caso(s) de uso:** CU-15, CU-19  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al coordinador autorizado, o al usuario con permiso de asignación delegado, designar y cambiar responsables de tareas, verificando la habilitación del destinatario y conservando el historial.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Reasignación guarda responsables anterior y nuevo y verifica permisos.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-093 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea asignada a analista A, candidato B habilitado y candidato C sin autorización.
- **Procedimiento:** Reasignar de A a B y luego intentar hacerlo a C.
- **Resultado esperado:** Se acepta B, rechaza C y queda historial de reasignaciones.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-094 — Definir prioridad y planificación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador / responsable autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir establecer prioridad, obligatoriedad y fecha objetivo de una tarea mediante una operación autorizada, identificando dicha fecha como administrativa y sin calcular automáticamente términos procesales.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** Política de fecha objetivo y obligatoriedad  
**Criterio de aceptación inicial:** Una fecha objetivo se identifica como administrativa, no como término procesal automático.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-094 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea elegible con fecha objetivo administrativa y prioridad Alta.
- **Procedimiento:** Guardar prioridad, obligatoriedad y fecha; consultar presentación.
- **Resultado esperado:** Se muestran como atributos de tarea y la fecha no se etiqueta como plazo procesal.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-095 — Modificar tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios autorizados modificar los atributos editables de una tarea, conservando el historial de los cambios relevantes y evitando alteraciones no permitidas de su identidad y origen.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Un cambio de prioridad deja historial; el origen de la tarea no puede cambiarse libremente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-095 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea En curso con prioridad editable; intento de cambiar novedad de origen.
- **Procedimiento:** Editar prioridad y luego intentar alterar vínculo de origen.
- **Resultado esperado:** Solo se permite atributo editable y se registra historia sin cambiar identidad de tarea.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-096 — Controlar estados de tarea

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de tareas y avisos  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá aplicar las transiciones válidas de ME-06, verificando el estado vigente, la autorización del usuario y las condiciones de cada operación.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Una transición válida se aplica; una inválida se rechaza.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-096 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea Pendiente y transición a Completada sin paso permitido; transición Pendiente a En curso.
- **Procedimiento:** Solicitar ambas transiciones.
- **Resultado esperado:** Se rechaza transición inválida y se permite transición autorizada por ME-06.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-097 — Gestionar bloqueos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir registrar, consultar y resolver impedimentos que bloqueen una tarea, conservando el motivo, responsable y resultado de su resolución.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Bloquear exige motivo y resolver conserva causa original.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-097 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea En curso que presenta impedimento y descripción verificable.
- **Procedimiento:** Bloquear, registrar causa y resolver bloqueo con actor autorizado.
- **Resultado esperado:** Se conservan motivo, responsable y resolución en el historial.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-098 — Completar tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al responsable autorizado marcar una tarea como Completada únicamente cuando registre el resultado y las evidencias obligatorias establecidas para dicha actividad.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** No completa sin resultado ni evidencia obligatoria.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-098 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea que requiere evidencia; primer cierre sin evidencia y segundo con evidencia válida.
- **Procedimiento:** Solicitar completar en ambas condiciones.
- **Resultado esperado:** No se completa sin prueba requerida; con prueba se registra resultado y pasa a Completada.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-099 — Cancelar tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador / responsable autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir cancelar una tarea no terminal mediante una decisión autorizada y justificada, conservando su historial y diferenciando la cancelación del cumplimiento de la obligación que la originó.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** RF-V1-101; ME-06  
**Criterio de aceptación inicial:** Cancelar registra motivo y no satisface automáticamente una obligación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-099 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea En curso y tarea Completada, con motivo de cancelación.
- **Procedimiento:** Solicitar cancelación en ambas.
- **Resultado esperado:** Solo la no terminal se cancela con justificación; obligación subyacente no se declara satisfecha.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-100 — Consultar tareas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar y filtrar tareas según su seguimiento, novedad, responsable, estado, prioridad y fechas disponibles, respetando los permisos sobre cada recurso.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Solo aparecen tareas autorizadas y filtros no revelan conteos de otros clientes.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-100 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tareas de dos clientes y filtros por responsable, prioridad, estado.
- **Procedimiento:** Consultar listado bajo un usuario con acceso a uno de los ámbitos.
- **Resultado esperado:** Filtros trabajan solo con tareas autorizadas y no revelan la cartera ajena.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-101 — Controlar condiciones de cierre

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de tareas y avisos  
**Caso(s) de uso:** CU-15, CU-09  
**Modelo(s):** ME-06  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá informar a G05 las condiciones de cumplimiento de las tareas obligatorias relacionadas con una novedad, distinguiendo actividades completadas, pendientes, bloqueadas, canceladas o sustituidas y sus excepciones autorizadas.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** RF-V1-070; tareas obligatorias  
**Criterio de aceptación inicial:** Una tarea obligatoria cancelada no se trata automáticamente como ejecutada.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-101 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Novedad con tarea obligatoria cancelada y tarea sustituta pendiente.
- **Procedimiento:** Solicitar evaluación de condiciones de cierre.
- **Resultado esperado:** La obligación sigue abierta hasta completarse o justificarse excepción autorizada.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-102 — Generar avisos internos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Sistema de tareas y avisos  
**Caso(s) de uso:** CU-15  
**Modelo(s):** Eventos de avisos internos  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá generar avisos dentro de la plataforma ante eventos configurados de asignación, reasignación o cambio relevante de tareas, identificando el destinatario y el recurso que originó el evento.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Nueva asignación genera aviso interno al responsable pertinente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-102 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Evento de reasignación de tarea para nuevo responsable.
- **Procedimiento:** Reasignar y consultar bandeja de avisos.
- **Resultado esperado:** Se genera aviso interno vinculado a la tarea y dirigido al responsable correcto.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-103 — Informar condiciones de atención

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Sistema de tareas y avisos  
**Caso(s) de uso:** CU-15  
**Modelo(s):** Eventos de avisos internos  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá identificar tareas bloqueadas o pendientes respecto a sus fechas objetivo y generar avisos internos a los responsables autorizados según las reglas de aviso configuradas, sin calcular términos procesales judiciales.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Tarea atrasada frente a su fecha administrativa produce aviso sin afirmar vencimiento procesal.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-103 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Tarea vencida según fecha objetivo administrativa y tarea bloqueada.
- **Procedimiento:** Ejecutar evaluación de avisos configurados.
- **Resultado esperado:** Se identifican pendientes/bloqueos y se emiten avisos sin calcular términos procesales.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-104 — Consultar y gestionar avisos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-15  
**Modelo(s):** Eventos de avisos internos  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a cada usuario autenticado consultar sus avisos internos, identificar cuáles han sido leídos y acceder al recurso relacionado cuando conserve autorización para ello.

**Reglas/invariantes:** RG07-01 a RG07-14; ME-06  
**Dependencias:** G05; G01; ME-06  
**Criterio de aceptación inicial:** Marcar leído funciona; aviso antiguo no permite abrir un recurso cuyo permiso fue revocado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-104 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Novedad y seguimiento controlados, tareas iniciales, roles y reglas de transición ME-06 configurados.
- **Datos de entrada:** Usuario A con aviso propio y aviso de B.
- **Procedimiento:** Consultar y marcar leído un aviso propio; intentar abrir aviso de B.
- **Resultado esperado:** Se gestiona aviso propio; no se concede acceso a aviso o recurso ajeno.
- **Evidencia de verificación:** Registro de tarea antes/después, eventos ME-06 y evidencias de cumplimiento/aviso.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G08 — Expediente, auditoría e indicadores

#### RF-V1-105 — Consultar expediente consolidado

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-11  
**Modelo(s):** ME-01, ME-03 y ME-05 (consulta consolidada)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a los usuarios internos autorizados consultar una vista consolidada de la información correspondiente a un seguimiento judicial, incluyendo sus datos generales, observaciones, novedades, documentos, revisiones y tareas accesibles.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-010; RF-V1-108
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Muestra secciones autorizadas sin mezclar trabajo privado de seguimientos de otros clientes.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-105 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Seguimiento autorizado con observaciones, novedades, documentos y tareas.
- **Procedimiento:** Abrir expediente consolidado con usuario interno habilitado.
- **Resultado esperado:** Se muestran componentes accesibles sin mezclar contextos privados de otros seguimientos.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-106 — Consultar historial de observaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-07, CU-11  
**Modelo(s):** ME-02 y observaciones de G04 (histórico)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir consultar las observaciones judiciales registradas para un proceso o seguimiento autorizado, identificando su fuente, fechas, cobertura, resultado de adquisición y condiciones de comparación.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-03; RF-V1-040; RF-V1-045
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** El historial conserva procedencia y resultados; fallo no se muestra como observación válida.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-106 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Proceso con observación válida, adquisición fallida posterior y fecha de cobertura.
- **Procedimiento:** Consultar historial de observaciones del proceso.
- **Resultado esperado:** Se diferencian observaciones válidas, fallos e integridad de su procedencia.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-107 — Consultar cronología del seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-11  
**Modelo(s):** ME-01, ME-02, ME-03 y ME-05 (secuencia histórica)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá presentar una secuencia temporal de los eventos relevantes de un seguimiento, diferenciando las fechas judiciales de las fechas de adquisición, detección y tratamiento interno.

**Reglas/invariantes y referencias precisadas v0.8:** RG04-21; RF-V1-020; RF-V1-067
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Fechas judiciales y operativas aparecen diferenciadas.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-107 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Seguimiento con actuación judicial, adquisición, detección y valoración en días diferentes.
- **Procedimiento:** Abrir cronología del seguimiento.
- **Resultado esperado:** Se muestran fechas con su significado, sin sustituir fecha judicial por fecha técnica.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-108 — Consultar relaciones y evidencias

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-11  
**Modelo(s):** ME-03, ME-04B y ME-05 (relaciones de evidencia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir navegar desde una novedad, actuación o decisión hacia las observaciones, documentos y evidencias relacionados, comprobando las autorizaciones correspondientes a cada recurso.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-010; RF-V1-041; RF-V1-074; RF-V1-080
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La evidencia se abre solo si el usuario cuenta con permiso específico.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-108 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Novedad publicada con observación y anexo habilitado; anexo restringido.
- **Procedimiento:** Navegar desde novedad hacia evidencias y documentos.
- **Resultado esperado:** Se preservan relaciones de origen y se deniega acceso al anexo restringido.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-109 — Buscar y filtrar expediente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-11  
**Modelo(s):** ME-01 y ME-03 (consulta por ámbito; no cambio de estados)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir localizar información autorizada dentro del expediente de seguimiento utilizando criterios estructurados disponibles, sin revelar registros ajenos al ámbito del usuario.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-010; RF-V1-105
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Búsquedas y conteos se restringen al seguimiento autorizado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-109 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Expedientes de A y B, filtros radicado, fecha y estado.
- **Procedimiento:** Buscar expediente con usuario autorizado solo para A.
- **Resultado esperado:** Se devuelven registros de A que satisfacen filtros, no registros privados de B.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-110 — Registrar auditoría operativa

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de auditoría  
**Caso(s) de uso:** CU-16  
**Modelo(s):** ME-01, ME-02, ME-03, ME-05 y ME-06 (eventos operativos)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar los eventos relevantes que modifiquen el estado, la responsabilidad o los resultados de los procesos de negocio, identificando la operación, recurso, actor, fecha y resultado.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-067; RF-V1-113; RF-V1-131
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Transición de novedad registra actor, recurso y resultado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-110 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Cambio de estado de novedad por actor autorizado.
- **Procedimiento:** Ejecutar transición y examinar auditoría operativa.
- **Resultado esperado:** Se registra actor, operación, objeto, marca temporal y resultado.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-111 — Registrar eventos técnicos y de seguridad

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de auditoría  
**Caso(s) de uso:** CU-16  
**Modelo(s):** ME-02, ME-04A y ME-05 (eventos técnicos)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar eventos relevantes de autenticación, autorización, administración técnica, integraciones y fallos, incluyendo la información necesaria para su diagnóstico sin exponer secretos o datos innecesarios.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-002; RF-V1-035; RF-V1-113
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un acceso denegado se registra sin contraseñas ni tokens.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-111 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Adquisición fallida por error de red y denegación de acceso.
- **Procedimiento:** Provocar ambos eventos controlados y revisar logs.
- **Resultado esperado:** Se registran eventos técnicos y de seguridad con referencias correlacionables sin exponer secretos.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-112 — Consultar auditoría

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario interno autorizado  
**Caso(s) de uso:** CU-16  
**Modelo(s):** Modelo de auditoría G08 (consulta de eventos; sin ME propia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios expresamente autorizados consultar y filtrar registros de auditoría dentro de su ámbito técnico u operativo, sin conceder capacidad de modificación de los eventos históricos.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-010; RF-V1-113
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un auditor autorizado consulta eventos; un usuario ajeno recibe denegación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-112 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Coordinador con permiso de consulta de auditoría y cliente externo.
- **Procedimiento:** Solicitar consulta de registros con ambos usuarios.
- **Resultado esperado:** Solo actor habilitado consulta registros permitidos; externo no accede.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-113 — Conservar trazabilidad e integridad de auditoría

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de auditoría  
**Caso(s) de uso:** CU-16  
**Modelo(s):** Modelo de auditoría G08 (integridad de eventos; sin ME propia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar los eventos de auditoría con información suficiente para reconstruir su contexto y secuencia, impedir su modificación mediante operaciones ordinarias y aplicar mecanismos de detección de alteraciones conforme a la política de integridad y retención vigente.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-110; RF-V1-111; RF-V1-114
**Dependencias:** RF-V1-110, 111; política de integridad y retención  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Un evento conserva correlación y no admite edición ordinaria.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-113 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Evento de auditoría persistido e intento de edición ordinaria.
- **Procedimiento:** Solicitar modificación por interfaz ordinaria y revisar historial.
- **Resultado esperado:** La edición se impide o detecta según política; se preserva rastro íntegro.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-114 — Auditar accesos sensibles

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de auditoría  
**Caso(s) de uso:** CU-16  
**Modelo(s):** Modelo de auditoría G08 (accesos sensibles; sin ME propia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar las operaciones internas y externas de acceso, consulta o descarga definidas como sensibles, incluyendo los intentos denegados cuando corresponda, identificando actor, recurso, operación, fecha y resultado conforme a la política de auditoría.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-010; RF-V1-113; RF-V1-148
**Dependencias:** RF-V1-010, 110, 111, 112; absorbe RF-V1-152  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Descarga de documento externo se audita según política; acceso indebido queda denegado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-114 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Descarga protegida por A e intento denegado a B sobre mismo recurso.
- **Procedimiento:** Realizar ambas solicitudes y consultar auditoría.
- **Resultado esperado:** Se registra acceso sensible y denegación según política, con actores y recursos correctos.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-115 — Consultar panel operativo

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Coordinador / usuario interno autorizado  
**Caso(s) de uso:** CU-04  
**Modelo(s):** ME-01, ME-02, ME-03 y ME-06 (agregación)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al coordinador y a otros usuarios internos autorizados consultar un panel con indicadores de vigilancia y trabajo operativo, restringidos a los clientes y seguimientos de su ámbito.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-010; RF-V1-116; RF-V1-117
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Coordinador observa exclusivamente indicadores de su cartera.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-115 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Coordinador con seguimientos A autorizados y otros seguimientos B.
- **Procedimiento:** Abrir panel de operación.
- **Resultado esperado:** Solo se muestran indicadores del ámbito autorizado y su fecha de corte.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-116 — Calcular indicadores de vigilancia

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador / usuario interno autorizado  
**Caso(s) de uso:** CU-04  
**Modelo(s):** ME-01, ME-02 y modelo de cobertura G04
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá calcular indicadores de adquisición y cobertura a partir de los estados y observaciones verificables, diferenciando seguimientos activos, actualizados, sin línea base y con incidencias, sin interpretar resultados fallidos o incompletos como cobertura satisfactoria.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-02; INV-RF-03; RF-V1-023; RF-V1-042
**Dependencias:** RF-V1-024, 032, 042, 046; definiciones de cobertura  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Seguimiento activo sin línea base no se contabiliza como actualizado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-116 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Dos seguimientos Activo: uno con observación vigente y otro sin línea base.
- **Procedimiento:** Calcular indicadores de adquisición y cobertura.
- **Resultado esperado:** Solo el primero puede contar como actualizado; se registra denominador y criterio.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-117 — Calcular indicadores de tratamiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Coordinador / usuario interno autorizado  
**Caso(s) de uso:** CU-04  
**Modelo(s):** ME-03 y ME-06 (estadísticas de tratamiento)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá calcular indicadores de novedades, revisiones, tareas e incidencias, distinguiendo sus estados y responsabilidades sin inferir resultados jurídicos no registrados.

**Reglas/invariantes y referencias precisadas v0.8:** RF-V1-059; RF-V1-068; RF-V1-101
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Novedad descartada no se contabiliza como cerrada salvo regla explícita.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-117 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Tres novedades: Cerrada, Descartada y En revisión.
- **Procedimiento:** Calcular indicador de tratamiento por estado.
- **Resultado esperado:** Cada estado se contabiliza en categoría correspondiente sin atribuir Descartada a Cerrada.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-118 — Identificar criterios y fecha de corte

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador / usuario interno autorizado  
**Caso(s) de uso:** CU-04  
**Modelo(s):** Diccionario de indicadores G08 (pendiente; sin ME propia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá conservar y presentar los criterios de interpretación de cada indicador, incluyendo ámbito, periodo, fecha de corte, definición de numerador y denominador cuando corresponda y tratamiento de datos insuficientes.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-02; INV-RF-03; RF-V1-116; RF-V1-117
**Dependencias:** RF-V1-116, 117; diccionario de indicadores  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** Indicador sin denominador válido se reporta sin datos o no aplicable.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-118 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Indicador con denominador cero y periodo de noviembre.
- **Procedimiento:** Solicitar cálculo y vista de indicador.
- **Resultado esperado:** Se presenta no aplicable/sin datos conforme a regla, además de ámbito y fecha de corte.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-119 — Exportar información operativa

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Coordinador / usuario interno autorizado  
**Caso(s) de uso:** CU-11, CU-16  
**Modelo(s):** Modelo de expediente y auditoría G08 (exportación; sin ME propia)
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados exportar conjuntos de información operativa definidos, aplicando filtros, restricciones de acceso y referencias de fecha y procedencia, sin incluir información ajena al ámbito autorizado.

**Reglas/invariantes y referencias precisadas v0.8:** INV-RF-01; RF-V1-010; RF-V1-114; RF-V1-118
**Dependencias:** G01; fuentes funcionales G02–G09  
**Estado de trazabilidad:** Referencias individualizadas documentalmente en v0.8; correspondencia semántica y decisiones por ratificar.
**Criterio de aceptación inicial:** La exportación mantiene los mismos filtros y ámbito autorizado de consulta.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-119 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Expediente de prueba con observaciones, novedades y trazas verificables; política de autorización para la consulta.
- **Datos de entrada:** Usuario de A con filtro de periodo y registros de A/B.
- **Procedimiento:** Exportar subconjunto operativo autorizado.
- **Resultado esperado:** El archivo conserva filtros y ámbito de A; no incluye filas privadas de B.
- **Evidencia de verificación:** Consulta o exportación resultante, definición de ámbito e indicadores o eventos de auditoría.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G09 — Publicaciones e informes

#### RF-V1-120 — Crear borradores de publicación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un usuario interno autorizado crear borradores de publicación, identificando su tipo, finalidad, responsable y contexto de origen, sin habilitar automáticamente su consulta externa.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Borrador creado no aparece en portal externo.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-120 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Usuario interno autorizado y novedad tratada.
- **Procedimiento:** Crear borrador de publicación para cliente destinatario.
- **Resultado esperado:** Se crea Borrador asociado sin visibilidad externa.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-121 — Definir destinatario

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá exigir que cada publicación identifique un cliente destinatario autorizado y, cuando corresponda, los seguimientos relacionados, rechazando asociaciones incompatibles con dicho cliente.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Informe no admite seguimiento privado de otro cliente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-121 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Publicación de cliente A y seguimiento de cliente B.
- **Procedimiento:** Intentar agregar seguimiento B como alcance de publicación A.
- **Resultado esperado:** Se rechaza la combinación de destinatarios incompatible.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-122 — Seleccionar contenido comunicable

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir incorporar información procedente de resultados operativos o jurídicos revisados, verificando que satisface las condiciones de validación aplicables y conservando sus referencias de origen.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Propuesta LLM pendiente de revisión no se publica como dato confirmado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-122 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Novedad con valoración revisada y propuesta LLM sin aprobar.
- **Procedimiento:** Seleccionar ambos contenidos para borrador.
- **Resultado esperado:** Solo el contenido revisado y comunicable se incorpora; propuesta no aprobada queda fuera.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-123 — Preparar contenido y evidencias

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir redactar y estructurar el contenido comunicable, diferenciando los hechos judiciales, las fechas, las valoraciones jurídicas aprobadas y las referencias de evidencia utilizadas.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Contenido distingue fecha de actuación y fecha de publicación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-123 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Actuación judicial con fecha propia y borrador con fecha de publicación futura.
- **Procedimiento:** Preparar comunicación con referencias y evidencias.
- **Resultado esperado:** Contenido identifica hechos, fechas y sustentos sin confundir actuaciones con publicación.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-124 — Seleccionar anexos externos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir asociar documentos a una versión de publicación y definir expresamente cuáles quedarán habilitados para el destinatario, sin ampliar automáticamente los permisos sobre otros documentos del expediente.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Documento no habilitado no se incluye como anexo descargable.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-124 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Dos documentos internos, solo uno expresamente autorizado como anexo externo.
- **Procedimiento:** Seleccionar anexos de la versión y consultar disponibilidad.
- **Resultado esperado:** Solo el anexo habilitado puede exponerse al destinatario.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-125 — Validar condiciones previas de publicación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-21, CU-20  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá comprobar que una versión de publicación satisface las condiciones aplicables de destinatario, contenido, revisión, evidencias y anexos, incluyendo la identidad del artefacto final cuando se trate de un informe PDF, antes de admitir su autorización.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-121 a 124; RF-V1-137 para PDF  
**Criterio de aceptación inicial:** PDF no generado o versión sin revisiones obligatorias no se envía a aprobación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-125 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Informe PDF aún no generado y novedad sin revisión obligatoria.
- **Procedimiento:** Solicitar validación previa de publicación.
- **Resultado esperado:** Se bloquea envío a autorización hasta disponer de artefacto y revisiones exigidas.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-126 — Solicitar autorización de versión

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21, CU-20  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir solicitar autorización sobre una versión identificable e inalterable del contenido y sus anexos, conservando la representación exacta sometida a aprobación.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-125; identidad de versión  
**Criterio de aceptación inicial:** La solicitud vincula versión exacta y no permite modificar contenido en revisión.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-126 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Borrador completo con PDF final candidato y anexos identificados.
- **Procedimiento:** Solicitar autorización y luego intentar editar versión en revisión.
- **Resultado esperado:** Se congela versión exacta y se rechazan modificaciones sobre ella.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-127 — Aprobar o rechazar publicaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador autorizado  
**Caso(s) de uso:** CU-20  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al coordinador autorizado aprobar o rechazar una versión específica, registrando responsable, fecha y resultado, y verificando las restricciones de segregación de funciones aprobadas para la organización.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-126; segregación de funciones pendiente  
**Criterio de aceptación inicial:** Aprobación autorizada queda registrada; usuario sin permisos no aprueba.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-127 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Coordinador autorizado y usuario sin permiso; versión Pendiente autorización.
- **Procedimiento:** Solicitar aprobación con ambos usuarios.
- **Resultado esperado:** Solo el autorizado decide y queda traza de identidad, fecha, resultado y versión.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-128 — Proteger la versión aprobada

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá impedir que una versión autorizada conserve su aprobación después de modificar contenido, destinatario o anexos, exigiendo una nueva versión y validación cuando ocurra un cambio.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-126, 127; control de versión  
**Criterio de aceptación inicial:** Modificar una versión autorizada fuerza nueva versión pendiente de aprobación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-128 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Versión Autorizada y cambio posterior en un anexo.
- **Procedimiento:** Intentar mantener autorización modificando el contenido.
- **Resultado esperado:** La autorización anterior no cubre el cambio; exige nueva versión y aprobación.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-129 — Ejecutar publicación autorizada

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá publicar únicamente una versión previamente autorizada, comprobando su identidad y destinatario y registrando el estado Publicada solo cuando se confirme su disponibilidad externa efectiva.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-127, 128; disponibilidad efectiva  
**Criterio de aceptación inicial:** Una publicación técnica fallida mantiene estado Autorizada.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-129 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Versión Autorizada y publicación técnica fallida simulada.
- **Procedimiento:** Intentar habilitar contenido para cliente.
- **Resultado esperado:** No se marca Publicada mientras no exista disponibilidad efectiva; permanece Autorizada con fallo.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-130 — Registrar fallos y reintentos de publicación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá registrar los intentos, resultados y fallos del proceso de publicación, permitiendo reintentos controlados sin crear versiones externas duplicadas.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Un reintento equivalente no origina doble publicación.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-130 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Intento de publicación de versión autorizado repetido dos veces.
- **Procedimiento:** Ejecutar publicación y reintento equivalente.
- **Resultado esperado:** El contenido se habilita una sola vez y queda historial de intentos.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-131 — Consultar historial de versiones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a usuarios internos autorizados consultar las versiones, decisiones, estados y referencias de evidencia de una publicación, conservando su secuencia histórica.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Versión reemplazada permanece trazable internamente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-131 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Publicación con versión v1 Reemplazada y v2 Publicada.
- **Procedimiento:** Consultar historial interno de publicación.
- **Resultado esperado:** Se observan estados, responsables, fechas y relación histórica, sin editar versiones previas.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-132 — Corregir y reemplazar publicaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir sustituir una publicación vigente mediante una nueva versión autorizada, conservando el historial anterior y evitando marcar la versión original como Reemplazada antes de confirmar la publicación de la sustituta.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-127 a 130; ME-05  
**Criterio de aceptación inicial:** Fallo de versión sustituta conserva vigencia anterior, salvo retirada independiente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-132 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Versión v1 Publicada y versión v2 Autorizada con fallo al publicar.
- **Procedimiento:** Intentar reemplazar y verificar cuál versión está vigente.
- **Resultado esperado:** v1 conserva vigencia hasta confirmar publicación de v2 o decisión independiente de retirada.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-133 — Retirar publicaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Coordinador autorizado  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir retirar una publicación mediante una operación autorizada y justificada, comprobar la revocación de su disponibilidad externa ordinaria y registrar las incidencias cuando la retirada no pueda completarse satisfactoriamente.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-134; revocación externa  
**Criterio de aceptación inicial:** Una retirada efectiva niega consulta externa; fallo no se declara exitoso.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-133 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Publicación vigente con autorización de retirada y fallo técnico simulado.
- **Procedimiento:** Solicitar retirada y comprobar acceso externo.
- **Resultado esperado:** No se declara Retirada si aún es accesible; se registra incidencia.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-134 — Controlar visibilidad externa

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-21  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá controlar la visibilidad externa de publicaciones, versiones y anexos conforme al cliente destinatario, autorizaciones, estado y vigencia, aplicando las revocaciones de acceso y evitando la consulta ordinaria de recursos retirados, reemplazados o no publicados.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-010, 124, 129, 132, 133; absorbe RF-V1-151  
**Criterio de aceptación inicial:** Una URL conocida de versión retirada o ajena no concede acceso.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-134 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Publicación v1 Retirada, v2 vigente para A; usuario cliente B.
- **Procedimiento:** Solicitar URL de v1 y v2 desde cuentas A y B.
- **Resultado esperado:** Solo v2 vigente es visible a A; v1 y acceso B se deniegan.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-135 — Preparar informes consolidados

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-29 (propuesto)  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un usuario interno autorizado preparar un informe para un cliente y un periodo definidos, seleccionando información y resultados elegibles de uno o varios seguimientos del mismo destinatario.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Informe con seguimientos de diferentes clientes se rechaza.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-135 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Carteras A y B, selección mezclada e intervalo de octubre.
- **Procedimiento:** Preparar informe consolidado de A incluyendo accidentalmente seguimiento B.
- **Resultado esperado:** Se rechaza inclusión de B y solo se permite consolidación de seguimientos de A.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-136 — Validar contenido y cobertura de informe

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Sistema de publicación  
**Caso(s) de uso:** CU-29 (propuesto)  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá comprobar que el informe identifica su periodo, fecha de corte, procesos incluidos, procedencia y condiciones de cobertura, diferenciando consultas satisfactorias, pendientes, incompletas y fallidas.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** G05, G06 y G08; G01; ME-05  
**Criterio de aceptación inicial:** Fallo de adquisición se presenta como limitación de cobertura y no sin cambios.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-136 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** Informe incluye consulta fallida durante periodo de cobertura.
- **Procedimiento:** Validar contenido de informe y su periodo.
- **Resultado esperado:** Se identifica limitación de cobertura, procedencia y corte; no se afirma ausencia de cambios.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-137 — Generar y publicar informe PDF

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Autor o responsable interno autorizado  
**Caso(s) de uso:** CU-29 (propuesto), CU-27  
**Modelo(s):** ME-05  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir generar una versión PDF verificable de un informe antes de solicitar su autorización y, una vez aprobada, publicar exactamente el artefacto autorizado, requiriendo una nueva versión y aprobación ante modificaciones posteriores.

**Reglas/invariantes:** RG09-01 a RG09-17; aprobación de artefacto exacto  
**Dependencias:** RF-V1-125 a 129, 135, 136; PDF antes de aprobación  
**Criterio de aceptación inicial:** PDF descargado coincide con artefacto aprobado; cualquier cambio posterior exige nueva autorización.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-137 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Publicación de prueba con versión, cliente destinatario, contenido revisado, guardas y contexto ME-05 definidos.
- **Datos de entrada:** PDF candidato final aprobado, luego archivo modificado.
- **Procedimiento:** Solicitar publicación del PDF modificado y descarga del original aprobado.
- **Resultado esperado:** Solo artefacto exacto aprobado es publicable; cambio exige nueva autorización.
- **Evidencia de verificación:** Identidad de versión/artifacto, historia ME-05, disponibilidad externa y registro de autorización.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


### G10 — Portal del cliente

#### RF-V1-138 — Consultar panel del cliente

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-22  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir a un usuario externo autenticado consultar un panel principal con información de los seguimientos y publicaciones autorizados para el cliente al que está vinculado.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Un cliente externo solo ve panel de su propio cliente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-138 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Cuentas externas de A y B con respectivos seguimientos.
- **Procedimiento:** Abrir portal con usuario A.
- **Resultado esperado:** Panel muestra solo cartera, avisos y publicaciones habilitados para A.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-139 — Consultar indicadores de cartera

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-22  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá presentar indicadores resumidos de la cartera del cliente, calculados exclusivamente sobre sus seguimientos autorizados y acompañados de criterios de interpretación y fecha de actualización.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Los conteos no incluyen novedades internas no publicadas ni datos de otro cliente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-139 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Cliente A tiene publicación vigente; novedad interna pendiente y seguimiento B ajeno.
- **Procedimiento:** Calcular indicadores externos de A.
- **Resultado esperado:** Conteos excluyen novedad privada y registros B; muestran criterio y fecha de corte.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-140 — Consultar cartera judicial

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-23  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al usuario externo consultar el listado de procesos judiciales asociados a los seguimientos autorizados de su cliente, mostrando sus datos de identificación y estados administrativos permitidos.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Un radicado de otro cliente no revela su seguimiento privado.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-140 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Procesos asociados a A y B, un radicado compartido con seguimiento independiente.
- **Procedimiento:** Consultar listado de A.
- **Resultado esperado:** Solo aparecen seguimientos autorizados de A, sin revelar el contexto B.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-141 — Filtrar cartera judicial

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-23  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir buscar y filtrar los seguimientos autorizados mediante radicado, estado administrativo y demás criterios expresamente habilitados para el portal.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** La búsqueda no devuelve recursos fuera del ámbito del usuario.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-141 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Seguimientos propios y ajenos con mismo término de búsqueda.
- **Procedimiento:** Filtrar cartera por radicado y estado.
- **Resultado esperado:** Los resultados cumplen filtro y permanecen restringidos al cliente A.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-142 — Consultar detalle del seguimiento

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-24  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al usuario externo consultar el detalle administrativo de un seguimiento de su cliente, incluyendo identificación del proceso, estado, referencias de vigilancia permitidas y acceso a sus publicaciones autorizadas.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** El detalle no expone notas internas ni propuestas LLM no publicadas.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-142 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Seguimiento A con publicación vigente y nota jurídica interna restringida.
- **Procedimiento:** Abrir detalle externo del seguimiento.
- **Resultado esperado:** Se presenta identificación y comunicaciones autorizadas, no nota interna.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-143 — Informar condición de vigilancia

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-24  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá presentar al cliente autorizado la condición de vigilancia de cada seguimiento, diferenciando estado administrativo, última observación válida, actualización y limitaciones de cobertura, sin interpretar adquisiciones fallidas como ausencia de actuaciones.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** RF-V1-032, 046, 116, 118  
**Criterio de aceptación inicial:** Seguimiento activo con última consulta fallida no se presenta actualizado al intento fallido.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-143 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Seguimiento Activo, última observación válida día 4, intento fallido día 6.
- **Procedimiento:** Consultar estado y fechas del seguimiento en portal.
- **Resultado esperado:** Se muestra última fecha válida 4, fallo día 6 y ausencia de cobertura confirmada al 6.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-144 — Consultar novedades publicadas

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-25  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al usuario externo consultar un listado de novedades cuyas publicaciones estén vigentes, efectivamente disponibles y dirigidas a su cliente.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Novedad pendiente de revisión no aparece en el portal.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-144 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Novedad En revisión y otra con publicación Publicada vigente.
- **Procedimiento:** Consultar listado externo de novedades.
- **Resultado esperado:** Solo publicación vigente es listada; novedad pendiente no se revela.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-145 — Consultar detalle de publicación

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-25  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir consultar el contenido autorizado de una publicación de novedad, incluyendo las referencias judiciales, fechas, información comunicada y anexos permitidos.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Un cliente no puede abrir detalle de publicación ajena por ID.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-145 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Publicaciones A y B y anexo protegido.
- **Procedimiento:** Abrir detalle de publicación B desde usuario A.
- **Resultado esperado:** Se deniega contenido B; anexos requieren autorización propia.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-146 — Diferenciar ausencia de publicaciones

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-25  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá diferenciar en el portal la ausencia de publicaciones vigentes de la ausencia verificable de cambios judiciales, sin divulgar novedades pendientes de revisión ni información interna restringida.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** RF-V1-134, 143  
**Criterio de aceptación inicial:** Sin publicaciones no produce mensaje automático de ausencia de actuaciones.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-146 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Seguimiento A sin publicaciones y con última consulta fallida.
- **Procedimiento:** Consultar sección de novedades.
- **Resultado esperado:** Se informa ausencia de publicaciones disponibles sin afirmar ausencia de cambios judiciales.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-147 — Consultar documentos habilitados

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-26  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al usuario externo consultar el listado de documentos expresamente habilitados para su cliente, mostrando únicamente los metadatos autorizados y su relación con las publicaciones correspondientes.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** Solo aparecen documentos expresamente habilitados para ese cliente.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-147 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Documento interno restringido y anexo de publicación vigente habilitado.
- **Procedimiento:** Consultar listado documental externo.
- **Resultado esperado:** Solo aparece anexo habilitado y sus metadatos permitidos.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-148 — Visualizar y descargar documentos

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P0  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-26  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir visualizar o descargar documentos expresamente habilitados para el cliente, comprobando la autorización contextual y vigencia del recurso en cada solicitud, incluso cuando se utilice un enlace previamente conocido.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** RF-V1-010, 124, 134, 147  
**Criterio de aceptación inicial:** Documento retirado o de otro cliente no puede abrirse con URL antigua.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-148 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Documento de A retirado y URL histórica conocida; documento vigente autorizado.
- **Procedimiento:** Solicitar descarga de ambos.
- **Resultado esperado:** Solo documento vigente es descargable; retirada o acceso ajeno se deniegan.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-149 — Consultar informes publicados

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-27  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir al usuario externo consultar los informes consolidados efectivamente publicados para su cliente, identificando su periodo, fecha de corte, versión y estado de disponibilidad.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** G01; G09; control de disponibilidad  
**Criterio de aceptación inicial:** No se muestran informes borrador ni de clientes ajenos.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-149 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Informe Borrador, informe Publicado de A e informe Publicado de B.
- **Procedimiento:** Consultar informes del cliente A.
- **Resultado esperado:** Solo informe A publicado figura en listado con periodo y fecha de corte.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


#### RF-V1-150 — Visualizar y descargar informes PDF

**Estado funcional:** Activo candidato  
**Recuperación del enunciado:** Recuperado en contexto  
**Prioridad:** P1  
**Actor/responsable:** Usuario externo autenticado / sistema  
**Caso(s) de uso:** CU-27  
**Modelo(s):** ME-01 y ME-05 (consulta externa)  
**Aprobación:** Candidato  

**Enunciado normativo vigente/propuesto:**

> El sistema deberá permitir consultar o descargar la versión PDF vigente de un informe efectivamente publicado para el cliente autorizado, verificando su identidad de versión y registrando las operaciones sensibles conforme a RF-V1-114.

**Reglas/invariantes:** RG10-01 a RG10-16; solo contenido habilitado  
**Dependencias:** RF-V1-114, 134, 137, 149  
**Criterio de aceptación inicial:** La descarga corresponde a PDF autorizado y audita acceso sensible.  
**Procedencia:** RT-RF-003 o especificación de G07–G10 visible en la conversación.  

**AT-V1-150 — Caso de aceptación estructurado (propuesto; no ejecutado)**

- **Precondiciones:** Portal de prueba con cuentas externas y seguimientos de dos clientes; el acceso se verifica en backend y no se emplean datos privados reales.
- **Datos de entrada:** Informe PDF aprobado vigente para A y archivo similar no autorizado.
- **Procedimiento:** Descargar informes desde sesión A.
- **Resultado esperado:** Solo se descarga el PDF aprobado, con control de versión y auditoría correspondiente.
- **Evidencia de verificación:** Respuesta de portal/API, controles de acceso por recurso, versión y auditoría cuando aplique.
- **Estado:** Diseño preliminar; pendiente de definición fina de datos, ratificación de reglas y ejecución en software.


## 4. Registro de cambios y equivalencias

| Código | Acción | Evidencia de decisión | Resultado |
|---|---|---|---|
| CHG-001 | EXCLUIR RF-V1-078 | Decisión G06 | Sin OCR independiente ni extracción nativa separada. |
| CHG-002 | REFORMULAR G06 | RT-RF-002/003 | Modelo LLM multimodal directo, compatibilidad y revisión humana. |
| CHG-003 | REFORMULAR G02/G04 | RT-RF-002/003 | Referencia técnica, línea base por seguimiento, temporalidad y cobertura separadas. |
| CHG-004 | REFORMULAR RF-V1-137 | RT-RF-002/003 | PDF final candidato antes de autorización; publicación del artefacto exacto. |
| CHG-005 | ABSORBER RF-V1-151 | RT-RF-003 | RF-V1-134 mantiene control de visibilidad/revocación. |
| CHG-006 | ABSORBER RF-V1-152 | RT-RF-003 | RF-V1-114 cubre auditoría de accesos externos. |
| CHG-007 | INCORPORAR RF-V1-153 | RT-RF-003 | Rectificación trazable de decisiones sobre novedades. Pendiente ratificación. |
| CHG-008 | CONDICIONAR habilitación externa | RT-RF-002 | POC fuente judicial y POC proveedor LLM pendientes. |
| CHG-009 | CONSOLIDAR 58 textos | RF-CAT-001 v0.4 | Se registraron 58 propuestas reconstruidas, pendientes de cotejo. |
| CHG-010 | RECUPERAR RF-V1-001 | Cotejo con formulación histórica G01 | Se restableció el texto del requisito original y disminuyó el saldo literal pendiente a 57. |
| CHG-011 | PRECISAR cinco reconstrucciones | Revisión semántica RV-001 (v0.5) | Ajustes propuestos a RF-V1-003, 033, 037, 039 y 073; permanecen provisionales. |

## 5. Matriz resumida de trazabilidad

| Grupo | Casos de uso | Estados/modelos | Pruebas transversales mínimas |
|---|---|---|---|
| G01 | CU-01, CU-02, CU-17 | Identidad y permisos | Acceso ajeno denegado, sesión deshabilitada. |
| G02 | CU-03, CU-04, CU-06, CU-18, CU-19 | ME-01 | Mismo proceso en dos clientes; reactivación sin cobertura. |
| G03 | CU-05, CU-28, CU-30 propuesto | ME-02, ME-07 candidata | Fuente no habilitada; fallos e idempotencia. |
| G04 | CU-07, CU-08 | Reglas determinísticas | Primera observación, duplicados, retrospectividad. |
| G05 | CU-09, CU-10, CU-21 | ME-03 | Descarte, revisión jurídica, rectificación y cierre. |
| G06 | CU-12, CU-13, CU-14 | ME-04A/04B | PDF nativo/escaneado multimodal, fallo, corrección humana. |
| G07 | CU-15, CU-19 | ME-06 | Bloqueo, cancelación obligatoria, aviso sin permiso adicional. |
| G08 | CU-07, CU-11, CU-16, CU-04 | Auditoría/invariantes | Accesos, secuencia temporal, indicador sin línea base. |
| G09 | CU-20, CU-21, CU-29 propuesto | ME-05 | Aprobación artefacto exacto, sustitución, retirada. |
| G10 | CU-22 a CU-27 | ME-01/ME-05 | Cliente ajeno, URL revocada, publicación no disponible. |

## 6. Decisiones y dependencias abiertas (no declaradas aprobadas)

| Código | Decisión o evidencia pendiente | Grupos | Criterio de cierre |
|---|---|---|---|
| PD-01 | Mecanismo autorizado de adquisición de la fuente inicial CPNU u otra fuente ratificada | G03/G04 | Ficha de factibilidad y prueba controlada con autorización. |
| PD-02 | Reglas de identidad y comparabilidad por fuente | G02/G04 | Corpus y criterios de correspondencia validados. |
| PD-03 | Proveedor y tipos documentales de LLM multimodal | G06 | POC realista con PDF nativo, escaneado e imagen admitida. |
| PD-04 | Aprobación del tratamiento externo y política de retención | G06/G08 | Validación responsable y control técnico habilitado. |
| PD-05 | Suspensión de cliente, accesos históricos y cuentas externas | G01/G02/G10 | Política formal de autorización y ciclo de vida. |
| PD-06 | Recuperación de cobertura al reactivar un seguimiento | G02/G04 | Reglas temporales, ejemplos y pruebas negativas aprobadas. |
| PD-07 | Contenido que exige revisión jurídica y segregación de aprobación | G05/G09 | Matriz de contenido/roles ratificada por responsables. |
| PD-08 | Rectificación de decisiones y publicaciones afectadas | G05/G07/G09 | Aprobar RF-V1-153 y sincronizar ME-03/ME-05. |
| PD-09 | Definiciones, periodos y denominadores de indicadores | G08/G10 | Diccionario de métricas verificable. |
| PD-10 | Criterios de retención, integridad y consulta de auditoría | G06/G08 | RNF y política aprobados. |
| PD-11 | Aprobación de absorciones 151→134, 152→114 | G08/G09/G10 | Acta de control de cambios ratificada. |
| PD-12 | CU-29 y CU-30 formalizados | G03/G09 | Especificaciones de casos de uso validadas. |

## 7. Calidad y limitaciones de esta versión

- **Total activo comprobado por script:** 150.
- **Recuperados en contexto o históricamente localizados:** 93.
- **Reconstrucciones con cotejo literal pendiente:** 57.
- Todos los IDs activos son únicos, inmutables y distintos de 078, 151 y 152.
- Todas las fichas incluyen enunciado, actor, prioridad/condición, CU, modelo, reglas, dependencia, criterio de aceptación y procedencia.
- Los CU y criterios recuperados o propuestos deben todavía verificarse individualmente contra los artefactos finales.
- El estado “recuperado en contexto” **no equivale** a aprobación por tutor, profesionales jurídicos ni responsable del producto.
- Los 57 enunciados todavía reconstruidos son **propuestas para cotejo**, no texto original recuperado ni aprobación de cambios de alcance.
- **No se han ejecutado pruebas de software** ni POC con fuentes judiciales o proveedor de IA en esta actividad.
- La versión histórica 0.5 se puede utilizar como documento de trabajo, pero no como línea base contractual de implementación.

## 8. Criterios de salida para RF-CAT-001 v1.0

1. Recuperar, cotejar y ratificar las 57 fichas marcadas como reconstruidas; conservar diferencias si las hubiera.
2. Confirmar prioridad y actor de cada requisito, especialmente G01–G06.
3. Revisar la correspondencia individual RF ↔ caso de uso ↔ regla de negocio ↔ máquina de estados ↔ prueba.
4. Convertir cada criterio de aceptación a casos verificables con precondiciones, entradas, pasos, resultado esperado y evidencia.
5. Formalizar CU-29 y CU-30 y sincronizar ME-03, ME-04A y ME-05.
6. Ratificar el estado de RF-V1-153 y las absorciones de RF-V1-151/152.
7. Registrar aprobaciones de negocio y dependencia externa; una POC no suplanta una autorización organizacional.
8. Versionar la línea base solo después de la revisión de calidad y aprobación correspondiente.

## 9. Próximas etapas hasta desarrollo

| Orden | Artefacto | Acción |
|---|---|---|
| 1 | RF-CAT-001 v1.0 | Cotejo literal/individual, trazabilidad y ratificación. |
| 2 (paralelo) | RNF-001 | Seguridad, privacidad, rendimiento, integridad, disponibilidad, mantenibilidad y pruebas medibles. |
| 3 (paralelo) | POC-FCT-001 / POC-LLM-001 | Factibilidad de adquisición y análisis documental multimodal habilitado. |
| 4 | ERS-001 | Unificar RF, RNF, reglas, interfaces y criterios de aceptación. |
| 5 | ARC-001 / DAT-001 | C4/ADR, modelo conceptual y lógico de datos. |
| 6 | API-001 / UX-001 | Contratos de servicios, eventos y flujos para actores internos/externos. |
| 7 | DEV-PLAN-001 | Backlog incremental, definición de terminado, pruebas y entornos. |
| 8 | DEV-001 | Primer flujo vertical de adquisición → detección → revisión → publicación → consulta. |

## 10. Checkpoint histórico (v0.6, superado por §18)

**Versión histórica a esa fecha:** RF-CAT-001 v0.6 (57 pruebas de aceptación diseñadas; 57 enunciados pendientes de cotejo).
**No rehacer G01–G10 desde cero.** El inventario y los contratos preliminares están aquí consolidados.
**No reintroducir OCR, extracción nativa separada ni fine-tuning propio.** La validación humana de propuestas sigue siendo obligatoria.
**No declarar factibilidad de adquisición judicial ni tratamiento LLM con datos reales sin comprobaciones y autorizaciones.**
**Siguiente tarea precisa:** cotejar las 57 reconstrucciones restantes de G01–G06 o ratificarlas como redacción nueva; revisar los 57 AT propuestos y completar las pruebas de aceptación de los otros 93 RF. Después efectuar una revisión de trazabilidad y elevar RF-CAT-001 a aprobación.


## 11. RV-001 — Revisión individual de los enunciados inicialmente reconstruidos

**Alcance:** revisión de coherencia semántica y riesgos de interpretación de los 58 requisitos que en v0.4 figuraban como reconstruidos. En v0.5, RF-V1-001 tiene su redacción original recuperada; 57 requieren aún cotejo literal. Esta revisión NO reemplaza el cotejo ni la aprobación funcional.

| RF | Dictamen semántico | Hallazgo verificable | Acción pendiente |
|---|---|---|---|
| RF-V1-001 | LITERAL RECUPERADO | Se recuperó el enunciado original G01 y se reemplazó la referencia a credenciales por «mecanismo de autenticación configurado». | Confirmar prioridad, actor y CA. |
| RF-V1-002 | CONFORME CON RESERVAS | El estado de sesión está definido, pero las reglas de invalidación y cierre deben concretarse. | Precisar criterios para expiración, cierre e invalidación. |
| RF-V1-003 | AJUSTE PROPUESTO | «Autorización del solicitante» no verificaba de manera precisa su identidad; riesgo de recuperación indebida. | Reformulación propuesta; ratificar identidad, canal y evidencias. |
| RF-V1-004 | CONFORME CON RESERVAS | El ciclo de usuario interno está cubierto; alcance de modificaciones y conservación por definir. | Cotejar operación y reglas de deshabilitación. |
| RF-V1-005 | DECISION PENDIENTE | No está cerrada la granularidad de asignación de permisos ni la separación entre rol y permiso. | Aprobar matriz de roles/permisos y auditoría. |
| RF-V1-006 | DECISION PENDIENTE | La regla de duplicidad de cliente no está expresada con clave de identidad comprobable. | Definir atributos de identificación y duplicidad. |
| RF-V1-007 | CONFORME CON RESERVAS | Actualización de datos administrativos no debe reescribir historia operativa. | Conservar valores históricos y auditoría según política. |
| RF-V1-009 | CONFORME CON RESERVAS | Vinculación de cuenta externa a un cliente en V1 es coherente; falta suspensión/acceso histórico. | Ratificar efectos de suspensión y permisos externos. |
| RF-V1-011 | CONFORME CON RESERVAS | Registro de proceso compatible con radicado; formato y validación deben cotejarse. | Comprobar estructura de radicado 23 dígitos y reglas por fuente. |
| RF-V1-013 | CONFORME CON RESERVAS | Consulta de proceso separada de consulta de seguimiento. | Asegurar que los metadatos privados no se mezclan. |
| RF-V1-014 | CONFORME CON RESERVAS | Carpeta/cartera filtrada por ámbitos de cliente. | Criterios de filtro y conteo autorizados. |
| RF-V1-015 | DECISION PENDIENTE | No está decidida la unicidad de seguimiento activo cliente-proceso. | Definir cardinalidad y restricciones de reactivación. |
| RF-V1-017 | DECISION PENDIENTE | Periodicidad/intensidad no poseen dominio de valores ni restricciones justificadas. | Formalizar parámetros de política de vigilancia. |
| RF-V1-018 | CONFORME CON RESERVAS | Responsables operativos y jurídicos se distinguen. | Precisar asignación simultánea y delegación. |
| RF-V1-019 | CONFORME CON RESERVAS | Suspensión conserva registro histórico y corta consultas ordinarias. | Ratificar controles de nueva elegibilidad. |
| RF-V1-021 | CONFORME CON RESERVAS | Finalización separada de suspensión. | Resolver acceso histórico y cierre documental. |
| RF-V1-022 | CONFORME CON RESERVAS | Consulta de estados e historial de seguimiento es coherente. | Vincular con ME-01 y permisos. |
| RF-V1-024 | DECISION PENDIENTE | El cumplimiento de política depende de frecuencia/cobertura y denominador no definido. | Crear reglas de cálculo y situaciones sin datos. |
| RF-V1-025 | CONFORME CON RESERVAS | Registrar fuente no implica habilitarla. | Conservar RF-V1-026 como control separado. |
| RF-V1-027 | CONFORME CON RESERVAS | Configurar modalidad de fuente es coherente sin fijar una técnica no autorizada. | Documentar restricciones del mecanismo seleccionado. |
| RF-V1-028 | CONFORME CON RESERVAS | Consulta individual por radicado coincide con alcance V1. | Validar propósito, fuente y solicitante elegible. |
| RF-V1-031 | DEPENDENCIA EXTERNA | Adquisición real requiere mecanismo autorizado; la formulación no acredita factibilidad. | Vincular POC de fuente y resultados de autorización. |
| RF-V1-033 | AJUSTE PROPUESTO | Una adquisición puede vincularse con varios seguimientos; redacción singular era restrictiva. | Usar solicitud y relaciones autorizadas uno-a-varios; verificar trazabilidad. |
| RF-V1-034 | CONFORME CON RESERVAS | Control de reintentos e idempotencia es coherente. | Parametrizar límites según fuente y política. |
| RF-V1-035 | CONFORME CON RESERVAS | Registro de errores suficiente a nivel funcional. | Evitar credenciales o contenido privado en logs técnicos. |
| RF-V1-037 | AJUSTE PROPUESTO | Compartición técnica de adquisición no habilita consulta de contextos privados ajenos. | Aplicar filtros por seguimiento e identidad. |
| RF-V1-038 | CONFORME CON RESERVAS | Incidencias quedan asociadas a adquisiciones/fuentes. | Formalizar transición y responsables de incidentes. |
| RF-V1-039 | AJUSTE PROPUESTO | Trazabilidad debe admitir asociación con varios seguimientos; relación exclusiva era débil. | Referencias de solicitudes y seguimientos aplicables. |
| RF-V1-040 | CONFORME CON RESERVAS | Observaciones comparables se registran; intentos fallidos quedan en G03. | Aclarar persistencia separada de datos incompletos. |
| RF-V1-041 | CONFORME CON RESERVAS | Procedencia debe mantener fuente y evidencia separadas de evaluaciones internas. | Cotejar conservación de respuesta original. |
| RF-V1-043 | CONFORME CON RESERVAS | Normalización determinística conservando valores originales. | Definir reglas y versiones por fuente. |
| RF-V1-044 | CONFORME CON RESERVAS | Identidad de actuaciones dentro de observación distinguida de comparación. | Definir campos por modalidad de fuente. |
| RF-V1-045 | CONFORME CON RESERVAS | Persistencia histórica sin sobrescrituras ordinarias. | Vincular con retención e integridad de datos. |
| RF-V1-048 | DEPENDENCIA EXTERNA | Identidad de actuación requiere pruebas con datos de fuente real y casos ambiguos. | POC de identidad y ground truth. |
| RF-V1-049 | CONFORME CON RESERVAS | Comparación determinística, sin LLM para diffs. | Documentar equivalencia de observaciones. |
| RF-V1-051 | CONFORME CON RESERVAS | Diferencia incorporación vs actualización identificada. | Agregar casos con corrección de metadatos. |
| RF-V1-052 | CONFORME CON RESERVAS | Registro de diferencias con evidencia. | Definir ID estable del cambio y procedencia. |
| RF-V1-053 | CONFORME CON RESERVAS | Idempotencia del motor coherente. | Validar reintento y reordenamiento de observaciones. |
| RF-V1-056 | CONFORME CON RESERVAS | Cambio elegible origina novedad candidata, no conclusión jurídica. | Verificar vínculo con G04 y ME-03. |
| RF-V1-057 | CONFORME CON RESERVAS | Novedad propia de seguimiento/cliente. | Asegurar que la evidencia compartida no expone tratamiento privado. |
| RF-V1-058 | CONFORME CON RESERVAS | No duplicar una novedad del mismo cambio y seguimiento. | Prueba de concurrencia/reintento. |
| RF-V1-059 | CONFORME CON RESERVAS | Revisión operativa separada de valoración jurídica. | Confirmar actores habilitados. |
| RF-V1-060 | CONFORME CON RESERVAS | Reasignación de novedad preserva historia. | Definir delegación y cambios de responsable. |
| RF-V1-061 | CONFORME CON RESERVAS | Vista interna respeta asignación y estado. | Concretar filtros y permisos. |
| RF-V1-063 | CONFORME CON RESERVAS | Notas operativas separadas de decisión y auditoría. | Relacionar evidencia con autor y novedad. |
| RF-V1-065 | DECISION PENDIENTE | La obligatoriedad de escalamiento jurídico por categoría sigue sin ratificar. | Matriz de tipos y revisión requerida. |
| RF-V1-067 | CONFORME CON RESERVAS | Historial de decisiones preservado. | Cotejar vínculo con RF-V1-153. |
| RF-V1-069 | DECISION PENDIENTE | Tratamiento y acciones requieren taxonomía y criterios de obligatoriedad. | Precisar tipos de tratamiento y cierre. |
| RF-V1-071 | CONFORME CON RESERVAS | Custodia documental desde origen permitido. | Verificar relación fuente/proceso y uso de metadatos. |
| RF-V1-072 | CONFORME CON RESERVAS | Procedencia documental explícita. | Control de autenticidad y origen según fuente. |
| RF-V1-073 | AJUSTE PROPUESTO | «Legibilidad técnica» podía interpretarse como examen del contenido; la validación de archivo no es OCR. | Reformulación técnica sin extracción de texto ni reconocimiento. |
| RF-V1-074 | DECISION PENDIENTE | Asociación múltiple requiere definir documento compartible frente a evidencia privada. | Modelo lógico de acceso a documentos por cliente. |
| RF-V1-075 | CONFORME CON RESERVAS | Integridad del original y versiones. | Definir huella/retención en RNF y arquitectura. |
| RF-V1-076 | CONFORME CON RESERVAS | Autorización documental contextual. | Verificar permisos para procesamiento IA externo. |
| RF-V1-085 | CONFORME CON RESERVAS | Trazabilidad del LLM y revisión humana. | Evitar guardar entradas sensibles completas en logs. |
| RF-V1-087 | CONFORME CON RESERVAS | Revisión del abogado, separada de propuesta LLM. | Definir reasignación de validador. |
| RF-V1-089 | CONFORME CON RESERVAS | Confirmación/corrección/rechazo con original preservado. | Precisar significado de solicitar aclaración. |
| RF-V1-090 | CONFORME CON RESERVAS | Entrega de datos validados sin autopublicación. | Revisar contrato con G05. |

### 11.1 Cambios editoriales históricos realizados en v0.5

| RF | Tratamiento | Alcance del cambio |
|---|---|---|
| RF-V1-001 | Recuperación de original | Se sustituyó una reconstrucción restringida a «credenciales» por el texto original sobre mecanismo de autenticación configurado. |
| RF-V1-003 | Ajuste editorial propuesto | «Autorización del solicitante» no verificaba de manera precisa su identidad; riesgo de recuperación indebida. |
| RF-V1-033 | Ajuste editorial propuesto | Una adquisición puede vincularse con varios seguimientos; redacción singular era restrictiva. |
| RF-V1-037 | Ajuste editorial propuesto | Compartición técnica de adquisición no habilita consulta de contextos privados ajenos. |
| RF-V1-039 | Ajuste editorial propuesto | Trazabilidad debe admitir asociación con varios seguimientos; relación exclusiva era débil. |
| RF-V1-073 | Ajuste editorial propuesto | «Legibilidad técnica» podía interpretarse como examen del contenido; la validación de archivo no es OCR. |

Las seis modificaciones se registran con origen explícito. Los cinco ajustes a textos aún reconstruidos **no** se presentan como recuperación literal del original y permanecen pendientes de ratificación.

### 11.2 Riesgos transversales hallados en el cotejo semántico

- **Separación de adquisición y seguimiento:** una misma adquisición técnica puede utilizarse legítimamente en diferentes seguimientos; eso no autoriza a compartir historiales privados de clientes. Se han señalado RF-V1-033, RF-V1-037 y RF-V1-039 para adecuación conceptual.
- **Procesamiento documental:** la validación del archivo no puede convertirse en OCR o extracción de contenido. RF-V1-073 distingue comprobaciones técnicas de interpretación mediante el LLM multimodal.
- **Autenticación recuperable:** el RF-V1-001 original no obliga a una tecnología específica de contraseñas; RF-V1-003 deberá concretar el restablecimiento seguro del acceso.
- **Fuentes externas:** RF-V1-031 y RF-V1-048 no se consideran verificados con datos reales; requieren prueba de factibilidad y corpus de comparación.
- **Revisión jurídica:** RF-V1-065 y el tratamiento de G05 necesitan categorías y guardas de validación aprobadas.

### 11.3 Balance de esta revisión

| Categoría | Cantidad |
|---|---:|
| AJUSTE PROPUESTO | 5 |
| CONFORME CON RESERVAS | 42 |
| DECISION PENDIENTE | 8 |
| DEPENDENCIA EXTERNA | 2 |
| LITERAL RECUPERADO | 1 |
| **Total** | **58** |

**Límites:** el dictamen CONFORME CON RESERVAS acredita alineación conceptual con el modelo de negocio documentado, no identidad literal con una versión anterior ni aprobación de interesados. Los estados DECISIÓN PENDIENTE y DEPENDENCIA EXTERNA indican bloqueos específicos para cerrar o verificar requisitos.

### 11.4 Puerta de salida del cotejo literal pendiente

1. Recuperar o contrastar las 57 formulaciones aún reconstruidas con la fuente histórica original o ratificarlas expresamente como nueva redacción v0.5 si el original no está disponible.
2. Aprobar o ajustar las cinco reformulaciones editoriales indicadas; no sustituir silenciosamente el historial.
3. Resolver decisiones funcionales críticas: roles, cardinalidades, políticas, identidad de actuaciones, documentación compartida y revisión jurídica.
4. Validar los 150 pares requisito–criterio mediante ejemplos con entradas, resultados esperados y evidencia; los actuales son criterios iniciales.
5. Mantener separadas aprobación del catálogo, viabilidad técnica y pruebas de software ejecutadas.



## 12. AT-001 — Diseño preliminar de pruebas de aceptación por requisito reconstruido (v0.6)

**Estado:** 57 casos propuestos, no ejecutados. Su presencia no modifica la condición de cotejo original de los 57 requisitos. Cada caso aparece también dentro de la ficha RF correspondiente.

**Formato uniforme:** precondiciones, datos de entrada, procedimiento, resultado esperado y evidencia requerida.

### 12.1 Control de cobertura

| Segmento | RF reconstruidos | Casos AT diseñados | Estado |
|---|---:|---:|---|
| G01 | 7 | 7 | Diseño preliminar |
| G02 | 10 | 10 | Diseño preliminar |
| G03 | 10 | 10 | Diseño preliminar |
| G04 | 10 | 10 | Diseño preliminar |
| G05 | 10 | 10 | Diseño preliminar |
| G06 | 10 | 10 | Diseño preliminar |
| **Total** | **57** | **57** | **No ejecutados** |

### 12.2 Pruebas negativas transversales prioritarias

| ID prueba | RF cubierto | Condición adversa | Resultado esperado |
|---|---|---|---|
| NEG-V1-002 | RF-V1-002 | Sesión revocada intenta descargar documento | La descarga se deniega incluso con URL conocida |
| NEG-V1-005 | RF-V1-005 | Rol removido durante sesión vigente | La siguiente operación controlada resulta denegada |
| NEG-V1-009 | RF-V1-009 | Cuenta externa intenta cambiar de cliente por parámetro | No cambia el ámbito ni obtiene datos de otro cliente |
| NEG-V1-015 | RF-V1-015 | Mismo radicado en dos clientes | No se comparten novedades ni valoraciones privadas |
| NEG-V1-019 | RF-V1-019 | Planificador ejecuta seguimiento suspendido | No origina solicitud atribuible a seguimiento suspendido |
| NEG-V1-024 | RF-V1-024 | Dos adquisiciones fallidas, cero observaciones válidas | Cobertura no figura como actualizada |
| NEG-V1-028 | RF-V1-028 | Consulta individual sin finalidad autorizada | Se bloquea y conserva razón de denegación |
| NEG-V1-031 | RF-V1-031 | Conector simulado de fuente judicial | La prueba no se clasifica como integración judicial real |
| NEG-V1-034 | RF-V1-034 | Reintento con mismo resultado | No se generan observaciones o novedades duplicadas |
| NEG-V1-037 | RF-V1-037 | Adquisición de un proceso compartido | No revela asociaciones privadas de otro cliente |
| NEG-V1-048 | RF-V1-048 | Dos actuaciones con identidad ambigua | No se declaran idénticas automáticamente |
| NEG-V1-049 | RF-V1-049 | Observaciones con coberturas incompatibles | No se emite diferencia concluyente |
| NEG-V1-053 | RF-V1-053 | Repetir comparación equivalente | No duplica cambios detectados |
| NEG-V1-058 | RF-V1-058 | Reentrega de un cambio al mismo seguimiento | No duplica la novedad |
| NEG-V1-065 | RF-V1-065 | Analista publica valoración jurídica sin abogado | Se deniega publicación de conclusión no validada |
| NEG-V1-073 | RF-V1-073 | Archivo incompatible o corrupto | Se registra incompatibilidad sin ejecutar OCR |
| NEG-V1-076 | RF-V1-076 | Usuario B usa URL del documento de A | Se deniega acceso al recurso |
| NEG-V1-089 | RF-V1-089 | Campo del LLM incorrecto confirmado automáticamente | No puede considerarse validado sin acción humana |
| NEG-V1-090 | RF-V1-090 | Propuesta multimodal pendiente enviada a G05 | Se impide presentarla como dato confirmado o publicarla |
| NEG-V1-137 | RF-V1-137 | PDF modificado después de aprobación | Se exige nueva aprobación del artefacto |
| NEG-V1-134 | RF-V1-134 | Publicación retirada consultada por enlace | Se deniega consulta externa ordinaria |
| NEG-V1-153 | RF-V1-153 | Rectificación intenta sobreescribir decisión original | Se conserva historia y crea relación correctiva |

Las pruebas negativas refuerzan controles de segregación, idempotencia, comparabilidad, confidencialidad y autorización; se integrarán al plan de pruebas antes del desarrollo.

### 12.3 Matriz de decisiones de salida de los RF G01–G06

| ID | RF relacionados | Asunto | Criterio de cierre | Responsable a validar |
|---|---|---|---|---|
| CR-01 | RF-V1-002, 003 | Sesión revocada, recuperación y deshabilitación | Definir TTL, revocación y verificación de cuenta; RNF de seguridad | Responsable de identidad |
| CR-02 | RF-V1-005, 010, 127 | Matriz rol-permiso y aprobación propia | Ratificar roles acumulados y maker-checker | Organización operadora |
| CR-03 | RF-V1-006, 012, 048 | Identidad de cliente, proceso y actuación | Definir claves de negocio por dominio y fuente; corpus controlado | Responsable de dominio + técnico |
| CR-04 | RF-V1-017, 019, 020, 024 | Política, suspensión y continuidad de cobertura | Aprobar reactivación sin suponer cobertura continua | Coordinador funcional |
| CR-05 | RF-V1-025, 027, 028, 031 | Permiso de uso y compatibilidad de fuentes | POC fuente habilitada; no afirmar integración real por simulación | Responsable jurídico/técnico |
| CR-06 | RF-V1-033, 037, 039 | Adquisición compartida entre seguimientos | Definir reutilización técnica con aislamiento por cliente | Arquitectura + dueño de datos |
| CR-07 | RF-V1-040, 043–045, 048–053 | Identidad y comparabilidad determinística | Corpus y reglas de normalización reproducibles | Responsable técnico/dominio |
| CR-08 | RF-V1-056–069, 153 | Categorías de revisión y rectificación | Ratificar responsabilidades y efectos de rectificación | Responsable jurídico |
| CR-09 | RF-V1-071–076 | Custodia, procedencia y acceso documental | Políticas de documentos y autorización por finalidad | Responsable de seguridad/dominio |
| CR-10 | RF-V1-085, 087, 089, 090 | Confidencialidad de trazas LLM y validación humana | Aprobar retención de trazas y contrato de datos validados | Responsable de IA/jurídico |

### 12.4 Diagnóstico actualizado y cierre de versión

- **150 fichas activas** con estructura básica uniforme (93 textos recuperados, 57 textos reconstruidos).
- **57 casos de aceptación AT-V1-xxx** diseñados y vinculados directamente a los 57 RF reconstruidos.
- **22 escenarios negativos** propuestos para los principales riesgos transversales.
- **10 grupos de decisiones** agrupados para ratificación y POC.
- **No se recuperaron nuevas formulaciones literales.** El saldo de cotejo sigue siendo **57**.
- **No hay evidencia de pruebas ejecutadas, POC completadas ni aprobación formal.**

**Próxima actividad específica:** cotejar los 57 enunciados frente a fuentes históricas disponibles o ratificarlos explícitamente como redacciones nuevas. Paralelamente, transformar los 93 criterios iniciales restantes en casos AT verificables y formalizar la matriz RF–CU–ME–reglas–pruebas.

**Checkpoint actualizado:** RF-CAT-001 v0.6 es un catálogo maestro candidato con mayor verificabilidad y sin cambios de alcance, todavía no es una línea base v1.0 aprobada.


## 13. AT-002 — Casos de aceptación estructurados para los 93 RF con enunciado localizado (v0.7)

**Cobertura:** 93 casos `AT-V1-XXX` adicionales, insertados dentro de cada ficha recuperada. Se preservan los 57 casos preparados en v0.6 para enunciados reconstruidos, completando **150 casos de diseño preliminar para 150 RF activos**. Los escenarios negativos transversales existentes siguen como pruebas complementarias, no se cuentan como nuevas fichas.

Cada caso contiene: **precondiciones, datos de entrada, procedimiento, resultado esperado y evidencia**. Se diseñaron para cubrir operaciones normales y restricciones críticas, pero no representan ejecuciones ni conformidad de los interesados. Los escenarios usan fuentes simuladas, documentos sintéticos y estados controlados cuando corresponde; requieren concretar datos y oráculos por fuente/rol.

| Grupo | Casos previos (v0.6) | Casos adicionales (v0.7) | Total |
|---|---:|---:|---:|
| G01 | 7 | 3 | 10 |
| G02 | 10 | 4 | 14 |
| G03 | 10 | 5 | 15 |
| G04 | 10 | 6 | 16 |
| G05 | 10 | 6 | 16 |
| G06 | 10 | 9 | 19 |
| G07 | 0 | 14 | 14 |
| G08 | 0 | 15 | 15 |
| G09 | 0 | 18 | 18 |
| G10 | 0 | 13 | 13 |
| **Total** | **57** | **93** | **150** |


## 14. RF-TRZ-001 — Matriz individual de trazabilidad precisada (v0.8)

**Alcance del cierre documental:** Se reemplazaron 46 referencias genéricas por dependencias y reglas individualizadas: 15 en G03, 16 en G04 y 15 en G08. En los otros 104 requisitos se conserva la asociación registrada en v0.7. Esta mejora es **estructural y semántica propuesta**, no ratificación jurídica ni evidencia de ejecución. En particular, `DG03-02`, `RG04-17` a `RG04-24` e `INV-RF-01` a `INV-RF-12` se citan como decisiones/reglas candidatas discutidas en RT-RF-001/002 y deben cotejarse con su ficha maestra antes de aprobar una línea base.

| Requisito | Grupo | CU registrado | Modelo precisado | Regla / dependencia vinculada | Prueba | Texto | Estado de traza |
|---|---|---|---|---|---|---|---|
| RF-V1-001 | G01 | CU-01 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-001 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-002 | G01 | CU-01 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-002 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-003 | G01 | CU-01 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-003 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-004 | G01 | CU-02 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-004 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-005 | G01 | CU-02 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-005 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-006 | G01 | CU-17 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-006 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-007 | G01 | CU-17 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-007 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-008 | G01 | CU-17 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-008 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-009 | G01 | CU-17 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-009 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-010 | G01 | CU-01, CU-02, CU-17 | Política de identidad/autorización | Autorización contextual; segregación y estado de cliente | AT-V1-010 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-011 | G02 | CU-03 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-011 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-012 | G02 | CU-03 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-012 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-013 | G02 | CU-03 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-013 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-014 | G02 | CU-04 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-014 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-015 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-015 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-016 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-016 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-017 | G02 | CU-06 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-017 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-018 | G02 | CU-19 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-018 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-019 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-019 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-020 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-020 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-021 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-021 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-022 | G02 | CU-18 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-022 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-023 | G02 | CU-06 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-023 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-024 | G02 | CU-04, CU-06 | ME-01 | RG04-19 a RG04-24; seguimiento independiente por cliente | AT-V1-024 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-025 | G03 | CU-30 (propuesto) | ME-07 (mecanismo de fuente, propuesta) | DG03-02; RF-V1-026; RF-V1-027 | AT-V1-025 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-026 | G03 | CU-30 (propuesto) | ME-07 (mecanismo de fuente, propuesta) | DG03-02; RF-V1-030 | AT-V1-026 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-027 | G03 | CU-30 (propuesto) | ME-07 (mecanismo de fuente, propuesta) | DG03-02; RF-V1-026; RF-V1-030 | AT-V1-027 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-028 | G03 | CU-05, CU-28 | ME-02 (adquisición) | DG03-02; RF-V1-030; RF-V1-032 | AT-V1-028 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-029 | G03 | CU-05, CU-28 | ME-02 (adquisición) | DG03-02; RF-V1-017; RF-V1-030 | AT-V1-029 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-030 | G03 | CU-05, CU-28 | ME-02 (adquisición) | DG03-02; RF-V1-026; INV-RF-03 | AT-V1-030 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-031 | G03 | CU-05, CU-28 | ME-02 (adquisición) | DG03-02; RF-V1-030; RF-V1-039 | AT-V1-031 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-032 | G03 | CU-05, CU-28 | ME-02 (adquisición) | INV-RF-03; RF-V1-042; RF-V1-143 | AT-V1-032 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-033 | G03 | CU-05, CU-28 | ME-02 (adquisición) | INV-RF-01; RF-V1-039; RF-V1-110 | AT-V1-033 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-034 | G03 | CU-05, CU-28 | ME-02 (adquisición) | RF-V1-033; RF-V1-039; RF-V1-053 | AT-V1-034 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-035 | G03 | CU-05, CU-28 | ME-02 (adquisición) | INV-RF-03; RF-V1-032; RF-V1-038 | AT-V1-035 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-036 | G03 | CU-05, CU-28 | Incorporación manual G03 y ME-02 (solo trazabilidad; no resultado automático) | RF-V1-041; RF-V1-042; RF-V1-110 | AT-V1-036 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-037 | G03 | CU-28 | ME-02 (adquisición) | INV-RF-01; RF-V1-010; RF-V1-114 | AT-V1-037 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-038 | G03 | CU-28 | ME-02 (adquisición) | RF-V1-035; RF-V1-111; RF-V1-115 | AT-V1-038 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-039 | G03 | CU-28 | ME-02 (adquisición) | INV-RF-01; RF-V1-033; RF-V1-041 | AT-V1-039 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-040 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RF-V1-031; RF-V1-041; RG04-17 | AT-V1-040 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-041 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RF-V1-040; RF-V1-045 | AT-V1-041 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-042 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RG04-23; INV-RF-03 | AT-V1-042 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-043 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RF-V1-041; RF-V1-047 | AT-V1-043 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-044 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RF-V1-048 | AT-V1-044 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-045 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RF-V1-040; RF-V1-046; RF-V1-106 | AT-V1-045 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-046 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-18; RF-V1-045; INV-RF-04 | AT-V1-046 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-047 | G04 | CU-07 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RG04-23; RF-V1-042 | AT-V1-047 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-048 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RF-V1-044; RF-V1-047 | AT-V1-048 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-049 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RG04-23; RF-V1-047 | AT-V1-049 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-050 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-21; RG04-23; RF-V1-048 | AT-V1-050 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-051 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RG04-17; RG04-21; RF-V1-049 | AT-V1-051 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-052 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RF-V1-045; RF-V1-049; RF-V1-108 | AT-V1-052 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-053 | G04 | CU-08 | Modelo de observación y comparación G04 (sin máquina de estados independiente); ME-02 como procedencia | RF-V1-048; RF-V1-052; RF-V1-058 | AT-V1-053 | Pendiente de cotejo literal | **Precisada v0.8; no ratificada** |
| RF-V1-054 | G04 | CU-08 | Modelo de elegibilidad G04 por ME-01 (seguimiento) y salida hacia ME-03 | RG04-19; RG04-20; RG04-22; RG04-23; RG04-24 | AT-V1-054 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-055 | G04 | CU-08 | Modelo de elegibilidad G04 por ME-01 (seguimiento) y salida hacia ME-03 | RG04-23; RG04-24; RF-V1-054; RF-V1-058 | AT-V1-055 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-056 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-056 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-057 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-057 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-058 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-058 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-059 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-059 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-060 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-060 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-061 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-061 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-062 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-062 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-063 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-063 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-064 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-064 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-065 | G05 | CU-10 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-065 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-066 | G05 | CU-10 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-066 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-067 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-067 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-068 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-068 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-069 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-069 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-070 | G05 | CU-09 | ME-03 | ME-03; frontera analista–abogado; decisiones trazables | AT-V1-070 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-071 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-071 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-072 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-072 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-073 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-073 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-074 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-074 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-075 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-075 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-076 | G06 | CU-12 | Gestión documental | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-076 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-077 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-077 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-079 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-079 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-080 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-080 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-081 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-081 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-082 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-082 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-083 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-083 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-084 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-084 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-085 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-085 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-086 | G06 | CU-13 | ME-04A | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-086 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-087 | G06 | CU-14 | ME-04B | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-087 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-088 | G06 | CU-14 | ME-04B | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-088 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-089 | G06 | CU-14 | ME-04B | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-089 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-090 | G06 | CU-14 | ME-04B | DG06-01; sin OCR/extracción nativa independientes; validación humana | AT-V1-090 | Pendiente de cotejo literal | Registrada; ratificación pendiente |
| RF-V1-091 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-091 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-092 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-092 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-093 | G07 | CU-15, CU-19 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-093 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-094 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-094 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-095 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-095 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-096 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-096 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-097 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-097 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-098 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-098 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-099 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-099 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-100 | G07 | CU-15 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-100 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-101 | G07 | CU-15, CU-09 | ME-06 | RG07-01 a RG07-14; ME-06 | AT-V1-101 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-102 | G07 | CU-15 | Eventos de avisos internos | RG07-01 a RG07-14; ME-06 | AT-V1-102 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-103 | G07 | CU-15 | Eventos de avisos internos | RG07-01 a RG07-14; ME-06 | AT-V1-103 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-104 | G07 | CU-15 | Eventos de avisos internos | RG07-01 a RG07-14; ME-06 | AT-V1-104 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-105 | G08 | CU-11 | ME-01, ME-03 y ME-05 (consulta consolidada) | INV-RF-01; RF-V1-010; RF-V1-108 | AT-V1-105 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-106 | G08 | CU-07, CU-11 | ME-02 y observaciones de G04 (histórico) | INV-RF-03; RF-V1-040; RF-V1-045 | AT-V1-106 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-107 | G08 | CU-11 | ME-01, ME-02, ME-03 y ME-05 (secuencia histórica) | RG04-21; RF-V1-020; RF-V1-067 | AT-V1-107 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-108 | G08 | CU-11 | ME-03, ME-04B y ME-05 (relaciones de evidencia) | RF-V1-010; RF-V1-041; RF-V1-074; RF-V1-080 | AT-V1-108 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-109 | G08 | CU-11 | ME-01 y ME-03 (consulta por ámbito; no cambio de estados) | INV-RF-01; RF-V1-010; RF-V1-105 | AT-V1-109 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-110 | G08 | CU-16 | ME-01, ME-02, ME-03, ME-05 y ME-06 (eventos operativos) | RF-V1-067; RF-V1-113; RF-V1-131 | AT-V1-110 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-111 | G08 | CU-16 | ME-02, ME-04A y ME-05 (eventos técnicos) | RF-V1-002; RF-V1-035; RF-V1-113 | AT-V1-111 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-112 | G08 | CU-16 | Modelo de auditoría G08 (consulta de eventos; sin ME propia) | INV-RF-01; RF-V1-010; RF-V1-113 | AT-V1-112 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-113 | G08 | CU-16 | Modelo de auditoría G08 (integridad de eventos; sin ME propia) | RF-V1-110; RF-V1-111; RF-V1-114 | AT-V1-113 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-114 | G08 | CU-16 | Modelo de auditoría G08 (accesos sensibles; sin ME propia) | RF-V1-010; RF-V1-113; RF-V1-148 | AT-V1-114 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-115 | G08 | CU-04 | ME-01, ME-02, ME-03 y ME-06 (agregación) | RF-V1-010; RF-V1-116; RF-V1-117 | AT-V1-115 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-116 | G08 | CU-04 | ME-01, ME-02 y modelo de cobertura G04 | INV-RF-02; INV-RF-03; RF-V1-023; RF-V1-042 | AT-V1-116 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-117 | G08 | CU-04 | ME-03 y ME-06 (estadísticas de tratamiento) | RF-V1-059; RF-V1-068; RF-V1-101 | AT-V1-117 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-118 | G08 | CU-04 | Diccionario de indicadores G08 (pendiente; sin ME propia) | INV-RF-02; INV-RF-03; RF-V1-116; RF-V1-117 | AT-V1-118 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-119 | G08 | CU-11, CU-16 | Modelo de expediente y auditoría G08 (exportación; sin ME propia) | INV-RF-01; RF-V1-010; RF-V1-114; RF-V1-118 | AT-V1-119 | Localizado en contexto | **Precisada v0.8; no ratificada** |
| RF-V1-120 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-120 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-121 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-121 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-122 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-122 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-123 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-123 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-124 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-124 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-125 | G09 | CU-21, CU-20 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-125 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-126 | G09 | CU-21, CU-20 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-126 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-127 | G09 | CU-20 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-127 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-128 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-128 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-129 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-129 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-130 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-130 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-131 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-131 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-132 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-132 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-133 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-133 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-134 | G09 | CU-21 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-134 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-135 | G09 | CU-29 (propuesto) | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-135 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-136 | G09 | CU-29 (propuesto) | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-136 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-137 | G09 | CU-29 (propuesto), CU-27 | ME-05 | RG09-01 a RG09-17; aprobación de artefacto exacto | AT-V1-137 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-138 | G10 | CU-22 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-138 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-139 | G10 | CU-22 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-139 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-140 | G10 | CU-23 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-140 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-141 | G10 | CU-23 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-141 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-142 | G10 | CU-24 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-142 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-143 | G10 | CU-24 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-143 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-144 | G10 | CU-25 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-144 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-145 | G10 | CU-25 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-145 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-146 | G10 | CU-25 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-146 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-147 | G10 | CU-26 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-147 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-148 | G10 | CU-26 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-148 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-149 | G10 | CU-27 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-149 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-150 | G10 | CU-27 | ME-01 y ME-05 (consulta externa) | RG10-01 a RG10-16; solo contenido habilitado | AT-V1-150 | Localizado en contexto | Registrada; ratificación pendiente |
| RF-V1-153 | G05 | CU-09, CU-10, CU-21 | ME-03 (rectificación vinculada) y ME-05 | Decisiones correctivas no sobrescribibles; RG09-09 a RG09-12 | AT-V1-153 | Localizado en contexto | Registrada; ratificación pendiente |

### 14.1 Control de reglas y referencias

| Tipo de referencia | Uso y advertencia |
|---|---|
| `RF-V1-XXX` | Obligación funcional identificable en este mismo catálogo; la vinculación requiere ratificación semántica. |
| `DG03-02` | Decisión candidata de habilitación de fuentes documentada en RT-RF-002; **no equivale a autorización real de integración**. |
| `RG04-17` a `RG04-24` | Reglas candidatas de comparación, línea base y cobertura de RT-RF-002; formalizar en RF-RN-001. |
| `INV-RF-01` a `INV-RF-12` | Invariantes transversales discutidos en RT-RF-001; conservar sus definiciones originales y ratificar correspondencias. |
| `ME-07` | Modelo de estados candidato, no aprobado; se propone especificación verificable en §16. |
| `ME-03`, `ME-04A`, `ME-05` | Propuesta de sincronización en §16; no se modifican los RF existentes ni se declara una máquina implementada. |

### 14.2 Cotejo del número de referencias generales

El diagnóstico v0.7 señaló **45** referencias generales. La revisión exhaustiva de la matriz mostró **46** filas: **15 G03 + 16 G04 + 15 G08**. Ese conteo se corrige en v0.8; las 46 poseen ahora referencias específicas y quedan **pendientes de ratificación semántica**. Una dependencia específica puede ser **provisional** y no equivale a evidencia validada.

## 15. Casos de uso propuestos CU-29 y CU-30 — Especificación candidata

> **Control de nomenclatura:** estas dos fichas formalizan **propuestas**, no la aprobación de los números `CU-29` y `CU-30`. Antes de adoptar los identificadores, cotejar el inventario histórico para descartar una asignación anterior —especialmente CU-29, que en materiales previos aparece asociado genéricamente a informes—. La consulta externa de informes sigue siendo **CU-27**; la preparación interna se distingue como el caso propuesto aquí.

### CU-29 (propuesto) — Preparar y someter informe consolidado de vigilancia

| Campo | Especificación candidata |
|---|---|
| Objetivo | Preparar un informe para un solo cliente, delimitar periodo y seguimientos, registrar cobertura, generar PDF final candidato y someter **ese mismo artefacto** a autorización de G09. |
| Actor principal | Usuario interno autorizado para preparar informes (según política de G01/G09). |
| Actores participantes | Coordinador con permiso de aprobación; sistema de publicación. El cliente externo consulta después vía CU-27. |
| Disparador | Solicitud autorizada de informe de vigilancia para un cliente y un periodo. |
| Precondiciones | Cliente habilitado según política, seguimientos pertenecientes al cliente, información de procedencia y cobertura disponible o limitaciones explícitas. |
| RF principales | RF-V1-135, RF-V1-136, RF-V1-137. |
| RF complementarios | RF-V1-120–129, RF-V1-130, RF-V1-131, RF-V1-134, RF-V1-149–150, RF-V1-114. |
| Modelo | ME-05 por versión de publicación. |
| Postcondición exitosa | PDF final aprobado y efectivamente publicado para su cliente y versión; posteriormente disponible para CU-27. |
| Postcondición alternativa | Borrador o versión rechazada, autorizada pendiente de publicación o incidente registrado; nunca publicación aparente. |

**Flujo principal (propuesto):**

1. El preparador autorizado selecciona exactamente un cliente y un periodo de vigilancia, así como los seguimientos elegibles de ese mismo cliente.
2. El sistema recupera datos de fuentes y observaciones autorizadas, indicando fecha de corte, cobertura, intentos fallidos e incompletos; evita equiparar ausencia de publicaciones con ausencia de cambios.
3. El preparador estructura el informe y selecciona referencias y anexos permitidos; el sistema valida la consistencia de destinatarios y procedencia.
4. El sistema genera un **PDF final candidato**, identifica su contenido y anexos y lo congela como versión revisable.
5. El preparador envía la versión exacta a autorización y ME-05 avanza a **Pendiente autorización**.
6. El coordinador autorizado comprueba el PDF final y aprueba esa versión específica, dejando evidencia de decisión.
7. El sistema publica únicamente el artefacto autorizado y confirma que está externamente disponible para el cliente.
8. G10 presenta el informe vigente al usuario externo autorizado mediante CU-27.

**Alternativas y excepciones:**

- **ALT-29-01:** si un seguimiento no pertenece al cliente, se rechaza su incorporación; no se mezcla cartera entre clientes.
- **ALT-29-02:** si existe información insuficiente o adquisición fallida, se indica expresamente la limitación; no se atribuye cobertura ficticia.
- **ALT-29-03:** si el coordinador rechaza la versión, se conserva el rechazo y se elabora otra versión; no se altera la rechazada.
- **ALT-29-04:** si falla la publicación, el artefacto queda **Autorizado**, con incidente registrado y reintento idempotente permitido.
- **ALT-29-05:** si cambia el PDF o anexo tras la autorización, exige nueva versión y nueva autorización.

**Aceptación mínima:** `AT-V1-135`, `AT-V1-136`, `AT-V1-137`, `AT-V1-125`, `AT-V1-127`, `AT-V1-129`, `AT-V1-150`; añadir ensayo de PDF modificado y de cobertura incompleta. **Estado:** propuesto; ratificación de actores/segregación pendiente.

### CU-30 (propuesto) — Administrar y habilitar fuentes judiciales

| Campo | Especificación candidata |
|---|---|
| Objetivo | Registrar fuentes y mecanismos, configurar condiciones autorizadas, habilitarlos, suspenderlos o deshabilitarlos con historial y verificaciones de uso. |
| Actor principal | Administrador o responsable interno **expresamente habilitado para gobierno de fuentes**. |
| Actores participantes | Responsable de cumplimiento/seguridad cuando aplique; sistema de adquisición. |
| Disparador | Alta, modificación o decisión de habilitación de un mecanismo por fuente y modalidad. |
| Precondiciones | Identidad y alcance de la fuente documentados; criterios de autorización, restricciones, cobertura y evidencia de factibilidad disponibles cuando se pretenda habilitar. |
| RF principales | RF-V1-025, RF-V1-026, RF-V1-027. |
| RF complementarios | RF-V1-030, RF-V1-031, RF-V1-032, RF-V1-035, RF-V1-039, RF-V1-110–114. |
| Modelo | ME-07 **propuesta** para el mecanismo de fuente; adquisiciones individuales permanecen en ME-02. |
| Postcondición exitosa | Mecanismo habilitado/deshabilitado según decisión documentada y trazable; su estado determina la admisibilidad de nuevas adquisiciones. |
| Condición externa | La ficha no demuestra que CPNU, SAMAI u otra fuente admita automatización real; requiere evaluación permitida y evidencias. |

**Flujo principal (propuesto):**

1. El responsable registra la fuente y un mecanismo concreto de consulta con modalidad, alcance y restricciones.
2. El responsable incorpora la documentación de autorización y factibilidad aplicable a esa fuente y mecanismo.
3. El sistema valida la completitud de las condiciones requeridas y registra la configuración identificable.
4. Una persona habilitada aprueba o rechaza la habilitación según política vigente.
5. Si se aprueba, el mecanismo pasa a **Habilitado**, conservando identidad de configuración y decisión.
6. Antes de cada adquisición, G03 vuelve a comprobar que la operación esté habilitada y permitida.
7. Las suspensiones/deshabilitaciones posteriores impiden nuevas adquisiciones y registran causa y responsable.

**Alternativas y excepciones:**

- **ALT-30-01:** aprobación documental incompleta: el mecanismo sigue registrado, **no habilitado**.
- **ALT-30-02:** restricciones cambiantes o revocación: se suspende o deshabilita el mecanismo y se bloquean nuevas operaciones; preservar trazabilidad.
- **ALT-30-03:** una consulta ya iniciada debe tratarse según su política de cancelación segura y registro de resultado; no falsear una adquisición completada.
- **ALT-30-04:** una fuente puede tener varios mecanismos/modalidades con condiciones y estados independientes; habilitar uno no habilita todos.

**Aceptación mínima:** `AT-V1-025`, `AT-V1-026`, `AT-V1-027`, `AT-V1-030`, `AT-V1-031`; pruebas de fuente sin autorización, revocación y bloqueo de ejecución. **Estado:** propuesto; pendiente de validación de gobierno y factibilidad de fuentes.

## 16. Sincronización de modelos ME — Transiciones candidatas y guardas

Esta sección expresa **transiciones propuestas para revisión**; no modifica directamente el modelo histórico aprobado (si lo hubiera), ni crea motores de estados ejecutables. Cualquier estado o transición se ratificará contra la definición formal de ME-03/04A/05/07 y los criterios de aceptación asociados.

### 16.1 ME-03 — Novedad (revisión, tratamiento y rectificación)

**Estados conocidos:** `Pendiente revisión operativa`, `En revisión operativa`, `Pendiente información`, `Pendiente revisión jurídica`, `Tratamiento definido`, `En seguimiento`, `Cerrada`, `Descartada`. Las formas de transición siguientes son propuestas para conciliación con G05.

| Origen | Destino | Guarda y efecto mínimo | Trazas |
|---|---|---|---|
| Pendiente revisión operativa | En revisión operativa | Analista autorizado inicia revisión; registrar responsable y fecha. | RF-V1-059; RF-V1-068 |
| En revisión operativa | Pendiente información | Falta evidencia suficiente; registrar motivo y solicitud. | RF-V1-061; RF-V1-062 |
| Pendiente información | En revisión operativa | Se recibe o incorpora evidencia pertinente; conservar historial. | RF-V1-061; RF-V1-067 |
| En revisión operativa | Pendiente revisión jurídica | Exige criterio jurídico; abogado habilitado asignado y motivo. | RF-V1-065; RF-V1-066 |
| Pendiente revisión jurídica | Tratamiento definido | Abogado registra valoración suficiente y revisión obligatoria satisfecha. | RF-V1-066; RF-V1-067 |
| En revisión operativa | Tratamiento definido | Tratamiento basado en hechos objetivos revisados, si categoría permite ruta no jurídica. | RF-V1-062; RF-V1-068 |
| En revisión operativa | Descartada | Causa válida registrada, permisos y evidencia; nunca borrar cambio de origen. | RF-V1-064; RF-V1-067 |
| Tratamiento definido | En seguimiento | Acciones/tareas que correspondan definidas y trazadas. | RF-V1-069; RF-V1-091 |
| En seguimiento | Cerrada | Tratamiento y revisiones obligatorias satisfechas; tareas obligatorias cumplidas o excepción autorizada. | RF-V1-070; RF-V1-101 |

**No hacer:** `Cerrada → En revisión operativa` y `Descartada → En revisión operativa` como transiciones ordinarias. Una corrección posterior se tramita como **registro de rectificación vinculado** (`RF-V1-153`), conservando la decisión terminal y activando revisiones/tareas/publicaciones correctivas mediante G05/G07/G09. La política de reabertura/rectificación requiere validación del dominio.

### 16.2 ME-04A — Ejecución de análisis multimodal documental

| Origen | Destino | Guarda y efecto mínimo | Trazas |
|---|---|---|---|
| Pendiente | ValidandoDocumento | Solicitud identificable y usuario con autorización de análisis. | RF-V1-077; RF-V1-079 |
| ValidandoDocumento | ProcesandoLLM | Proveedor/finalidad/documento compatibles y habilitados para tratamiento externo. | RF-V1-079; RF-V1-081; RF-V1-082 |
| ValidandoDocumento | Bloqueada | Falta habilitación; no transmitir documento. | RF-V1-081 |
| ValidandoDocumento | Fallida | Formato o entrada incompatible; registrar causa. | RF-V1-079; RF-V1-086 |
| ProcesandoLLM | PropuestaDisponible | Respuesta estructurada comprobable aceptada como **propuesta**, no como validación jurídica. | RF-V1-083; RF-V1-084; RF-V1-085 |
| ProcesandoLLM | Fallida | Error, timeout o esquema inválido; registrar intento. | RF-V1-084; RF-V1-086 |
| Pendiente | Cancelada | Cancelación permitida antes del procesamiento. | RF-V1-086 |

**Invariantes:** sin OCR propio, sin extracción nativa separada, sin fine-tuning; el documento original se conserva; cada nuevo intento es un registro identificable; `PropuestaDisponible` no equivale a validación en ME-04B. No se determinan reintentos o cancelaciones en curso sin decisión expresa.

### 16.3 ME-05 — Publicación por versión

| Origen | Destino | Guarda y efecto mínimo | Trazas |
|---|---|---|---|
| Borrador | Pendiente autorización | Contenido y anexos congelados, destinatario correcto, PDF final candidato generado si aplica. | RF-V1-125; RF-V1-126; RF-V1-137 |
| Pendiente autorización | Rechazada | Decisión motivada del aprobador habilitado; versión rechazada terminal, corrección en otra versión. | RF-V1-127; RF-V1-131 |
| Pendiente autorización | Autorizada | Aprobación de versión exacta, guardas de segregación comprobadas. | RF-V1-127; RF-V1-128 |
| Autorizada | Publicada | Confirmación de disponibilidad efectiva de la **misma versión** para el destinatario. | RF-V1-129; RF-V1-134 |
| Publicada | Retirada | Decisión y revocación externa confirmadas, historial conservado. | RF-V1-133; RF-V1-134 |
| Publicada | Reemplazada | Una nueva versión quedó efectivamente publicada; referencia anterior se conserva. | RF-V1-132; RF-V1-134 |

**Excepciones clave:** publicación fallida deja versión **Autorizada**, registra intento y permite reintento idempotente; intento de retirada fallido **no se registra como retirada confirmada**. Una nueva versión autorizada no retira automáticamente la anterior antes de estar publicada. Se conserva un máximo de una versión **vigente** por publicación y destinatario conforme a la política ratificada.

### 16.4 ME-07 — Estado del mecanismo de adquisición por fuente (propuesta nueva)

La unidad de estado es **mecanismo/modalidad de una fuente**, no una respuesta de consulta ni el resultado de ME-02. La fuente registrada puede admitir múltiples mecanismos con estados distintos.

| Origen | Destino | Guarda y efecto mínimo | Trazas |
|---|---|---|---|
| Registrada / No habilitada | Habilitada | Documentación de autorización, cobertura, restricciones y configuración validada; decisión registrada. | RF-V1-025; RF-V1-026; RF-V1-027 |
| Habilitada | Suspendida | Incidencia o restricción temporal, motivo, responsable y bloqueo de nuevas adquisiciones. | RF-V1-026; RF-V1-030 |
| Habilitada | Deshabilitada | Decisión de retirada/revocación; nuevas adquisiciones bloqueadas. | RF-V1-026; RF-V1-030 |
| Suspendida | Habilitada | Nueva comprobación de habilitación y restricciones; autorización registrada. | RF-V1-026; RF-V1-030 |
| Suspendida | Deshabilitada | Revocación o baja, responsable y causa. | RF-V1-026 |
| Deshabilitada | Habilitada (nueva versión de configuración) | Solo después de nueva evaluación/decisión documentada; no reactivación silenciosa. | RF-V1-025; RF-V1-026; RF-V1-027 |

**Condición no resuelta:** la factibilidad y autorización de CPNU u otras fuentes debe demostrarse antes de habilitar una modalidad real. Un mecanismo deshabilitado impide *nuevas* adquisiciones; la cancelación de operaciones ya iniciadas exige política adicional. `ME-07` no está aprobado.

## 17. Protocolo de cotejo y ratificación de 57 enunciados reconstruidos

El saldo permanece en **57**. RF-V1-001 ya fue recuperado en v0.5, pero ello no equivale a aprobación formal. La ausencia del texto original para un RF **no se subsana inventando una fuente**: debe cotejarse con la formulación histórica recuperable, o ratificarse explícitamente el texto reconstruido como **nueva formulación**, dejando versión, actor decisor, fecha y criterio de aceptación.

### 17.1 Método de ratificación

1. Localizar el texto anterior, su versión y procedencia o documentar su no disponibilidad.
2. Comparar el texto reconstruido con objetivos y límites del TO-BE y decisiones de RT-RF-002/003.
3. Registrar una disposición: **ratificar como nuevo texto**, **corregir**, **fusionar con otro RF**, **diferir**, o **excluir**. No adoptar por silencio.
4. Cotejar actor, permiso, prioridad, límites y criterio de aceptación; actualizar CU/ME/AT y registrar diffs.
5. Registrar validador competente y evidencia de decisión; mantener la condición de pendiente hasta contar con ella.

### 17.2 Matriz individual de ratificación pendiente

| RF | Grupo | Nombre del requisito | Responsable sugerido de validación | Estado textual | Disposición | Evidencia requerida |
|---|---|---|---|---|---|---|
| RF-V1-002 | G01 | Gestionar sesiones | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-003 | G01 | Recuperar acceso | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-004 | G01 | Gestionar usuarios internos | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-005 | G01 | Administrar roles y permisos | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-006 | G01 | Registrar clientes | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-007 | G01 | Gestionar datos de clientes | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-009 | G01 | Gestionar cuentas externas de clientes | Responsable de producto / seguridad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-011 | G02 | Registrar procesos judiciales | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-013 | G02 | Consultar proceso judicial | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-014 | G02 | Consultar cartera interna | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-015 | G02 | Vincular proceso a cliente | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-017 | G02 | Configurar política de vigilancia | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-018 | G02 | Asignar responsables al seguimiento | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-019 | G02 | Suspender seguimiento | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-021 | G02 | Finalizar seguimiento | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-022 | G02 | Consultar estado y antecedentes del seguimiento | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-024 | G02 | Comprobar cumplimiento de política de vigilancia | Coordinador de vigilancia / analista | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-025 | G03 | Registrar fuentes judiciales | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-027 | G03 | Configurar mecanismos de fuente | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-028 | G03 | Solicitar consulta individual | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-031 | G03 | Ejecutar adquisición judicial | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-033 | G03 | Registrar intentos y resultados | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-034 | G03 | Gestionar reintentos de adquisición | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-035 | G03 | Gestionar errores de adquisición | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-037 | G03 | Consultar ejecuciones de adquisición | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-038 | G03 | Registrar y atender incidencias de adquisición | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-039 | G03 | Conservar trazabilidad de adquisición | Responsable de integración y fuentes | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-040 | G04 | Registrar observaciones judiciales | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-041 | G04 | Conservar procedencia de observaciones | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-043 | G04 | Normalizar representaciones judiciales | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-044 | G04 | Identificar actuaciones judiciales | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-045 | G04 | Conservar historial inmutable de observaciones | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-048 | G04 | Determinar identidad de actuaciones | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-049 | G04 | Comparar observaciones sucesivas | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-051 | G04 | Detectar modificaciones entre observaciones | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-052 | G04 | Registrar diferencias detectadas | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-053 | G04 | Evitar duplicación de cambios | Analista + responsable del comparador | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-056 | G05 | Crear novedad candidata | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-057 | G05 | Asociar novedad y seguimiento | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-058 | G05 | Evitar duplicación de novedades | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-059 | G05 | Iniciar revisión operativa | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-060 | G05 | Asignar responsables de novedades | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-061 | G05 | Consultar novedades para revisión | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-063 | G05 | Registrar observaciones de revisión | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-065 | G05 | Escalar novedad a revisión jurídica | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-067 | G05 | Conservar historial de decisiones | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-069 | G05 | Definir tratamiento | Coordinador + asesoría jurídica | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-071 | G06 | Incorporar documentos judiciales | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-072 | G06 | Verificar procedencia documental | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-073 | G06 | Validar condiciones técnicas del documento | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-074 | G06 | Asociar documento al expediente | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-075 | G06 | Conservar integridad documental | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-076 | G06 | Controlar acceso a documentos | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-085 | G06 | Registrar trazabilidad de propuesta IA | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-087 | G06 | Asignar validación humana | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-089 | G06 | Confirmar, corregir o rechazar propuesta | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |
| RF-V1-090 | G06 | Entregar datos validados al tratamiento | Responsable documental + jurídico/privacidad | Reconstruido; cotejo pendiente | **Sin decisión** | Texto histórico verificable o acta de ratificación de nueva redacción |

### 17.3 Controles por decisión de negocio

| Punto de control | RF afectados | Aprobación/documento mínimo | Estado |
|---|---|---|---|
| Permisos, estado de cliente y acceso histórico | 008–010, 019–020, 134, 138–150 | Política de roles/cliente y prueba de segregación | Pendiente |
| Regla de identidad, comparabilidad y reactivación | 012, 020, 023, 042–055 | Corpus etiquetado; reglas de fuente y línea base | Condicionada a datos |
| Fuente y mecanismo permitido | 025–031 | Ficha de factibilidad, términos/autorización y ensayo controlado | Condicionada externamente |
| Contenido que requiere revisión jurídica | 062, 065–070, 122, 125, 127 | Matriz de categorías y responsable de aprobación | Pendiente de dominio |
| Rectificación y efectos sobre comunicaciones | 153, 132–134 | Procedimiento y escenarios de corrección del registro original | Pendiente de dominio |
| Proveedor y tratamiento de documentos | 077, 079–090 | POC multimodal y condiciones de tratamiento autorizadas | Condicionada externamente |
| Agregado de indicadores y retención | 110–119, 139, 143 | Diccionario de indicadores y política de conservación | Pendiente RNF/política |
| Aprobación propia y rechazo | 126–129 | Matriz de segregación de funciones | Pendiente de dominio |
| Asignación definitiva de CU-29 / CU-30 | 025–027, 135–137 | Inventario de CU y ficha ratificada sin colisión | Pendiente |
| Absorciones de RF-V1-151 y RF-V1-152 | 114, 134 | Control de cambios aprobado | Pendiente |

## 18. Auditoría de v0.8, control de cambios y checkpoint

### 18.1 Balance documental

- **150/150** RF activos con ficha y AT diseñado, sin ejecución de software.
- **46/46** referencias generales identificadas en G03/G04/G08 ahora **individualizadas** en fichas y en matriz, aún no ratificadas semánticamente.
- **93** enunciados localizados históricamente; **57** reconstruidos permanecen pendientes de cotejo o ratificación explícita.
- **CU-29 y CU-30** especificados como **propuestas** de caso de uso; números y contenido por ratificar con inventario de CU.
- **ME-03, ME-04A y ME-05** sincronizados mediante tablas de transición **candidatas**; **ME-07** formulada como propuesta de gobierno del mecanismo, no aprobada.
- **0** pruebas ejecutadas; **0** POC verificadas en esta actividad; **0** decisiones externas/legales aprobadas por esta revisión.

### 18.2 Cambios de versión

| Código | Cambio v0.8 | Condición |
|---|---|---|
| CHG-012 | Matriz de 150 filas regenerada con 46 referencias específicas en G03/G04/G08. | Mejora documental, ratificación pendiente. |
| CHG-013 | CU-29 y CU-30 propuestos descritos con actores, flujos, excepciones y pruebas. | No adoptar números hasta revisar inventario histórico. |
| CHG-014 | Tablas de guardas/transiciones propuestas para ME-03, ME-04A, ME-05 y ME-07. | Sujeto a aprobación funcional. |
| CHG-015 | Protocolo y matriz de 57 RF reconstruidos pendientes de cotejo/ratificación. | Ninguna ratificación automática. |
| CHG-016 | Corrige el conteo v0.7 de 45 a 46 asociaciones generales. | Auditable mediante matriz. |

### 18.3 Puertas de salida para línea base v1.0

| Puerta | Condición | Estado al cierre v0.8 |
|---|---|---|
| PB-01 | 150 fichas RF con campos y caso AT diseñado | Cubierta documentalmente; sin ejecución |
| PB-02 | Referencias CU/ME/RN precisas y validadas | 46 precisadas; validación semántica pendiente |
| PB-03 | Ratificación 57 reconstrucciones | **No**: 57 pendientes |
| PB-04 | Aprobación de CU-29/CU-30 y modelos ME revisados | **No**: solo propuestas documentadas |
| PB-05 | Ratificación de prioridades, roles, condiciones de aprobación y absorciones | **No** |
| PB-06 | Pruebas de factibilidad judicial y LLM permitidas | **No** |
| PB-07 | RNF críticos integrados a ERS | **No**; actividad RNF-001 pendiente |
| PB-08 | Aprobación formal de la línea base | **No** |

### 18.4 Próximos pasos recomendados

1. **RF-DEC-001:** realizar taller de ratificación de las decisiones de negocio (permisos, revisión jurídica, rectificación, autoaprobación, historia).
2. **RF-RN-001 / RF-TRZ-001:** formalizar definiciones de reglas citadas (`DG03`, `RG04`, `INV-RF`) y validar las 46 asociaciones precisadas.
3. **Cotejo/ratificación G01–G06:** resolver las 57 fichas con acta de decisión o evidencia histórica, sin reescribirlas silenciosamente.
4. **Formalizar CU-29/CU-30 y ME-03/04A/05/07:** comprobar nomenclatura y aprobar flujos/guardas.
5. **RNF-001 + POC de fuentes/LLM en paralelo:** definir umbrales y evaluar acceso autorizado e integración multimodal; respetar privacidad.
6. **RF-CAT-001 v1.0 / ERS-001:** elevar a línea base solo tras aprobar pendientes críticos; luego ARC-001, DAT-001, API/UX y DEV-PLAN-001.

**Checkpoint de continuidad:** RF-CAT-001 **v0.8 candidata**; usar como documento maestro más reciente. No rehacer G01–G10, no introducir OCR/extraíbles nativos independientes ni afirmar integraciones verificadas. Los textos reconstruidos son candidatos pendientes y los vínculos específicos son propuestas de trazabilidad, no validaciones por expertos. El primer paso siguiente es el taller de decisiones y ratificación de reglas/57 fichas, mientras se inicia RNF-001 y pruebas de factibilidad.
