# TOBE-001 — Modelo TO-BE de vigilancia judicial

**Versión:** 0.2 (candidata)  
**Estado:** sujeto a revisión y validación del dominio  
**Propósito:** documento de modelado anterior a la ERS, no constituye aprobación final ni especificación ejecutable.

## Cobertura y archivos

| Archivo | Subprocesos | Inicio | Finales principales |
|---|---|---|---|
| `BPMN-01_Alta_y_activacion.bpmn` | SP-01 | Solicitud de seguimiento | Seguimiento preparado o ya existente |
| `BPMN-02_Vigilancia_y_cambios.bpmn` | SP-02, SP-03 | Solicitud individual o condición programada | Línea base / sin cambios / posibles novedades / incidencia |
| `BPMN-03_Revision_y_publicacion.bpmn` | SP-04, SP-05, SP-06 | Novedad pendiente | Descarte / pendiente / rechazo / publicación autorizada |
| `BPMN-04_Portal_cliente.bpmn` | SP-07 | Solicitud de autenticación o consulta autenticada | Acceso validado / denegado / consulta autorizada |

Los cuatro XML son modelos BPMN 2.0 **no ejecutables**, con elementos BPMN y coordenadas DI para representación gráfica. Se validó su sintaxis XML, unicidad de IDs y referencias de flujos de secuencia. No se ha probado su ejecución en un motor BPMN, ni se ha validado contra el XSD oficial.

## Fronteras del modelo

- **Organización operadora:** una instalación V1, varios clientes destinatarios, operadores internos con permisos segregados.
- **Cliente externo:** una cuenta externa vinculada a un cliente en V1; acceso exclusivamente a información habilitada y publicada según su autorización.
- **Proceso judicial:** entidad jurídica consultada, con observaciones de fuente.
- **Seguimiento:** relación cliente-proceso con responsables, políticas y novedades privadas.
- **Consulta:** intento de adquisición con resultado, estado, fuente, fecha y evidencia; puede fallar sin invalidar historial.
- **Observación:** representación conservada de información recibida; solo se compara si cumple criterios de validez y comparabilidad.
- **Cambio:** diferencia técnica determinística entre observaciones comparables.
- **Novedad:** objeto de gestión de un seguimiento, no equivalente a cambio ni conclusión jurídica.
- **Publicación:** versión autorizada para destinatarios, independiente del estado operativo de la novedad.

## Precisiones BPMN

1. No representar que el cliente debe iniciar sesión justo al publicar una novedad. Son procesos asincrónicos separados.
2. La fuente judicial y el proveedor LLM son pools externos; los conectores constituyen tareas internas.
3. Los flujos de secuencia se mantienen en el pool de la organización operadora; se usan flujos de mensaje hacia participantes externos.
4. La programación recurrente se representa como un evento de inicio de temporizador (frecuencia de ejecución **pendiente de definir**).
5. La consulta individual por radicado es la unidad de adquisición; varios seguimientos pueden activar consultas individuales.
6. La primera observación válida establece línea base; una consulta fallida no constituye prueba de ausencia de cambios.
7. Los documentos y la invocación de LLM son condicionales; las propuestas nunca son conclusiones jurídicas validadas.
8. Separación de responsabilidad: analista comprueba operativamente; abogado valida lo jurídico; coordinador autoriza publicación.
9. Los resultados compartidos de fuente judicial solo pueden reutilizarse si lo permiten la procedencia y las reglas de confidencialidad; la gestión entre clientes no se comparte.
10. Las respuestas parciales o discrepantes de fuentes no deben fusionarse automáticamente como observaciones completas.

## Decisiones pendientes antes de línea base de ERS

| ID | Cuestión | Riesgo o dependencia |
|---|---|---|
| PD-01 | Acceso automatizado permitido a SAMAI y Publicaciones Procesales | Externo: factibilidad y autorización |
| PD-02 | Reglas por fuente para completitud y comparabilidad | Falsos cambios / omisiones |
| PD-03 | Identidad estable de actuación, deduplicación y comparaciones entre fuentes | Duplicados / diferencias ambiguas |
| PD-04 | Política de frecuencia, reintento, actualización y proveedor no disponible | Operación confiable |
| PD-05 | Taxonomía de novedades y descarte | Criterio de tratamiento |
| PD-06 | Documentos, campos LLM, proveedor y tratamiento de datos | Alcance de IA y privacidad |
| PD-07 | Estados, transiciones y condiciones de cierre de novedades | Modelo funcional |
| PD-08 | Alcance de visibilidad de resultados objetivos no revisados en portal | Confidencialidad y comunicación |
| PD-09 | Política de retirada, rectificación y republicación | Versionado y responsabilidad |
| PD-10 | Restricciones reales por cliente, usuario, expediente y documento | Autorización |

## Reglas críticas

- Nunca equiparar una respuesta vacía, fallida o parcial a ausencia de cambios.
- No crear novedades iniciales sobre toda la historia durante la primera observación.
- No duplicar novedades sobre el mismo cambio por reintentos equivalentes.
- No publicar una conclusión jurídica sin validación de abogado.
- No permitir a un cliente leer notas, documentos o seguimientos privados de otro cliente.
- Registrar autor, fecha, procedencia, cambios y versiones de publicación.

## Puerta de salida de TOBE-001

Se considera listo para apoyar la ERS cuando el equipo haya revisado escenarios normales y excepcionales, la matriz RACI, el alcance de los roles, la política de publicación, la trazabilidad de datos y los riesgos de integración, y haya registrado los pendientes que impidan aprobar requisitos de automatización real.

**Alcance de evidencia:** estos diagramas formalizan las decisiones de análisis del equipo en esta conversación; no acreditan validación empírica con personal jurídico ni autorizaciones de fuentes judiciales.
