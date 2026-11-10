---
documento: RF-DEC-001
nombre: Registro de decisiones funcionales y reglas de negocio
version: 0.4-propuestas-autores-paquete-A-diseno-paquete-B
fecha_corte: '2026-11-09'
proyecto: Plataforma LegalTech de vigilancia de carteras de procesos judiciales
documentos_base:
  - RF-DEC-001_decisiones_funcionales_LegalTech_v0.3_paquete_A.md
  - RF-CAT-001_catalogo_maestro_LegalTech_v0.8_cierre_trazabilidad.md
  - RF-VAL-001
inventario_rf:
  activos: 150
  identificadores: RF-V1-001 a RF-V1-153
  excluido: RF-V1-078
  absorbidos:
    RF-V1-151: RF-V1-134
    RF-V1-152: RF-V1-114
  reconstruidos_pendientes_de_cotejo: 57
estado: Selecciones de autores DEC-01/03/04 documentadas; paquete B DEC-08/09 diseñado; pendiente validación de dominio
---

# RF-DEC-001 v0.4 — Decisiones de autores (Paquete A) y especificación propuesta (Paquete B)

**Proyecto:** plataforma de software para la vigilancia trazable y escalable de carteras de procesos judiciales.  
**Corte de actualización:** 9 de noviembre de 2026.  
**Entrada:** RF-CAT-001 v0.8 y RF-DEC-001 v0.3.  
**Resultado:** selección expresa de los autores para DEC-01, DEC-03 y DEC-04; formalización operativa propuesta para DEC-08 y DEC-09; conserva el registro de 18 decisiones y los bloqueos de validación.

> **Advertencia sobre evidencia:** formular y contrastar una política no equivale a aprobarla. Esta versión **sí registra la selección explícita de los autores del proyecto** para DEC-01/03/04, pero **no afirma** aprobación del cliente jurídico, coordinador, tutor, responsable de privacidad, proveedor ni fuente judicial. Los responsables, fechas, firmas y evidencias de ratificación permanecen vacíos hasta la decisión real. Los 57 RF reconstruidos continúan pendientes de cotejo literal o ratificación como nueva formulación.

## 1. Propósito de la revisión

El objetivo de v0.2 es convertir las decisiones abiertas de v0.1 en políticas ejecutables para el diseño del software, especialmente en tres dominios: **(A) autorización y acceso histórico**, **(B) revisión jurídica y publicación**, y **(C) rectificaciones, tareas y estados terminales**. Se conservan sin cambio las reglas previamente acordadas sobre adquisición permitida, comparación determinística, LLM multimodal, identidad del contenido aprobado e aislamiento entre clientes.

Se emplean cuatro estados de control:

- **AC — Acordada previamente:** respaldada por decisiones explícitas de G01–G10 y RT-RF-001/002/003.
- **SA — Selección de autores:** alternativa escogida expresamente por los autores para la propuesta de V1; no equivale a aprobación de interesados externos.
- **PR — Política propuesta:** resolución candidata estructurada en esta versión, aún no seleccionada por los autores o por ratificar con el responsable designado.
- **CE — Condicionada a evidencia:** exige resultado verificable externo o prueba técnica antes de habilitar el comportamiento real.
- **PD — Pendiente de definición:** existe una alternativa material que debe resolver un interesado facultado.

La aprobación debe ser **por decisión y versión**, no masiva por simple aceptación de la siguiente etapa del proyecto.

## 2. Síntesis ejecutiva de las 18 decisiones

| Decisión | Área | Política de referencia para v0.2 | Estado | Ratificador requerido |
|---|---|---|---|---|
| DEC-01 | Autorización contextual | Ámbitos configurables por cuenta, dentro de un único cliente; denegación por defecto y control por recurso | AC (principio); **SA** (alcance configurable) | Producto y seguridad |
| DEC-02 | Cuentas externas | Una cuenta externa por cliente en V1; múltiples cuentas por cliente | AC | Producto |
| DEC-03 | Suspensión del cliente | Bloquear portal ordinario mientras dure la suspensión; conservar historial sin alterar en bloque los seguimientos | **SA** | Producto, operación, privacidad |
| DEC-04 | Acceso histórico | **Cerrar acceso externo al finalizar cada seguimiento**; preservar el histórico interno sin retirada automática | **SA**; reglas de informes mixtos por validar | Producto, privacidad y jurídico |
| DEC-05 | Fuente autorizada | No ejecutar modalidades sin habilitación documentada | AC/CE | Titular de la fuente y cumplimiento |
| DEC-06 | Referencias comparables | Separar observación, línea base por seguimiento y elegibilidad | AC/CE | Operación y equipo técnico |
| DEC-07 | Reactivación | Registrar brechas y no afirmar cobertura recuperada sin evidencia | PR | Operación jurídica |
| DEC-08 | Intervención jurídica | Valoración jurídica obligatoria para interpretación y consecuencias legales | AC (principio); PR (categorías) | Abogado responsable |
| DEC-09 | Doble control | Preparador y aprobador de una misma versión deben ser personas distintas | PR | Coordinación y seguridad |
| DEC-10 | Rectificaciones | Registro correctivo vinculado sin sobrescribir decisiones finales | PR | Operación y abogado |
| DEC-11 | Obligaciones/tareas | Cancelar tarea no equivale a satisfacer obligación; excepción explícita | AC (principio); PR (excepciones) | Operación y jurídico |
| DEC-12 | LLM documental | LLM multimodal sin OCR/nativo independientes; transmisión autorizada | AC/CE | Producto, privacidad y jurídico |
| DEC-13 | Publicación | Aprobar artefacto final verificable; publicar solo versión autorizada | AC (principio); PR (manejo de fallos) | Coordinación |
| DEC-14 | Informe consolidado | Autorizar informe íntegro, incluso cuando incluya datos no publicados separadamente | AC | Coordinación y jurídico |
| DEC-15 | Indicadores | Definiciones, población y fecha de corte; no confundir intentos con cobertura | AC (principio); PD (fórmulas) | Producto/operación |
| DEC-16 | Auditoría/retención | Accesos internos y externos auditables; plazos de retención pendientes | AC (principio); PD (retención) | Seguridad/privacidad |
| DEC-17 | Casos y modelos | CU-29, CU-30 y ME-07 como propuestas individualizadas | PR | Equipo de requisitos/tutor |
| DEC-18 | Numeración | 078 excluido, 151→134, 152→114 y 153 candidato nuevo | PR; 078 AC | Equipo de requisitos/tutor |

**Regla de clasificación:** una decisión puede contener un principio previo acordado y una operacionalización nueva seleccionada por los autores. SA registra una decisión de diseño de los autores; no acredita aceptación jurídica, contractual, de seguridad o de privacidad. DEC-08 y DEC-09 siguen siendo propuestas hasta su selección expresa.

## 3. Paquete A — Decisiones seleccionadas por los autores (vigentes para la propuesta, no aprobación externa)

### 3.1 DEC-01 — Ámbitos configurables por cuenta externa

**Selección expresa de los autores (SA-DEC-01):** cada cuenta externa de V1 pertenece a un único cliente y recibe un ámbito de acceso explícitamente configurado. El ámbito puede contener toda la cartera autorizada de ese cliente o un subconjunto de sus seguimientos; no existe derecho implícito a consultar toda la cartera por pertenecer al cliente.

**Reglas de aplicación candidatas:**

- **A01-01:** cuentas sin asignación de ámbito no acceden a seguimientos ni publicaciones protegidas; no se infiere permiso general.
- **A01-02:** la concesión, modificación y revocación del ámbito requiere actor interno autorizado y registro de auditoría; las reglas de quién administra esos ámbitos deben ratificarse.
- **A01-03:** un ámbito nunca puede incluir seguimientos o recursos de otro cliente. Conocer radicado, ID o URL no amplía permisos.
- **A01-04:** las listas, paneles, indicadores, detalle, novedades, anexos e informes se filtran desde el backend por los ámbitos y permisos vigentes de la cuenta.
- **A01-05:** una publicación de un seguimiento no queda accesible si la cuenta no tiene ese seguimiento en su ámbito, incluso si la publicación está en estado `Publicada` y el cliente es el destinatario.
- **A01-06:** revocar un ámbito impide nuevas consultas y descargas, incluidos enlaces anteriores. No revoca copias ya descargadas fuera de la plataforma.
- **A01-07:** todas las operaciones protegidas requieren identidad vigente, rol/permiso, cliente, ámbito, relación con el recurso, operación solicitada y estados pertinentes; por defecto se deniega.
- **A01-08:** información de una organización jurídica sobre un proceso común no permite ver novedades privadas de otro cliente.

**Pendiente del responsable competente:** quién configura ámbitos (administrador, coordinador del cliente o ambos); política de altas/invitaciones; política de egreso contractual y si pueden existir permisos extraordinarios controlados. Ninguno se presume autorizado por esta selección.

**RF:** 005, 008–010, 114, 134, 138–150. **CU:** 01, 02, 17, 22–27. **Modelo/Reglas:** RG-A-01/02, RG-A4-01..08. **Estado:** SA autores; revisión producto/seguridad/privacidad pendiente.

### 3.2 DEC-02 — Cuentas vinculadas a un cliente

**Acuerdo anterior conservado:** en V1, cada cuenta externa está vinculada a un único cliente; un cliente puede tener múltiples cuentas. DEC-01 fija que esas cuentas pueden tener distintos subconjuntos de su cartera. No se autoriza acceso multicliente ni se asigna toda la cartera automáticamente a una cuenta nueva.

**RF:** 009–010, 138–150. **Estado:** principio AC; ámbitos SA-DEC-01.

### 3.3 DEC-03 — Suspensión: bloqueo ordinario temporal

**Selección expresa de autores (SA-DEC-03):** cuando el cliente queda `Suspendido`, las cuentas externas asociadas no pueden utilizar el portal ordinario ni descargar recursos protegidos; la plataforma deja de originar nuevas adquisiciones ordinarias atribuibles exclusivamente a sus seguimientos. El histórico interno se conserva y los estados de cada seguimiento no se modifican masivamente.

**Reglas:**

- **A03-01:** registrar actor, causa, instante y alcance de suspensión.
- **A03-02:** bloquear listados, panel, detalle, documentos, informes y URL de descargas ordinarias durante suspensión, aunque la cuenta tenga ámbito asignado.
- **A03-03:** no alterar automáticamente ME-01 ni pasar publicaciones a `Retirada` en ME-05 por el solo hecho de suspender al cliente.
- **A03-04:** revalidar la elegibilidad antes de ejecutar solicitudes programadas; una adquisición ya iniciada puede registrar su resultado técnico, sin crear nuevas novedades ordinarias para el suspendido.
- **A03-05:** otra organización jurídica/cliente activo que comparte radicado puede continuar su adquisición autorizada y su ciclo privado.
- **A03-06:** reactivación no reestablece cobertura pasada ni permisos revocados; se recalculan restricciones y se registra brecha de vigilancia.
- **A03-07:** si existe una publicación autorizada pero no efectivamente publicada, suspender al cliente impide completar la emisión externa; no se marca falsamente `Publicada`.

**Alcance explícito:** suspensión de cliente ≠ finalización de seguimiento (DEC-04). Las cuentas pueden permanecer habilitadas administrativamente pero quedan inoperativas en su portal durante la suspensión.

**RF:** 008, 010, 016, 019–020, 029–030, 054–055, 129–134, 138–150. **Estado:** SA autores; revisión contractual/privacidad/operación pendiente.

### 3.4 DEC-04 — Cierre de acceso externo al finalizar seguimiento

**Selección expresa de autores (SA-DEC-04, distinta de recomendación v0.3):** al pasar un seguimiento individual a `Finalizado`, se **cierra su consulta externa ordinaria** para todas las cuentas del cliente, aunque permanezcan activas y tengan el seguimiento dentro de su ámbito. La medida comprende ficha del seguimiento, novedades publicadas vinculadas a él, anexos y documentos habilitados por ese seguimiento, y acceso directo a recursos exclusivos de dicho seguimiento.

**Reglas de aplicación candidatas:**

- **A04-01:** el `Finalizado` permanece en ME-01 y bloquea nuevas adquisiciones ordinarias atribuibles a ese seguimiento.
- **A04-02:** se bloquea el acceso externo ordinario a la ficha, publicaciones, documentos y anexos cuya autorización dependa de ese seguimiento, incluso a través de enlaces previamente accesibles.
- **A04-03:** no borrar observaciones, tareas, decisiones, auditoría ni documentos internos; aplicar políticas de retención todavía por definir.
- **A04-04:** no cambiar automáticamente publicaciones `Publicada` a `Retirada` ni `Reemplazada`; siguen almacenadas y trazables internamente, pero la autorización externa se bloquea por el estado del seguimiento.
- **A04-05:** finalizar un seguimiento de A no afecta otro seguimiento de A, ni el seguimiento de B sobre el mismo radicado.
- **A04-06:** los listados y tableros externos no ofrecen acceso al seguimiento finalizado ni cuentan como recursos consultables sus publicaciones. No generar un enlace/ítem navegable hacia su histórico.
- **A04-07 (propuesta conservadora, sujeto a ratificación):** un informe consolidado ya publicado que incluya **cualquier** seguimiento finalizado deja de estar accesible como unidad; la continuidad de un informe para otros seguimientos exige una **nueva versión autorizada** que excluya información del seguimiento finalizado, no una modificación silenciosa del PDF aprobado.
- **A04-08:** no se revocan copias previamente descargadas fuera de la plataforma. La política de egreso/entrega posterior, si existe, será una decisión contractual aparte.
- **A04-09:** el cierre externo ocurre al quedar efectivamente confirmado `Finalizado` el seguimiento, con control en cada solicitud. No se supone que el estado `Cerrada` de una novedad equivale a `Finalizado` del seguimiento.

**Precisión crítica:** el usuario escogió *cerrar acceso externo*, no *mantener histórico visible para cliente activo*. Por tanto, queda descartada para la propuesta de V1 la opción PH-03 original de v0.3. El bloqueo no es una retirada de contenido aprobada ni un mecanismo de borrado.

**RF:** 019–020, 010, 105–114, 133–134, 138–150. **CU:** 18, 22–27. **ME:** 01, 05. **Estado:** SA autores; consentimiento organizacional/contractual, tratamiento de informes con múltiples seguimientos y retención pendientes.

### 3.5 Precedencia de restricciones propuestas

1. Cuenta deshabilitada o identidad no autenticada → denegar.
2. Cliente suspendido o no habilitado para operación → bloquear portal ordinario.
3. Recurso fuera del ámbito explícito de la cuenta externa → denegar.
4. Seguimiento vinculado al recurso está `Finalizado` → bloquear acceso externo ordinario.
5. Versión no publicada vigente o documento no habilitado → denegar.
6. Si todas las condiciones aplicables son verdaderas → permitir únicamente la operación autorizada; auditar según RF-V1-114.

No se incluye un permiso automático de excepción para el estado `Finalizado` en la primera versión.

### 3.6 Matriz de decisión externa de los autores

| Cliente | Cuenta | Seguimiento | Publicación | Ámbito cuenta | Disponibilidad externa esperada |
|---|---|---|---|---|---|
| Activo | Habilitada | Activo | Publicada vigente | Incluido | Permitida, si operación autorizada |
| Activo | Habilitada | Activo | Publicada vigente | **No incluido** | **Denegada** |
| Suspendido | Habilitada | Activo | Publicada vigente | Incluido | **Bloqueada por cliente** |
| Activo | Habilitada | **Finalizado** | Publicada vigente | Incluido | **Bloqueada por seguimiento** |
| Activo | Habilitada | Finalizado | Retirada/reemplazada | Incluido | Denegada también por vigencia |
| Activo | Habilitada | Suspendido | Publicada vigente | Incluido | **Pendiente política separada** de suspensión individual del seguimiento |
| Activo | Deshabilitada | Activo | Publicada vigente | Incluido | Denegada por cuenta |
| Activo | Habilitada | Activo | Autorizada no publicada | Incluido | Denegada por falta de publicación efectiva |

### 3.7 Reglas derivadas del paquete A (v0.4)

| ID | Regla | RF |
|---|---|---|
| RG-A4-01 | Cada cuenta externa pertenece a un solo cliente y recibe ámbito explícito, no acceso global implícito | 009–010, 138–150 |
| RG-A4-02 | Los permisos se evalúan en cada operación de backend, incluidas URL directas | 010, 134, 148–150 |
| RG-A4-03 | Suspender un cliente bloquea portal ordinario y nuevas adquisiciones propias, sin cambiar ME-01 masivamente | 008, 020, 030, 054, 138–150 |
| RG-A4-04 | `Finalizado` bloquea consulta externa del seguimiento, incluso si su publicación sigue `Publicada` | 019, 134, 142, 144–150 |
| RG-A4-05 | Retención histórica interna no confiere disponibilidad externa | 105–114, 134 |
| RG-A4-06 | Informes con alcance mixto requieren política indivisible: no revelar datos de seguimientos finalizados | 135–137, 149–150 |
| RG-A4-07 | Una cuenta nueva sin ámbito explícito no obtiene cartera completa | 009–010, 138–150 |

## 4. Paquete B — DEC-08 y DEC-09: revisión jurídica y segregación (propuestas nuevas, sin selección de autores)

**Distinción de estado:** DEC-08 preserva como principio previo que la interpretación jurídica depende de un profesional habilitado. DEC-09 dispone de un criterio de segregación previamente propuesto, pero **el usuario no lo ratificó en esta intervención**. Las formulaciones siguientes son propuestas concretas para selección de los autores y posterior validación organizacional.

### 4.1 DEC-08 — Matriz de clasificación y revisión obligatoria

**Texto candidato PR-DEC-08-v0.4:** la plataforma clasificará el contenido de una novedad y de sus posibles comunicaciones según su naturaleza y la evidencia disponible. La revisión operativa determina hechos verificables; toda interpretación, consecuencia o recomendación jurídica requiere validación por abogado habilitado antes de poder someterse a aprobación externa. Una propuesta LLM es un insumo no verificado que nunca se publica automáticamente.

| Clase | Información o ejemplo | Control mínimo antes de publicar | ¿Revisión jurídica? | Excepción / límite |
|---|---|---|---|---|
| **B1 — Metadatos objetivos** | Radicado, despacho, fecha e identificación de actuación apoyados por observación válida | Verificación operativa de identidad, procedencia, fecha, completitud y autorización G09 | No obligatoria por defecto **solo si responsable jurídico ratifica categoría B1** | Si el dato es ambiguo o afecta valoración, escalar a B6/B3 |
| **B2 — Descripción estrictamente factual** | «Se registró una actuación denominada ...» sin inferir efectos jurídicos | Verificación operativa del documento/actuación + revisión de redacción y autorización G09 | Requiere determinación de política por tipos de comunicación; **hasta ratificación, escalar a abogado** | No permitir verbos de conclusión jurídica disfrazados de hecho |
| **B3 — Interpretación jurídica** | Efecto legal de una providencia, alcance de una decisión | Abogado valida evidencia y conclusión + autorización G09 | **Obligatoria** | No puede aprobarse solo por analista o LLM |
| **B4 — Consecuencia/recomendación jurídica** | Consecuencias procesales o actuaciones recomendadas | Abogado habilitado + G09; recomendaciones solo dentro del alcance permitido | **Obligatoria** | No se introduce estrategia procesal autónoma; cálculo automático de términos fuera de V1 |
| **B5 — Datos o síntesis propuestos por LLM** | Campos extraídos/interpretados directamente por modelo multimodal | Validación humana de G06; en V1, por abogado habilitado según ME-04B, con original visible | **Abogado en validación documental G06**; si hay conclusión jurídica, además se aplica B3/B4 | La aceptación del formato del JSON no confirma exactitud; sin OCR independiente |
| **B6 — Información insuficiente o ambigua** | Observación parcial, identidad de actuación dudosa, documento ilegible | Registrar incertidumbre, revisión operativa, bloqueo de afirmación judicial confirmada | Si hace falta interpretación, escalar a abogado | Puede comunicarse una **limitación de cobertura**, revisada y autorizada, sin presentarla como novedad confirmada |

**Reglas atómicas candidatas:**

- **B08-01 — Clasificación explícita:** toda comunicación que declare hechos o efectos de una novedad debe tener categoría revisada y evidencia relacionada.
- **B08-02 — Frontera operativa:** el analista puede constatar hechos, calidad de fuente, duplicidad, fechas y suficiencia; no registra dictámenes jurídicos por ese rol.
- **B08-03 — Escalamiento por defecto:** si existe ambigüedad de categoría, posibilidad de efecto jurídico o síntesis inferencial, exigir revisión jurídica antes de aprobar la publicación.
- **B08-04 — Conclusión jurídica:** B3/B4 siempre exige decisión de abogado habilitado con evidencia y responsable trazables.
- **B08-05 — IA documental:** B5 exige revisión humana habilitada según G06 (abogado para V1); no se transforma en resultado validado por mera estructura correcta ni se publica automáticamente.
- **B08-06 — Independencia de publicación:** una revisión jurídica finalizada no equivale a autorización G09; coordinador sigue decidiendo sobre versión concreta.
- **B08-07 — Cobertura insuficiente:** ausencia de adquisición válida o evidencia incompleta no se convierte en «sin cambios» ni en hecho positivo confirmado.
- **B08-08 — Cambio de categoría:** al introducir interpretación sobre contenido B1/B2, reabrir la evaluación de obligatoriedad antes de publicar una nueva versión.
- **B08-09 — Excepciones controladas:** si la organización aprueba que B1 o una parte de B2 se comuniquen sin abogado, debe identificar tipos, condiciones, responsable y trazabilidad; nunca aplicar la excepción a B3/B4.
- **B08-10 — Destinatario:** revisión suficiente no amplía alcance de cliente/seguimiento; se aplican DEC-01/03/04 y G09.

**Roles:** analista (verifica hechos), abogado (valora jurídicamente y valida propuesta LLM según G06), preparador autorizado (compone publicación), coordinador independiente (aprueba versión), sistema (guarda y registra). Una persona con roles acumulados sigue sometida a los controles pertinentes.

**Impacto:** RF-V1-062, 063, 065–067, 069–070, 077, 081–090, 120, 122–127, 137, 153; CU-09,10,13,14,20,21,29; ME-03, ME-04A, ME-04B, ME-05.

**Cuestiones no cerradas por el modelo:** lista concreta de tipos de actuación de B1/B2; quién puede categorizar comunicaciones mixtas; política de datos personales; habilitación de proveedor para documentos reales.

### 4.2 DEC-09 — Control de doble persona en aprobación de publicación

**Texto candidato PR-DEC-09-v0.4:** una misma **persona natural** no podrá crear/preparar materialmente y aprobar una **misma versión** de publicación. Esta restricción aplica aunque disponga de múltiples roles, cuentas o permisos. El sistema registrará identidades de las personas que prepararon la versión y de quien la aprobó; denegará autoaprobación y exigirá un aprobador distinto, con rol y ámbito vigentes, antes de permitir su publicación.

**Reglas atómicas candidatas:**

- **B09-01 — Persona vs cuenta:** comparar identidad única de persona, no únicamente nombre de rol, login o cuenta. La asociación de múltiples cuentas a una persona requiere control de identidad.
- **B09-02 — Alcance del preparador:** se consideran preparadores el creador y quienes hayan modificado materialmente contenido comunicable, destinatario o anexos de la versión sometida a autorización. La autoría debe estar registrada.
- **B09-03 — Aprobador:** solo un coordinador o persona con facultad de aprobación explícitamente habilitada y distinta de todo preparador material puede autorizar la versión.
- **B09-04 — Prohibición por rol acumulado:** poseer roles Abogado+Coordinador o Analista+Coordinador no habilita autoaprobación de versión preparada por esa misma persona.
- **B09-05 — No sustitución de revisión jurídica:** aprobación editorial no subsana una revisión B3/B4 pendiente. Una misma persona podría actuar como abogado revisor y coordinador aprobador **si no fue preparador y su matriz de roles lo permite**, asunto sujeto a ratificación del dominio.
- **B09-06 — Versión inmutable:** aprobación identifica versión, contenido, anexos, cliente destinatario, fecha y persona aprobadora. Alteración exige nueva versión y nueva autorización.
- **B09-07 — Sin aprobador alterno:** la versión queda `Pendiente autorización` o se gestiona mediante rechazo formal; **no** se autopublica ni se crea aprobación automática por urgencia.
- **B09-08 — Bloqueo backend:** la guarda debe verificarse durante la acción de aprobación, no solo en interfaz. El rechazo genera registro auditado.
- **B09-09 — Informes:** la prohibición se aplica también a informes PDF finales de G09, con el artefacto generado antes de la aprobación.
- **B09-10 — Rectificaciones:** una nueva versión corregida requiere nuevos controles; la aprobación de una versión previa no cubre la correctiva.

**Diferencia de controles:** (a) revisión de hechos por analista; (b) revisión jurídica del abogado cuando aplique; (c) preparación de contenido; (d) aprobación de versión por coordinador independiente. Son responsabilidades distintas, aunque una persona pueda ejecutar más de una si no viola las restricciones ratificadas.

**Impacto:** RF-V1-005, 010, 114, 120–129, 132, 137, 153; CU-20,21,29; ME-05. No se exige un nuevo RF a menos que el catálogo actual no pueda alojar la guarda y sus criterios de aceptación.

### 4.3 Compatibilidad con DEC-13 y DEC-14

- Se genera y congela la representación final exacta (incluido PDF) antes de solicitar aprobación.
- La aprobación corresponde al contenido revisado y la identidad inmutable de versión y anexos.
- Un fallo de publicación permanece `Autorizada`, no `Publicada`, y permite recuperación controlada.
- El informe integral de un cliente puede aprobar información validada aunque sus novedades individuales no se hayan publicado por separado.
- **Nuevo efecto de DEC-04:** un informe que contiene un seguimiento finalizado queda sujeto a bloqueo de acceso externo como unidad, según A04-07, sin cambiar automáticamente el estado ME-05; no se debe publicar una versión «recortada» sin nueva autorización.

### 4.4 Decisiones listas para selección de los autores

| Decisión | Opción recomendada para V1 | Alternativa | Estado actual |
|---|---|---|---|
| **DEC-08** | B1 factual verificado sin abogado **solo si** se ratifica la excepción; B2 ambiguo o mixto a abogado; B3/B4 obligatorio; B5 abogado validando documento; B6 bloqueado como hecho confirmado | Exigir abogado para todas las categorías comunicables | **PR — pendiente selección de autores y validación jurídica** |
| **DEC-09** | Prohibición de que una persona que prepara una versión pueda aprobarla, sin excepción en V1 | Autoaprobación regulada (no recomendada) | **PR — pendiente selección de autores y validación organizacional** |

### 4.5 Reglas derivadas del paquete B v0.4

| Regla | Contenido | RF |
|---|---|---|
| RG-B4-01 | B3/B4 requieren revisión jurídica antes de publicación | 065–067, 122, 125 |
| RG-B4-02 | Propuesta LLM validada estructuralmente no es hecho confirmado | 077–090, 122 |
| RG-B4-03 | B1/B2 solo pueden comunicarse sin abogado cuando exista política jurídica ratificada | 062–066, 122–125 |
| RG-B4-04 | Preparador material y aprobador de una misma versión son personas distintas | 005, 010, 127 |
| RG-B4-05 | Aprobación de informe abarca artefacto exacto, no plantilla anterior | 125–129, 137 |
| RG-B4-06 | DEC-04 impide divulgar información externa de seguimientos finalizados incluso dentro de informes consolidados | 134, 135–137, 149–150 |

## 5. Paquete C — Rectificaciones, tareas y estados terminales

### 5.1 DEC-10 — Rectificación trazable RF-V1-153

**Política PR-DEC-10:** una rectificación es una **nueva decisión relacionada** con una novedad o decisión anterior; no reescribe la evidencia original, la revisión histórica, ni modifica silenciosamente el estado terminal de ME-03.

**Secuencia funcional propuesta:**

1. **Iniciar:** usuario habilitado registra motivo, referencia de novedad/decisión e indicios de error o nueva evidencia.
2. **Clasificar:** responsable operativo distingue error factual/documental y necesidad de revisión jurídica.
3. **Revisar:** se obtiene aprobación de la persona competente según la clase de contenido; una propuesta LLM continúa siendo auxiliar.
4. **Resolver:** se registra si la rectificación procede, no procede o requiere nueva evidencia, sin sobrescribir el resultado anterior.
5. **Evaluar impacto:** revisar tareas/obligaciones vigentes, valoraciones, documentos y publicaciones relacionadas.
6. **Comunicar, si aplica:** si cambia la información comunicable, iniciar retiro, sustitución o nueva publicación bajo G09 con autorización independiente.
7. **Auditar:** conservar secuencia, actor, motivo, evidencias, decisiones y vínculos anteriores/posteriores.

**No implica:** agregar automáticamente nuevos estados a ME-03, crear publicación automática, retirar publicaciones preventivamente sin autorización, ni reabrir silenciosamente estados terminales. Los subestados de la operación de rectificación, si se necesitan, se diseñarán al concretar el modelo de datos.

**Urgencia:** cuando se confirma contenido externo incorrecto que amerita actuación inmediata, el responsable competente podrá ordenar una retirada controlada G09; si falla, registrar incidencia y aplicar contención según política. El procedimiento de urgencia y sus responsables deben ratificarse.

**Requisitos:** RF-V1-064, 067–070, 091, 099–101, 132–134, 153; ME-03, ME-05 y ME-06.  
**Estado:** propuesta aún pendiente de validación jurídica/operativa.

### 5.2 DEC-11 — Tareas y obligaciones pendientes

**Principio acordado:** la tarea concreta y la obligación que representa pueden tener ciclos de vida diferentes. Una tarea cancelada no queda completada ni satisface por sí misma una obligación.

**Política candidata de cierre:**

- **Completada:** obligación satisfecha si se valida la evidencia exigida.
- **Pendiente, En curso, Bloqueada:** obligación pendiente si la tarea es obligatoria.
- **Cancelada sin reemplazo:** obligación no satisfecha; cierre ordinario bloqueado.
- **Sustituida:** la obligación queda pendiente de la tarea sustituta.
- **Excepción autorizada:** podrá permitir cierre únicamente si un responsable facultado registra causa y evidencia suficientes.
- **Fecha objetivo:** es administrativa y no debe presentarse automáticamente como plazo procesal calculado.

**Requisitos:** RF-V1-070, 091, 094, 098–101; ME-03 y ME-06.  
**Estado:** principio AC; quién autoriza excepciones y condiciones específicas PR.

### 5.3 Reglas derivadas del paquete C

| ID | Regla candidata | Requisitos |
|---|---|---|
| RG-C-01 | Una rectificación no elimina ni sobrescribe decisiones terminales anteriores | 064, 067–068, 153 |
| RG-C-02 | Las decisiones correctivas quedan relacionadas con las actuaciones, evidencias y publicaciones afectadas | 067, 105–114, 132–134, 153 |
| RG-C-03 | Cambiar información ya publicada exige nuevo flujo G09 | 125–134, 153 |
| RG-C-04 | Cancelar una tarea no satisface automáticamente su obligación | 070, 099, 101 |
| RG-C-05 | Las excepciones de cierre requieren responsabilidad y justificación verificables | 070, 101 |

## 6. Protocolo de ratificación: decisiones concretas a someter a aprobación

| Acta | Pregunta de decisión para el responsable | Opción predeterminada recomendada | Alternativa relevante | Responsables sugeridos | Estado |
|---|---|---|---|---|---|
| ACT-DEC-01 | ¿Se ratifica ámbito configurable por cuenta y denegación contextual por recurso? | **Autores seleccionan ámbitos configurables** (cuenta dentro de cliente único) | Acceso a toda cartera del cliente por defecto | Producto + seguridad | **Selección de autores registrada; validación externa pendiente** |
| ACT-DEC-03 | ¿Se ratifica bloqueo de portal durante suspensión del cliente? | **Autores seleccionan bloqueo ordinario** | Histórico limitado durante suspensión | Producto + privacidad | **Selección de autores registrada; validación externa pendiente** |
| ACT-DEC-04 | ¿Se ratifica cierre del acceso externo cuando finaliza el seguimiento? | **Autores seleccionan cierre del acceso** | Mantener consulta de publicaciones históricas vigentes | Producto + privacidad + jurídico | **Selección de autores registrada; validación externa pendiente** |
| ACT-DEC-08 | ¿Se adoptan las categorías B1–B6 y el protocolo escalonado descrito en 4.1? | B3/B4 jurídicos obligatorios; B2 ambiguo se escala; B5 abogado valida | Abogado para todos los comunicados | Autores + abogado responsable | **Pendiente selección de autores y validación jurídica** |
| ACT-DEC-09 | ¿Se prohíbe que una persona materialmente preparadora apruebe su propia versión? | Dos personas sin excepción en V1 | Autoaprobación restringida | Autores + coordinación + seguridad | **Pendiente selección de autores y validación organizacional** |
| ACT-DEC-10 | ¿Se ratifica RF-V1-153 y la rectificación inmutable vinculada? | Sí; efectos externos por G09 | Flujo correctivo alternativo | Operación + jurídico | Sin ratificar |
| ACT-DEC-11 | ¿Quién puede conceder excepción de cierre y con qué evidencia? | Coordinador competente con justificación, y abogado si afecta criterio jurídico | Solo abogado, o sin excepciones | Operación + jurídico | Sin ratificar |
| ACT-DEC-13 | ¿Cómo responder ante retirada publicada que falla? | Incidencia + contención autorizada + evidencia de recuperación | Protocolo de incidentes diferente | Coordinación + seguridad | Sin ratificar |
| ACT-DEC-17 | ¿Se formalizan CU-29, CU-30 y ME-07 en la matriz maestra? | Sí, sin renumerar | Ajustes de nombre/actor/guardas | Equipo + tutor | Sin ratificar |
| ACT-DEC-18 | ¿Se aceptan 151→134, 152→114 y RF-153 nuevo sin reutilizar 078? | Sí, con matriz de equivalencias | Revisión de absorción | Equipo + tutor | Sin ratificar |

**Validación de decisiones previas:** DEC-02 (un cliente por cuenta externa), DEC-06 (separación de referencias), DEC-12 (multimodal sin OCR) y DEC-14 (informe aprobado como unidad) se conservan como acuerdos del proceso de requisitos, pero la política de tratamiento/uso en operación real y sus evidencias deben ser verificadas.

### 6.1 Acta de ratificación individual — plantilla

```yaml
id_acta: ACT-DEC-XX
id_decision: DEC-XX
version_sometida: RF-DEC-001-v0.4
resultado: pendiente # aprobar | aprobar_con_cambios | rechazar | diferir
texto_aprobado: null
responsable: null
rol_competente: null
fecha_decision: null
fundamento: null
evidencia: null
impacto_rf: []
impacto_cu_me: []
impacto_casos_prueba: []
version_catalogo_destino: RF-CAT-001-v0.9-propuesta
```

**Regla de registro:** nunca completar nombres, firmas, fechas o evidencias por inferencia; una discusión conceptual de los autores no equivale automáticamente a autorización de condiciones legales o contractuales externas.

## 7. Casos de aceptación de decisiones (nuevos o refinados, diseñados)

| Caso | Precondiciones / datos | Procedimiento | Resultado esperado | RF relacionados |
|---|---|---|---|---|
| AT-DEC2-01 | Cuenta activa de cliente A, documento restringido de B y URL conocida | Consultar recurso de B | Denegado sin revelar contenido, registrando el evento aplicable | 010, 114, 148 |
| AT-DEC2-02 | Administrador técnico sin rol jurídico | Abrir valoración privada | Denegado; no se deduce permiso del rol técnico | 005, 010, 105 |
| AT-DEC2-03 | Cliente A suspendido, B activo, proceso compartido | Ejecutar programación para B y para A | No iniciar adquisición por A; B continúa si está habilitado | 008, 020, 029–030 |
| AT-DEC2-04 | Seguimiento finalizado y publicación externa vigente | Consultar como cliente activo autorizado | Denegado según selección de autores DEC-04; exige ratificación externa para ser política operativa | 134, 142, 144 |
| AT-DEC2-05 | Cuenta desactivada y enlace anterior de descarga | Descargar documento | Denegado en backend, incluso por URL directa | 010, 148, 150 |
| AT-DEC2-06 | Novedad factual B1 con evidencia suficiente | Preparar publicación para un cliente | Revisión operativa y aprobación G09; abogado solo si política B1 es ratificada jurídicamente | 062, 122, 125–127 |
| AT-DEC2-07 | Novedad B3 sin validación jurídica | Solicitar aprobación de publicación con interpretación | Bloqueado por falta de revisión obligatoria | 065–066, 122, 125 |
| AT-DEC2-08 | Propuesta LLM no revisada | Intentar incorporarla como conclusión publicada | Denegado; requiere validación humana y jurídica cuando aplique | 081–090, 122 |
| AT-DEC2-09 | Preparador y coordinador son la misma persona con ambos roles | Intentar aprobar su propia versión | Denegación esperada bajo propuesta DEC-09; pendiente selección de autores y ratificación organizacional | 005, 010, 127 |
| AT-DEC2-10 | PDF final con huella de versión aprobada; anexo alterado | Intentar publicación | Requiere nueva versión y aprobación | 125–129, 137 |
| AT-DEC2-11 | Publicación autorizada con fallo de disponibilidad | Ejecutar publicación fallida | Permanece `Autorizada`, se registra incidente/reintento | 129–130 |
| AT-DEC2-12 | Novedad `Cerrada` con decisión incorrecta | Registrar rectificación autorizada | Nueva decisión relacionada; original y estado terminal no se sobrescriben | 064, 067–068, 153 |
| AT-DEC2-13 | Rectificación afecta publicación vigente | Intentar alterar texto externo directamente | Se bloquea edición directa; se exige flujo G09 | 132–134, 153 |
| AT-DEC2-14 | Tarea obligatoria cancelada sin reemplazo | Intentar cerrar novedad | Bloqueado salvo excepción autorizada, motivada y trazable | 070, 099, 101 |
| AT-DEC2-15 | Tarea sustituida por otra no completada | Intentar cerrar novedad | Obligación sigue pendiente | 070, 101 |
| AT-DEC2-16 | Seguimiento reactivado tras periodo sin cobertura | Consultar portal | No declara continuidad ni «sin cambios» sin evidencia suficiente | 020, 023, 143, 146 |

Todas las pruebas anteriores están **diseñadas** y sus resultados son **esperados**; ninguna está ejecutada ni verificada empíricamente. En pruebas condicionadas, la regla indicada como «si se ratifica» debe permanecer explícita.

## 8. Dependencias externas y decisiones que no puede cerrar esta ratificación

| Código | Pendiente | Evidencia mínima | Bloqueo concreto |
|---|---|---|---|
| FCT-01 | CPNU/fuente judicial autorizada | Condiciones de uso, mecanismo permitido, prueba documentada | No afirmar adquisición real automatizada |
| FCT-02 | Identidad/comparabilidad de actuaciones | Corpus de observaciones fuente/GT y reglas determinísticas evaluadas | No aprobar comparadores finales por fuente |
| FCT-03 | Proveedor LLM multimodal | Compatibilidad PDF/imagen, respuesta, pruebas con material permitido | No declarar G06 implementable en producción |
| FCT-04 | Tratamiento documental externo | Evaluación de privacidad, finalidad y condiciones del proveedor | No transmitir documentos reales sin habilitación |
| DOM-01 | Categorías B1–B6 de DEC-08 | Selección expresa de autores y acta de revisión con profesional jurídico | No aprobar matriz como política definitiva |
| DOM-02 | Suspensión/cierre del acceso tras finalización | Autores seleccionaron opciones; faltan actas de producto, jurídico y privacidad | No declarar política organizacional ratificada |
| DOM-03 | Rectificación | Protocolo ratificado por operación/jurídico | No congelar tratamiento final ME-03/ME-05 |
| GOV-01 | Auditoría y retención | Política de conservación, minimización y acceso | No fijar plazos en código o documentación |

La referencia académica principal continúa siendo CPNU; la disponibilidad de sus mecanismos automatizables todavía no se ha demostrado. El procesamiento de contenido documental de V1 es exclusivamente multimodal; no se reinstala OCR ni extracción nativa independiente.

## 9. Impacto en catálogo, casos de uso, reglas y máquinas

| Decisión | RF-V1 afectados | Casos de uso | Modelos/reglas | Acción sobre RF-CAT-001 v0.9 |
|---|---|---|---|---|
| 01–04 | 005, 008–010, 016, 019–020, 030, 114, 134, 138–150 | CU-01, 02, 17, 18, 22–27 | ME-01, RG-A4 | Registrar selección de autores; integrar como política obligatoria solo con validación competente |
| 08 | 062, 065–070, 081–090, 122, 125 | CU-09, 10, 13, 14, 20 | ME-03/ME-04B, RG-B | Vincular matriz de categorías y sus excepciones |
| 09 | 005, 010, 120–129, 137 | CU-20/21/29 | ME-05, RG-B | Introducir guarda de distinta identidad en RF-127 si se aprueba |
| 10 | 064, 067–070, 132–134, 153 | CU-09, 10, 21 | ME-03/05, RG-C | Precisar flujo correctivo sin sobrescritura |
| 11 | 070, 091–101 | CU-09, 15 | ME-03/06, RG-C | Ajustar guardas de cierre y excepciones |
| 13–14 | 122–137, 149–150 | CU-20, 21, 27, 29 | ME-05, RG-B | Preservar versión exacta, informes integrales |
| 17–18 | 025–027, 114, 134–137, 151–153 | CU-29/30 | ME-07 | Mantener numeración y equivalencias |

**Advertencia:** esta matriz es un plan de cambios, **no evidencia de que RF-CAT-001 v0.8 ya se haya actualizado**. El catálogo v0.8 permanece fuente normativa de trabajo hasta formalizar los cambios aprobados.

## 10. Estado de los 57 requisitos reconstruidos

Se mantienen **57 textos reconstruidos**. Una ratificación de política no prueba que la redacción reconstruida sea igual a la fuente histórica original. Cada ficha exige registrar una de dos evidencias:

1. **Cotejo histórico:** origen original localizado, comparación de texto y conclusión de equivalencia o cambio.
2. **Ratificación sustitutiva:** enunciado actual aprobado explícitamente como redacción vigente nueva, conservando la condición de reconstrucción histórica.

| Grupo | RF pendientes | Cantidad |
|---|---|---:|
| G01 | 002–007, 009 | 7 |
| G02 | 011, 013–015, 017–019, 021–022, 024 | 10 |
| G03 | 025, 027–028, 031, 033–035, 037–039 | 10 |
| G04 | 040–041, 043–045, 048–049, 051–053 | 10 |
| G05 | 056–061, 063, 065, 067, 069 | 10 |
| G06 | 071–076, 085, 087, 089–090 | 10 |
| **Total** | | **57** |

La organización de estos 57 RF por paquete de ratificación debe preservarse en RF-CAT-001, sin promoverlos a «cotejados» por su mera revisión semántica.

## 11. Puertas de salida y plan de cierre

| Puerta | Condición | Estado actual |
|---|---|---|
| G-DEC-01 | Las políticas A/B/C están ratificadas por responsables competentes y con acta | Parcial: selección de autores A; todo el aval externo pendiente |
| G-DEC-02 | Las categorías jurídicas B1–B6 y sus excepciones han sido revisadas jurídicamente | Pendiente; solo propuesta DEC-08 documentada |
| G-DEC-03 | Selecciones de autores DEC-01/03/04 registradas y segregación DEC-09 aprobada externamente | **Parcial:** autores A registrados; B y validación externa pendientes |
| G-DEC-04 | RF-153 y su relación con ME-03/ME-05 han sido ratificados | Pendiente |
| G-DEC-05 | Los 57 RF reconstruidos han sido cotejados o ratificados textualmente | Pendiente |
| G-DEC-06 | Se actualiza RF-CAT-001 v0.9 con estado SA/PR y decisiones ratificadas por separado | Pendiente |
| G-DEC-07 | Se producen evidencias de fuentes, comparador y LLM y se mantienen restricciones mientras tanto | Pendiente |

**Secuencia próxima recomendada:** (1) seleccionar opciones propuestas DEC-08/09; (2) presentar DEC-01/03/04 y B a responsables; (3) revisar el catálogo diferenciando SA, PR y ratificación; (4) desarrollar RNF-001 y protocolos POC en paralelo; (5) construir ERS-001 y arquitectura cuando se cuente con una línea base suficientemente estable para cada incremento.

## 12. Checkpoint histórico de la versión 0.2 (conservado)

- **Catálogo fuente:** `RF-CAT-001_catalogo_maestro_LegalTech_v0.8_cierre_trazabilidad.md` (150 RF activos, 93 enunciados localizados, 57 reconstruidos).
- **Decisiones anteriores:** `RF-DEC-001_decisiones_funcionales_LegalTech_v0.1.md` (18 decisiones, 14 reglas transversales y 22 casos de aceptación de decisiones propuestos).
- **Este artefacto:** `RF-DEC-001_decisiones_funcionales_LegalTech_v0.2.md`, paquete de ratificación funcional, **sin aprobaciones ficticias**.
- **Principios conservados:** aislamiento por cliente/seguimiento; detección determinística; CPNU como referencia académica, integración no verificada; LLM multimodal sin OCR o extracción nativa independiente; revisión humana; PDF/versión exacta aprobada antes de publicación; auditoría externa central en RF-114.
- **No terminado:** validación externa, cotejo de 57 RF, ratificación de políticas, actualización RF-CAT v0.9, RNF, ERS, POC, arquitectura y desarrollo.
- **Nota histórica v0.2:** fue escrita antes de la selección de los autores de DEC-01/03/04. La instrucción actual es decidir DEC-08/09, obtener ratificación externa y actualizar RF-CAT v0.9 con control de versiones.

---

## 13. Actas dirigidas v0.4 — Selección de autores frente a ratificación organizacional

### 13.1 Registro de selección expresa de los autores

| Acta | Autoría de la selección | Alternativa escogida | Fecha de registro de esta versión | Autoridad organizacional |
|---|---|---|---|---|
| ACT-DEC-01 | Autores del proyecto, decisión expresada en la conversación | Ámbitos configurables por cuenta externa | 2026-11-09 | **Pendiente** |
| ACT-DEC-03 | Autores del proyecto, decisión expresada en la conversación | Bloquear acceso ordinario durante suspensión | 2026-11-09 | **Pendiente** |
| ACT-DEC-04 | Autores del proyecto, decisión expresada en la conversación | Cerrar acceso externo al finalizar seguimiento | 2026-11-09 | **Pendiente** |

**Precisiones de evidencia:** no se consignan nombres propios de firmantes, aceptación del tutor, organización jurídica, delegado de protección de datos ni contrato. La fecha anterior identifica el registro de esta propuesta, **no** una fecha ficticia de aprobación institucional.

### 13.2 Actas de decisión del paquete B (preparadas para adopción de autores)

**ACT-DEC-08 — Matriz de intervención jurídica**

- **Propuesta:** adoptar B1–B6 y reglas B08-01..10.
- **Opción 1 (recomendada):** B1 metadatos objetivos con revisión operativa y eventual excepción jurídicamente ratificada; B2 escalado ante ambigüedad; B3/B4 siempre abogado; B5 siempre revisión humana G06 por abogado en V1; B6 sin afirmación no acreditada.
- **Opción 2:** exigir abogado para toda comunicación, incluida la puramente factual.
- **Selección expresa de autores:** `PENDIENTE`.
- **Ratificador competente:** abogado responsable de la política jurídica; después, coordinación de publicaciones.
- **Criterio de salida:** decisión firmada/documentada y actualización de guardas en RF-V1-062/065/066/122/125, CU-09/10/14/20 y ME-03/ME-04B.

**ACT-DEC-09 — Segregación de funciones**

- **Propuesta:** prohibición de autoaprobación por la misma persona natural que creó o editó materialmente el contenido/versiones/anexos sometidos, sin excepción en V1.
- **Alternativa:** autoaprobación excepcional regulada y auditada (no recomendada).
- **Selección expresa de autores:** `PENDIENTE`.
- **Ratificadores competentes:** coordinación responsable de publicación y responsable de seguridad.
- **Criterio de salida:** política aprobada por interesados competentes y guarda de identidad vinculada a RF-V1-127, ME-05 y CU-20/21/29.

### 13.3 Plantilla de ratificación institucional (no rellenada)

```yaml
acta_id: ACT-DEC-XX
version_politica: RF-DEC-001-v0.4
seleccion_autores: null  # no completar si no se ha realizado
resultado_aprobacion_organizacional: pendiente
responsable_competente: null
cargo_rol: null
fecha_aprobacion: null
fundamento: null
evidencia_verificable: null
observaciones: null
requisitos_afectados: []
```

### 13.4 Escenarios de aceptación diferenciales para DEC-01/03/04

| Caso | Precondición | Acción | Resultado esperado de la propuesta |
|---|---|---|---|
| AT-A4-01 | Cliente A, cuenta U con ámbito solo S1, otro seguimiento S2 del mismo cliente | Consultar S2 por ID | Denegado, aunque A sea propietario de S2 |
| AT-A4-02 | Cuenta U autorizada para S1; publicación de S1 vigente | Consultar detalle y anexo de S1 | Permitido solo si todas las demás condiciones vigentes se cumplen |
| AT-A4-03 | Cuenta U sin ámbito asignado | Consultar tablero, procesos e informe | Sin datos de seguimientos; denegación de operaciones protegidas |
| AT-A4-04 | Cliente suspendido, cuenta U con ámbito y publicación vigente | Descargar por enlace anterior | Denegado; publicación interna no se cambia a Retirada |
| AT-A4-05 | Cliente A suspendido y B activo, mismo radicado | Adquirir para B | Permitido si B y fuente están habilitados; no produce novedad ordinaria para A |
| AT-A4-06 | Seguimiento S1 pasa a Finalizado con publicación `Publicada` | Abrir publicación de S1 como cuenta autorizada de A | Denegado por estado de S1; la versión puede seguir Publicada internamente |
| AT-A4-07 | Cliente A tiene S1 Finalizado y S2 Activo | Consultar S2 | Permitido; finalizar S1 no bloquea S2 |
| AT-A4-08 | Informe PDF publicado contiene S1 Finalizado y S2 Activo | Descargar informe | **Bloqueo conservador** del PDF completo hasta aprobar una nueva versión sin S1 (propuesta derivada pendiente de ratificación) |
| AT-A4-09 | Se descargó PDF de S1 antes de finalizar | Intentar revocar copia local | No se declara revocable fuera de plataforma; solo se deniegan descargas nuevas |
| AT-A4-10 | Seguimiento S1 finaliza, cuenta U sigue activa | Consultar panel externo | S1 no ofrece navegación ni datos detallados protegidos; no se presenta su publicación como disponible |

### 13.5 Escenarios de aceptación para DEC-08/09 (no ejecutados)

| Caso | Datos y precondición | Procedimiento | Resultado esperado de política propuesta | Trazabilidad |
|---|---|---|---|---|
| AT-B4-01 | B1 con metadatos cotejables, política jurídica que admite excepción | Preparar y solicitar aprobación G09 | Puede continuar sin valoración jurídica, pero no sin revisión operativa ni aprobación de versión | RF 062,122,125 |
| AT-B4-02 | B2 contiene «implica vencimiento» sin evidencia jurídica | Clasificar como factual y publicar | Rechazado/escalado a B3/B4 | RF 065,066,122,125 |
| AT-B4-03 | B3 con interpretación y sin abogado | Autorizar publicación | Bloqueado por revisión jurídica obligatoria | RF 066,125,127 |
| AT-B4-04 | B4 con acción procesal sugerida por LLM | Intentar publicar sin abogado | Rechazado; modelo no constituye criterio jurídico validado | RF 077–090,122 |
| AT-B4-05 | B5 propuesta de campos LLM y estructura correcta, aún sin validación humana | Incorporar a resultado publicable | Bloqueado; exige G06/ME-04B | RF 084,088–090,122 |
| AT-B4-06 | B6 con adquisición incompleta | Publicar «sin actuaciones» | Bloqueado; no transformar falta de evidencia en certeza | RF 032,042,143,146 |
| AT-B4-07 | Ana creó/editó versión V1 y tiene rol Coordinador | Intentar aprobar V1 | Denegado por identidad, aunque acumule roles | RF 005,010,127 |
| AT-B4-08 | Ana creadora; Luis coordinador autorizado; V1 con revisiones completas | Luis aprueba V1 | Permitido si ámbitos, estados y guardas cumplen | RF 125–129 |
| AT-B4-09 | Ana usa dos cuentas distintas ligadas a misma persona | Preparar por cuenta 1, aprobar por cuenta 2 | Denegado por persona, no solo ID de cuenta | RF 005,010,127 |
| AT-B4-10 | Versión aprobada; preparador modifica anexos | Intentar publicar versión antigua como modificada | Denegado; nueva versión y nueva aprobación | RF 126–129,137 |
| AT-B4-11 | Solo una persona con roles de preparar/aprobar disponible | Intentar autoaprobación de urgencia | No aprobación automática; requiere distinto aprobador o decisión institucional nueva | RF 127 |
| AT-B4-12 | PDF final de informe revisado por abogado y preparado por coordinador | El mismo coordinador intenta aprobar | Denegado bajo propuesta DEC-09 | RF 127,137 |

**Advertencia:** todos los AT-A4 y AT-B4 son **diseños de prueba**, no pruebas ejecutadas ni decisiones organizacionalmente ratificadas.

### 13.6 Matriz de actualización posterior de RF-CAT-001 v0.9

| Política/decisión | RF | Cambios propuestos en el futuro catálogo | Aplicación inmediata |
|---|---|---|---|
| DEC-01 SA | 009,010,114,138–150 | Añadir ámbito configurable por cuenta y filtrado de indicadores/documentos/informes | Registrar SA y trazabilidad; **no declarar aprobación externa** |
| DEC-03 SA | 008,019–020,029–030,054,134,138–150 | Bloqueo de acceso por suspensión y revalidación de adquisiciones compartidas | Registrar SA y pruebas; aprobación externa pendiente |
| DEC-04 SA | 019,105–114,134,138–150 | Bloqueo de consulta externa al `Finalizado`, con reglas de informes mixtos | Registrar SA; política de informe mixto requiere ratificación |
| DEC-08 PR | 062,065–066,077–090,122,125 | Matriz B1–B6, guardas jurídicas y validación humana | Esperar selección de autores y revisión jurídica |
| DEC-09 PR | 005,010,120–129,137 | No autoaprobación por misma persona, identidad de preparadores | Esperar selección de autores y gobierno de aprobación |

## 14. Checkpoint CP-DEC-v0.4 — Continuidad

- **Fecha de corte:** 2026-11-09.
- **Fuente normativa funcional:** RF-CAT-001 v0.8; 150 RF activos, RF-V1-078 excluido, RF-V1-151→134 y RF-V1-152→114, RF-V1-153 candidato. RF-CAT aún no se ha modificado en esta etapa.
- **Registros de decisión:** RF-DEC-001 v0.4, con DEC-01 (ámbitos configurables), DEC-03 (bloqueo portal por suspensión), DEC-04 (bloqueo externo al finalizar seguimiento) **seleccionadas expresamente por los autores**; falta ratificación organizacional.
- **DEC-04 cambia la recomendación v0.3:** ya no hay lectura ordinaria externa de publicaciones de seguimientos finalizados. No confundir bloqueo de visibilidad con retirada ME-05 o eliminación del histórico.
- **Paquete B propuesto:** DEC-08 categorías B1–B6 y revisión jurídica obligatoria para B3/B4; B5 requiere validación humana G06 por abogado en V1; DEC-09 separación entre preparadores materiales y aprobador como personas distintas. Ambas pendientes de elección expresa de autores y revisión competente.
- **Pendientes priorizados:** (i) política sobre informes que mezclan seguimientos finalizados y activos; (ii) permiso de histórico para seguimiento `Suspendido` individual; (iii) retención y egreso contractual; (iv) ratificación de paquete B; (v) rectificaciones y tareas obligatorias paquete C; (vi) 57 RF reconstruidos sin cotejo literal.
- **Dependencias externas sin avance verificable:** CPNU/otras fuentes autorizadas, corpus de identidad de actuaciones, LLM multimodal habilitado, tratamiento de datos reales.
- **Ruta siguiente:** seleccionar opciones DEC-08/09; documentar ratificación jurídica/organizacional; desarrollar paquete C DEC-10/11 y contingencia DEC-13; actualizar RF-CAT-001 v0.9 con control de cambios, sin falsificar aprobaciones; en paralelo RNF-001 y POC técnicas.
