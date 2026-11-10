---
documento: PROTO-001
proyecto: Plataforma LegalTech para vigilancia de carteras de procesos judiciales
version: "0.1-candidata"
fecha: "2026-11-09"
estatus: "Especificación de prototipo; sin implementación ni aprobación formal"
baseline_funcional: "RF-CAT-001 v0.8 (candidata, 150 RF activos)"
registro_decisiones: "RF-DEC-001 v0.4 (DEC-01/03/04 seleccionadas por autores; DEC-08/09 propuestas)"
tipo: "Prototipo funcional demostrativo con datos sintéticos y operaciones emuladas"
---

# PROTO-001 — Especificación del prototipo demostrativo de la plataforma LegalTech

## 1. Propósito y dictamen

**Dictamen de preparación:** APTO PARA PROTOTIPADO, no para despliegue productivo. Este artefacto delimita una muestra del ciclo de vigilancia judicial para tutor, docentes y autores del proyecto. Pretende comprobar comprensión del dominio y navegabilidad del flujo, **no validar la integración real con fuentes judiciales, seguridad productiva ni calidad jurídica**.

**Pregunta de demostración:** ¿Cómo una organización jurídica registra un seguimiento, compara dos observaciones judiciales, detecta una novedad, la revisa, autoriza una comunicación y permite que su cliente la consulte sin exponer información ajena?

**Fuentes:** RF-CAT-001 v0.8; RF-DEC-001 v0.4; AS-IS y TO-BE del proyecto; tesis I–III. Las 57 formulaciones catalogadas como reconstruidas en RF-CAT se usan solo como base candidata; la muestra no las ratifica automáticamente.

**Límite estricto:** El prototipo utilizará información **100 % sintética**. No efectuará consultas a CPNU, SAMAI ni otras fuentes reales; tampoco enviará documentos a un LLM real. Se indicará siempre que las adquisiciones, identidades y resultados son de demostración.

## 2. Objetivo demostrativo y alcance

### 2.1 Resultado de extremo a extremo

1. Entrar al entorno en el rol demostrativo de analista.
2. Consultar o registrar un cliente y proceso ficticios; crear/activar un seguimiento.
3. Visualizar observación inicial comparable (línea base), con cinco actuaciones ficticias.
4. Ejecutar un **paso emulado de adquisición** que carga una segunda observación con seis actuaciones.
5. Ejecutar la **comparación determinística local** para identificar una actuación adicional; no usar IA para comparar.
6. Generar una única novedad vinculada a un seguimiento elegible.
7. Revisar evidencia operativa y escalar para valoración jurídica.
8. Cambiar al actor demostrativo abogado, registrar una valoración redactada para la muestra.
9. Cambiar al preparador y luego a una **persona distinta** con rol coordinador: preparar, autorizar y publicar una versión de comunicación.
10. Entrar como cuenta externa del cliente A y verificar la publicación autorizada.
11. Entrar como cliente B y comprobar que no puede acceder a la publicación de A, aunque conozca el radicado.
12. Finalizar el seguimiento A y verificar que se bloquea su acceso externo ordinario sin borrar el histórico interno (**DEC-04 seleccionada por autores**).

### 2.2 Dentro del prototipo

- Navegación responsive; identidad/rol de demostración, con advertencia visible de que **no** equivale a autenticación productiva.
- Cartera, seguimiento, línea base, dos observaciones y cambios.
- Comparador determinístico ejecutable sobre fixtures reproducibles; comportamiento idempotente en repetición.
- Revisión operativa y jurídica; decisiones y estados con restricciones básicas.
- Preparación, aprobación por un actor distinto y emisión **local** de una publicación.
- Consulta externa sometida a restricciones de cliente, ámbito de cuenta, estado del seguimiento y vigencia de la publicación dentro del **modelo simulado**.
- Registro local de acciones de demostración y botón de reinicio para repetir la presentación.
- Estados vacíos y advertencias de cobertura cuando la adquisición emulada falla.

### 2.3 Fuera del prototipo (sin eliminar de V1)

Integración judicial real; scraping o uso de credenciales para fuentes; procesamiento multimodal real; extracción/OCR; cálculos de términos procesales; asesoramiento jurídico autónomo; correos/SMS/WhatsApp; informes PDF consolidados; administración completa de cuentas; controles de seguridad productiva; despliegue productivo; múltiples proveedores; indicadores avanzados y el resto de RF no incluidos en el itinerario.

## 3. Actores de la muestra

| Actor demostrativo | Operaciones mostradas | Límites |
|---|---|---|
| Analista | Ver cartera/observaciones, ejecutar paso emulado, revisar y escalar novedad | No registra conclusiones jurídicas ni aprueba publicaciones |
| Abogado | Consultar evidencia, registrar y validar valoración jurídica de ejemplo | No publica automáticamente |
| Preparador interno | Generar borrador con contenido validado | No aprueba la misma versión preparada |
| Coordinador | Aprobar/rechazar y emitir publicación en la muestra | Persona demostrativa distinta del preparador |
| Cliente externo A | Ver seguimientos autorizados, novedades publicadas y estado | No puede leer material interno o recursos de B |
| Cliente externo B | Ver únicamente su propio ámbito; intentar abrir recurso de A para probar restricción | No obtiene información privada de A |

Para mantener ocho vistas, los actores internos comparten el mismo entorno y cambian su ámbito mediante un **selector explícitamente rotulado como «simulación de usuario»**. El prototipo no implementa autenticación verificable, protección real de endpoints ni aislamiento a nivel servidor; estas capacidades se evaluarán en V1.

**DEC-08 y DEC-09:** la exigencia de abogado para la interpretación jurídica y la separación entre preparador/aprobador se aplican como **salvaguardas del escenario**, pero siguen pendientes de selección expresa y ratificación organizacional en RF-DEC-001.

## 4. Vistas de interfaz (máximo 8)

| Vista | Nombre | Acciones principales | Estado mínimo |
|---|---|---|---|
| V01 | Acceso de demostración | Seleccionar actor de prueba y entrar, indicar modo ficticio | Actor seleccionado |
| V02 | Panel interno | Ver cartera, novedad y tareas del escenario; continuar flujo | Resumen y acceso a registros |
| V03 | Cartera judicial | Listar/registrar proceso, vincular cliente, activar seguimiento | Cliente, proceso, seguimiento |
| V04 | Detalle y vigilancia | Línea base, observaciones, cobertura, ejecutar adquisición emulada y comparar | Observaciones, cambio, ejecución |
| V05 | Novedades | Revisar la novedad, clasificar, ver evidencia y escalar | Estado ME-03, responsable |
| V06 | Revisión jurídica | Ver evidencia ficticia y añadir valoración profesional simulada | Valoración, revisión |
| V07 | Publicaciones | Crear borrador, solicitar autorización, aprobar, publicar | Estado ME-05, versión, destinatario |
| V08 | Portal del cliente | Mis seguimientos, novedad publicada, controles de acceso, finalización | Cliente, ámbito de cuenta, recursos publicados |

El diseño final de las vistas se decidirá posteriormente; esta tabla es el **contrato de interacción**, no un mockup aprobado.

## 5. Selección verificable de RF

### 5.1 Requisitos cuya conducta se representará en el recorrido

| Grupo | RF seleccionados | Comportamiento de demostración | Nivel de implementación |
|---|---|---|---|
| G01 | RF-V1-009, RF-V1-010 | Cuenta externa con ámbito configurado y filtro de acceso por recurso | **Emulación** de autorización, no seguridad productiva |
| G02 | RF-V1-011, 015, 016, 021, 023 | Registrar proceso/seguimiento, establecer línea base y finalizar | Funcional con datos sintéticos |
| G03 | RF-V1-028, 032, 033 | Solicitud y resultado de adquisición emulados, con fallos identificables | **Simulado**; RF-V1-031 (adquisición real) fuera |
| G04 | RF-V1-040, 045, 046, 047, 048, 049, 050, 052, 053, 054, 055 | Registrar observaciones; comparar, identificar y registrar diferencia sin duplicarla; determinar elegibilidad | Núcleo **determinístico local** funcional |
| G05 | RF-V1-056, 057, 058, 059, 062, 065, 066, 068, 069 | Crear novedad y tratarla con analista/abogado respetando estados | Funcional limitado al escenario |
| G08 | RF-V1-110 | Registro local de acciones relevantes | Emulado; no auditoría inalterable/productiva |
| G09 | RF-V1-120, 121, 122, 125, 126, 127, 128, 129, 134 | Borrador, validación, autorización, emisión, control de visibilidad | Funcional local, sin publicación externa real |
| G10 | RF-V1-138, 140, 142, 143, 144, 145, 146 | Cartera propia, detalle, condición de cobertura y novedad publicada | Funcional sobre recursos sintéticos, permisos emulados |

**Importante:** mostrar parcialmente un RF no equivale a verificar completamente sus criterios de V1. Las fichas de esta sección tendrán estado de prueba **«demostrado en prototipo»** separado de **«verificado en producto»**.

### 5.2 Ampliación opcional posterior a la primera muestra

- G06 / RF-V1-071, 077, 082, 088–090: pantalla adicional dentro de V06 para mostrar una propuesta multimodal **predefinida** y su corrección humana; no afirmar que se utilizó un modelo real.
- G07 / RF-V1-091, 096, 100–101: tareas de seguimiento del tratamiento.
- G09 / RF-V1-124: anexo de ejemplo expresamente habilitado, con archivo sintético.
- G10 / RF-V1-147–148: consulta y descarga de anexo sintético autorizado.
- G09/G10 / RF-V1-135–137, 149–150: informes PDF, posterior.

La ampliación opcional no condiciona el éxito del escenario principal.

## 6. Datos de demostración y reproducibilidad

**Todos los nombres, radicados, actuaciones, fechas y valoraciones de este conjunto son ficticios.** La cadena de radicado `00000000000000000000001` es un identificador sintético de **23 dígitos** y no representa un expediente judicial real.

| Elemento | Fixture propuesto |
|---|---|
| Organización que opera | Estudio Jurídico Demo |
| Cliente A | Cliente Alfa S.A.S. (ficticio) |
| Cliente B | Cliente Beta S.A.S. (ficticio) |
| Proceso compartido | Radicado `00000000000000000000001` (sintético) |
| Seguimiento A | `SEG-A-001`, Cliente A; activo; ámbito de la cuenta externa A |
| Seguimiento B | `SEG-B-001`, Cliente B; activo; otro ámbito |
| Observación 1 | `OBS-001`, 2026-10-15; actuaciones `ACT-01` a `ACT-05` |
| Observación 2 | `OBS-002`, 2026-10-16; actuaciones `ACT-01` a `ACT-06` |
| Cambio detectado | `ACT-06` (incorporación) con evidencia sintética |
| Novedad del A | `NOV-A-001`, vinculada a `SEG-A-001` y al cambio elegible |
| Valoración jurídica | Texto de demostración redactado por actor abogado; no asesoría jurídica real |
| Publicación | `PUB-A-001` / versión `v1`; destinatario A; estado final Publicada |
| Cuenta externa A | Ámbito `{SEG-A-001}`; no toda la cartera por defecto |
| Cuenta externa B | Ámbito `{SEG-B-001}`; no puede leer `PUB-A-001` |

**Regla de comparación local:** para observaciones comparables sobre el mismo proceso, identificar actuaciones mediante clave estable ficticia (`ACT-XX`). Solo claves presentes en la segunda observación y no en la primera son candidatas a incorporación. Repetir la comparación o entrega no crea de nuevo el mismo cambio o novedad por seguimiento.

**Precisión sobre cliente B:** compartir un proceso judicial no habilita la publicación del cliente A a B. El prototipo podrá tener observaciones técnicas comunes, pero no reutilizará indiscriminadamente decisiones, novedades o publicaciones privadas. La elegibilidad del cambio para B se parametrizará aparte y no es objetivo principal de la muestra.

**Modo de reinicio:** un botón «Reiniciar demostración» restablece estados, fixtures y bitácora; permite repetir los escenarios sin manipular la base de datos real.

## 7. Reglas funcionales obligatorias de la muestra

| ID | Regla del prototipo | Referencia |
|---|---|---|
| P-RN-01 | Datos etiquetados permanentemente como «Demostración · información ficticia». | Transparencia del alcance |
| P-RN-02 | La primera observación constituye referencia inicial; no genera novedad histórica automáticamente. | RF-V1-023, 046 |
| P-RN-03 | Un resultado emulado Fallido/Incompleto no equivale a «sin cambios». | RF-V1-032, 143, 146 |
| P-RN-04 | La comparación utiliza reglas determinísticas, no LLM. | RF-V1-047–055 |
| P-RN-05 | Repetir adquisición/comparación de la misma observación no duplica cambios ni novedades. | RF-V1-053, 058 |
| P-RN-06 | Una novedad no se hace visible externamente por el solo hecho de detectarse o revisarse. | RF-V1-122, 134, 144 |
| P-RN-07 | La interpretación jurídica del escenario debe registrarla el abogado. | DEC-08, propuesta B3/B4 |
| P-RN-08 | El coordinador de la muestra es una persona distinta del preparador. | DEC-09, propuesta |
| P-RN-09 | La versión enviada a autorización no puede editarse sin crear nueva versión. | RF-V1-126, 128 |
| P-RN-10 | El estado Publicada solo aparece tras una operación local de publicación exitosa. | RF-V1-129, 130 |
| P-RN-11 | La cuenta externa está limitada a su cliente y a los seguimientos explícitamente asignados. | DEC-01 (seleccionada por autores) |
| P-RN-12 | Suspender al cliente bloquea temporalmente consulta externa ordinaria sin borrar histórico. | DEC-03 (seleccionada por autores) |
| P-RN-13 | Finalizar `SEG-A-001` bloquea consulta externa de sus recursos sin cambiar automáticamente `PUB-A-001` a Retirada. | DEC-04 (seleccionada por autores) |
| P-RN-14 | No hay consultas, datos judiciales reales ni documentos reales en la demostración. | Alcance PROTO-001 |

## 8. Modelo mínimo de estados para la demostración

- **Seguimiento:** Pendiente → Activo → Finalizado, con posibilidad de representar Suspendido solo para prueba secundaria. La terminación de un seguimiento cierra acceso externo ordinario según DEC-04 seleccionada, sin borrar histórico ni retirar automáticamente la publicación.
- **Adquisición emulada:** Pendiente → Exitosa / Incompleta / Fallida; registrar hora y procedencia `DEMO-FIXTURE`.
- **Novedad:** Pendiente revisión operativa → En revisión operativa → Pendiente revisión jurídica → Tratamiento definido → En seguimiento, según condiciones de revisión. No forzar estado Cerrada para permitir publicación de contenido revisado.
- **Publicación:** Borrador → Pendiente autorización → Autorizada → Publicada; Rechazada como desenlace alternativo. Una nueva edición tras solicitud de aprobación requiere nueva versión.

**Las denominaciones y guardas definitivas deben cotejarse con ME-01, ME-02, ME-03 y ME-05.** Estos subconjuntos de demostración no sustituyen las máquinas de estados del producto.

## 9. Criterios de aceptación del prototipo (diseño, no ejecución)

| ID | Precondición | Acción | Resultado esperado / evidencia |
|---|---|---|---|
| PROTO-AT-01 | Sin proceso cargado | Registrar el radicado sintético | Proceso visible en cartera con identidad estable |
| PROTO-AT-02 | Proceso y Cliente A válidos | Crear/activar SEG-A-001 | Seguimiento activo y vinculado a A |
| PROTO-AT-03 | No existe referencia inicial | Cargar OBS-001 | Se establece línea base; ninguna novedad |
| PROTO-AT-04 | OBS-001 comparable | Cargar OBS-002 y comparar | Se identifica exactamente `ACT-06` como incorporación |
| PROTO-AT-05 | Cambio ya registrado | Repetir comparación | Sin duplicación de cambio |
| PROTO-AT-06 | Novedad ya generada para A | Repetir entrega | Sin duplicación de NOV-A-001 |
| PROTO-AT-07 | Novedad en revisión operativa | Confirmar hecho y solicitar abogado | Registro de decisión y estado de revisión jurídica |
| PROTO-AT-08 | Evidencia disponible | Abogado registra valoración | Valoración trazable asociada a NOV-A-001 |
| PROTO-AT-09 | Revisión exigida completada | Preparar versión v1 | Borrador identificado, no visible externamente |
| PROTO-AT-10 | Versión pendiente autorización | Coordinador distinto autoriza | Versión Autorizada, no aún Publicada |
| PROTO-AT-11 | Versión Autorizada | Ejecutar publicación local | Estado Publicada y disponibilidad a cuenta A autorizada |
| PROTO-AT-12 | Cuenta B y enlace de publicación A | Abrir el recurso A | Denegación en lógica de demostración; sin mostrar contenido privado |
| PROTO-AT-13 | Cliente A suspendido | Consultar recurso A | Acceso ordinario bloqueado; publicación conserva estado interno |
| PROTO-AT-14 | SEG-A-001 activo, publicación vigente | Finalizar seguimiento y volver a portal A | Acceso externo ordinario cerrado; histórico interno preservado |
| PROTO-AT-15 | Adquisición emulada Fallida | Ver detalle del seguimiento | Mensaje «cobertura no verificada», no «sin cambios» |
| PROTO-AT-16 | Cambios de estado realizados | Reiniciar demostración | Datos iniciales y bitácora restablecidos |
| PROTO-AT-17 | Usuario externo A sin SEG-A-002 en su ámbito | Intentar abrir SEG-A-002 | Acceso denegado aun siendo del mismo cliente |
| PROTO-AT-18 | Publicación con texto modificado después de enviar | Intentar conservar aprobación previa | Se exige nueva versión/solicitud; nunca se publica texto distinto |

**Evidencias de verificación previstas:** capturas de cada paso, registro visible de estados, listado de diferencias, evento local de rechazo, versión autorizada, capturas de portal A y B, resultados de reinicio. **Ningún caso está ejecutado** hasta que exista el prototipo.

## 10. Diseño técnico provisional, sin atar la arquitectura final

**Opción recomendada para el prototipo:** Vue 3 + Vite + TypeScript, con datos sintéticos versionados y estado local. El comparador determinístico se mantiene como módulo puro reutilizable, independiente de componentes visuales; reglas de transición como funciones verificables. Puede utilizarse una persistencia local opcional, con opción de reinicio y aviso de no almacenar datos reales.

**Restricciones:** no afirmar que el selector de actores autentica; no afirmar que el filtrado cliente del navegador implementa seguridad multi-tenant; no describir respuestas fixture como consultas CPNU ni propuestas predefinidas como salida de un LLM real. Una validación futura de seguridad exige backend, almacenamiento y controles propios de la arquitectura de V1.

### 10.1 Organización conceptual

```text
src/
  demo/                 # identidades sintéticas, fixtures, reinicio
  domain/               # proceso, seguimiento, observación, actuación, novedad, publicación
  comparison/           # función determinística e idempotencia
  policies/             # reglas de alcance y transiciones simuladas
  views/                # ocho vistas agrupadas por actor
  components/           # elementos compartidos
  tests/                # escenarios determinísticos y de estados
```

No impone una arquitectura productiva de microservicios ni estructura final de base de datos.

## 11. Guion de presentación

1. Explicar problema de múltiples procesos judiciales y necesidad de vigilancia trazable.
2. Mostrar cartera y seguimiento del cliente Alfa.
3. Enseñar línea base de cinco actuaciones y segunda observación de seis.
4. Ejecutar comparación; mostrar la actuación adicional y su evidencia.
5. Revisar y escalar novedad al abogado.
6. Registrar valoración profesional de ejemplo.
7. Preparar y aprobar publicación con dos identidades distintas.
8. Acceder al portal Alfa y visualizar publicación.
9. Mostrar acceso denegado para Beta y/o cuenta sin ámbito.
10. Finalizar seguimiento Alfa, demostrar bloqueo externo y preservación del historial interno.
11. Explicar límites: fuente/LLM simulados, sin seguridad productiva, y vínculo con requisitos reales.

## 12. Artefactos de salida y definición de terminado

| Artefacto | Entrega | Condición |
|---|---|---|
| PROTO-001 | Esta especificación | Aprobación del alcance por autores |
| PROTO-DAT-001 | Fixtures sintéticos versionados | Consistencia temporal; 23 dígitos; sin datos reales |
| PROTO-UX-001 | Mapa de navegación y diseños seleccionados | Ocho vistas; roles, estados vacíos y bloqueos |
| PROTO-CMP-001 | Comparador determinístico | Pruebas sobre baseline, incorporación y duplicados |
| PROTO-APP-001 | Aplicación interactiva local | Recorrido principal funciona sin red externa |
| PROTO-VAL-001 | Protocolo y resultados | 18 criterios ejecutados y evidenciados |
| PROTO-DEMO-001 | Guion y capturas | Exposición reproducible con reinicio |

**Definición de terminado (prototipo):** se recorren los pasos del guion, el comparador produce el cambio esperado, hay revisión y aprobación humana diferenciada, el cliente A ve solamente su contenido, el cliente B no lo ve, la finalización bloquea acceso externo, se registran resultados de aceptación, y todos los datos simulados están claramente identificados.

## 13. Riesgos y decisiones pendientes

| ID | Asunto | Tratamiento en prototipo | Pendiente para V1 |
|---|---|---|---|
| DP-01 | Mecanismo real CPNU/fuentes | Emular adquisición con fixtures | Factibilidad y autorización real |
| DP-02 | Modelo LLM/documentos | Omitir en muestra principal o respuesta predefinida declarada | Proveedor, tratamiento y prueba multimodal |
| DP-03 | DEC-08 revisión jurídica | Utilizar abogado para la interpretación demostrada | Selección de autores y ratificación jurídica |
| DP-04 | DEC-09 segregación | Personas distintas por precaución | Selección y ratificación organizacional |
| DP-05 | DEC-04 finalización | Bloquear acceso a recursos del seguimiento finalizado | Política final de informes mixtos y validación externa |
| DP-06 | Cotejo histórico 57 RF | Trazar sin declararlos aprobados | Ratificación catálogo RF-CAT |
| DP-07 | Seguridad real | Selector de identidades de prueba | RNF, backend y modelo de acceso productivo |

## 14. Siguiente paso

**PROTO-DAT-001 + PROTO-UX-001**: concretar fixtures, transiciones, mensajes de error y mapa de navegación; después elegir el diseño visual antes de codificar. No bloquear la muestra por el cierre total de RF-CAT-001 ni confundir resultados de prototipo con validación de la V1.
