# HANDOFF-ARQ-001 — Contexto para análisis de arquitectura backend LegalTech

**Versión:** 0.1 · **Fecha de consolidación:** 2026-11-09 · **Estado:** Documento de transferencia entre sesiones; NO es diseño aprobado.

## 1. Decisión de alcance de la nueva sesión

Diseñar **arquitectura de backend para el producto LegalTech V1**, identificando un **primer incremento implementable que sirva a PROTO-001**. No asumir que PROTO-001 exige backend: originalmente contempla frontend Vue 3, Vite y TypeScript con datos sintéticos y estado local. La nueva sesión debe justificar el valor y el costo de agregar un backend demostrativo.

**Objetivo:** arquitectura técnicamente coherente, trazable, segura por diseño y evolutiva, evitando sobreingeniería. No escribir código ni fijar stack o infraestructura definitiva sin análisis previo.

## 2. Fuentes obligatorias y prelación

1. `01_Requisitos/RF-CAT-001_v0.8.md` — catálogo maestro de 150 requisitos funcionales activos, 150 casos de aceptación, reglas, trazabilidad y modelos. **57 enunciados reconstruidos siguen pendientes de cotejo literal**. Catálogo candidato, no aprobado.
2. `02_Decisiones/RF-DEC-001_v0.4.md` — registro de 18 decisiones, con estado diferenciado entre selección de autores y validación externa. **DEC-01**, **DEC-03** y **DEC-04** seleccionadas por autores; **DEC-08** y **DEC-09** son propuestas no adoptadas formalmente por autores; ratificación organizacional pendiente para todas.
3. `03_Prototipo/PROTO-001_v0.1.md` — especificación demostrativa de 8 vistas, 47 RF vinculados con distinta fidelidad, 18 pruebas planeadas y datos ficticios. No implica solución de producción.
4. `04_Proceso_TO_BE/TOBE-001_Especificacion_y_revision.md` y `BPMN-01...04` — flujos de operación; usar para detectar límites transaccionales y responsabilidades, no tomar BPMN como contratos API definitivos.

En discrepancias, **no corregir silenciosamente las fuentes**. Proponer resolución en registro ADR/pendientes y señalar versión y apartado implicados. DEC-04 v0.4 reemplaza recomendación previa de permitir consulta externa tras finalización.

## 3. Reglas de dominio esenciales para arquitectura

- Cliente jurídico ↔ seguimiento es relación independiente: varios clientes pueden seguir el mismo radicado (23 dígitos); **línea base, elegibilidad de novedades, decisiones, versiones, visibilidad y ámbito de acceso son por seguimiento/cliente**.
- Fuente judicial y observación técnica potencialmente compartibles, **sin compartir** automáticamente novedades, valoraciones ni publicaciones privadas.
- Una primera observación constituye línea base; no crea automáticamente novedades históricas. Resultado Fallido/Incompleto no equivale a «sin cambios» ni a cobertura continua.
- Comparación de actuaciones determinística, trazable e idempotente, con identidad que puede ser ambigua; no fusionar actuaciones inciertas automáticamente.
- Operación del analista separada de valoración jurídica del abogado; publicación externa solamente tras autorización de versión fija. Un cambio posterior exige nueva versión; retirada o sustitución no puede permanecer accesible como versión vigente.
- G06: análisis documental mediante **LLM multimodal preexistente**, con revisión humana. **No imponer OCR separado, extracción nativa por reglas, ni entrenamiento/fine-tuning**. Integración y tratamiento de datos reales pendientes de autorización/factibilidad. No usar LLM para la comparación determinística.
- DEC-01: ámbitos configurables por cuenta externa, sin acceso indiscriminado a toda la cartera del cliente.
- DEC-03: suspensión de cliente bloquea acceso externo ordinario sin borrar histórico o interrumpir otro cliente.
- DEC-04: al finalizar seguimiento, **cerrar acceso externo ordinario incluso a publicaciones vigentes**, sin alterar automáticamente estado de publicación ni borrar historial interno.
- DEC-08/09: matriz de revisión jurídica y separación entre preparador/aprobador son **propuestas**; se usan como salvaguardas de la demostración, pero no presentar como ratificadas.

## 4. Alcance de la muestra

Recorrido del PROTO-001: proceso + seguimiento A → OBS-001 inicial con cinco actuaciones → OBS-002 con seis actuaciones → nueva ACT-06 → NOV-A-001 → analista → abogado → borrador PUB-A-001 v1 → coordinador independiente → publicación → portal A; pruebas negativas de aislamiento B, suspensión y finalización. Datos exclusivamente sintéticos. Fuente judicial y LLM emulados. Separar explícitamente seguridad real de controles demostrativos locales.

## 5. Arquitectura: preguntas que deben resolverse ANTES de elegir tecnología

- ¿Se diseñará backend solo en papel para V1 o se añadirá un backend ejecutable al prototipo? Definir valor, riesgos y esfuerzo.
- ¿Cuáles son los módulos del dominio y sus límites? ¿Qué transacciones requieren consistencia fuerte y cuáles admiten asincronía?
- ¿Cómo modelar proceso judicial global, seguimiento por cliente, observación técnica, línea base, actuación, cambio, novedad, valoración, evidencia, tarea, publicación/versionado?
- ¿Qué modelo de autorización (roles+ámbitos+recurso+estado), tenencia y acceso seguro resuelve DEC-01/03/04? ¿Cómo prohibir acceso directo por ID al objeto de otro cliente?
- ¿Qué políticas de adquisición, reintentos, idempotencia, observabilidad y manejo de fallos hacen viable la vigilancia? Fuentes públicas y permiso real NO validados.
- ¿Cómo gestionar versiones inmutables de PDF, aprobación del artefacto exacto, visibilidad, retiro y auditoría?
- ¿Qué eventos de dominio necesita el flujo sin introducir prematuramente infraestructura distribuida?
- ¿Qué calidad no funcional se necesita medir? RNF-001 aún no está elaborado.
- ¿Cómo evolucionar desde fixtures sintéticos hacia adaptadores reales sin reescribir la lógica de dominio?

## 6. Entregables solicitados para la nueva sesión, por fases

0. Diagnóstico de suficiencia y lista de decisiones/bloqueos, distinguiendo producto V1 y prototipo.
1. Mapa de dominios, módulos y responsabilidades; casos de uso y RF asociados; invariantes.
2. Comparación motivada de alternativas: monolito modular vs microservicios (no decidir por tendencia), con ADR inicial.
3. Diseño lógico C4: contexto, contenedores, componentes backend; límites externos y escenarios de fallo.
4. Modelo conceptual/lógico de datos, entidades/relaciones, claves, tenencia y versionado; decisiones de almacenamiento justificadas.
5. Contratos preliminares de API, operaciones/estados, idempotencia y errores; esquema de eventos si se necesitan.
6. Seguridad, roles/ámbitos, privacidad, auditoría, observabilidad; RNF candidatos medibles.
7. Despliegue y plan de implementación incremental (vertical slice de PROTO-001) con pruebas.
8. Matriz de trazabilidad RF → componente → datos/API → prueba y listado ADR/pendientes.

**Protocolo:** avanzar una fase a la vez. Primero revisar fuentes y producir Fase 0; no diseñar todas las capas de una vez ni generar código sin solicitud. Cuando falten datos, marcar hipótesis verificables, no inventar políticas ni capacidades de las fuentes judiciales.

## 7. Controles de calidad del análisis

- Diferenciar decisión de autores, decisión pendiente de dominio, dato hipotético, diseño candidato y validación técnica ejecutada.
- Rastrear referencias exactas `RF-V1-XXX`, `DEC-XX`, `PROTO-AT-XX` cuando existan.
- Consistencia de datos multicliente y línea base por seguimiento, casos de aislamiento, publicación no visible antes de estar publicada y denegación externa posterior a finalización.
- Separar prototipo emulado de MVP conectado a servicios reales.
- Documentar tradeoffs y justificar elecciones con objetivos de tesis, no con volumen ficticio de usuarios.

## 8. Nota de integridad documental

No se incluyen como documentos ya elaborados `PROTO-DAT-001`, `PROTO-UX-001`, `RNF-001`, POC de fuentes ni POC de LLM, porque todavía no se ha verificado la existencia de versiones aprobadas en este paquete. Son tareas posteriores.
