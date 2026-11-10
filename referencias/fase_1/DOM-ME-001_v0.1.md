---
documento: DOM-ME-001
version: 0.1-candidata
fecha: 2026-11-10
estado: subconjunto de estados propuesto para el prototipo; no reemplaza ME de V1
---

# DOM-ME-001 — Estados, guardas y transiciones del primer incremento

## 1. Criterios de diseño

- Estados del dominio separados de los estados de presentación y de errores HTTP.
- Cambio de estado solo por operación permitida, con permisos actuales y guarda explícita.
- Transiciones registran persona/cuenta que actuó, instante, evidencia y motivo cuando aplique.
- No saltar estados obligatorios y no convertir errores técnicos en éxito de negocio.
- `Cliente.Suspendido` y `Seguimiento.Finalizado` son ejes **independientes**, no una máquina conjunta.
- Los nombres son semánticos; la representación literal en API/DB se decidirá en fases 3–4.

## 2. Cliente — subconjunto para DEC-03

| Origen | Operación | Destino | Guarda | Efecto |
|---|---|---|---|---|
| Activo | SuspenderCliente | Suspendido | Actor interno habilitado, motivo registrado | Bloquear accesos externos y adquisiciones ordinarias exclusivas de A; preservar datos |
| Suspendido | ReactivarCliente | Activo | Actor interno habilitado, justificación/registro | Rehabilitar evaluación normal de acceso; **sin afirmar cobertura retroactiva** |
| Suspendido | SuspenderCliente | — | Ya suspendido | No duplicar transición; reintento idempotente o error según API-001 |

**No** modifica automáticamente estados de todos los seguimientos ni marca `Retirada` a publicaciones. `DEC-03` seleccionada por autores; ratificación organizacional pendiente.

## 3. Seguimiento — subconjunto ME-01

| Origen | Operación | Destino | Guarda y efecto |
|---|---|---|---|
| Pendiente | ActivarSeguimiento | Activo | Cliente/proceso válidos, actor interno autorizado, seguimiento propio; historial |
| Activo | FinalizarSeguimiento | Finalizado | Actor interno habilitado, motivo; acceso externo posterior bloqueado |
| Finalizado | ConsultarInternamente | Finalizado | Permiso interno vigente, lectura histórica controlada |
| Finalizado | ActivarSeguimiento | — | Prohibido en demo: no reactivación implícita |

**Nota:** el estado `Suspendido` de **seguimiento** existe conceptualmente en V1 pero su política de consulta externa está pendiente (DEC-F0-001/DEC-F1-001). No se implementará por inferencia. Tampoco la suspensión de cliente impone `Seguimiento.Suspendido`.

**Referencia basal:** no es estado ME-01. Se administra como estado/atributo separado `SinBaseline → Baseline(OBS-001)` al aceptar primera observación comparable, con control de concurrencia. Observaciones fallidas no cambian este hecho.

## 4. Adquisición y observación — subconjunto G03/G04

### 4.1 Solicitud/ejecución de adquisición

| Origen | Evento | Destino | Regla |
|---|---|---|---|
| Pendiente | Fixture completo válido | Exitosa | Resultado + procedencia + observación preservada |
| Pendiente | Fixture parcial | Incompleta | Causa, dato recibido y brecha; no comparación confirmada |
| Pendiente | Error de fuente/fixture | Fallida | Causa y fecha; no crear observación comparable |
| Exitosa/Incompleta/Fallida | Segundo resultado de mismo intento | — | No reescribir; un reintento es identificable separadamente |

La observación resultante tiene clasificación de calidad independiente: `Comparable`, `NoComparable` o `Indeterminada`. `Exitosa` de transporte no basta sin verificación de identidad, completitud y coherencia.

### 4.2 Resultado de comparación

| Resultado | Condición | Permitido como entrada de novedad |
|---|---|---|
| BaselineEstablecida | Primera observación aceptada para seguimiento | No: inicializa referencia |
| DiferenciasConfirmadas | Par ordenado comparable, identidad estable | Sí, solo tras elegibilidad de seguimiento |
| SinDiferenciasConfirmadas | Par comparable y conjunto igual | No; solo para ese par/alcance, no extrapolar a cobertura total |
| NoComparable | Incompleta, caída, proceso equivocado o reglas incompatibles | No |
| Indeterminada | Identidad ambigua o evidencia insuficiente | No; requiere evaluación manual fuera de recorrido |

**Riesgo:** una comparación técnica compartida entre dos observaciones no decide elegibilidad por cliente. A y B pueden divergir incluso usando el mismo par.

## 5. Novedad — subconjunto ME-03

| Origen | Acción | Destino | Guarda y evidencia |
|---|---|---|---|
| (No existe) | GenerarNovedad | Pendiente revisión operativa | Cambio confirmado, seguimiento activo/elegible y unicidad `(seguimiento,cambio)` |
| Pendiente revisión operativa | IniciarRevision | En revisión operativa | Analista autorizado; responsable y fecha |
| En revisión operativa | EscalarAbogado | Pendiente revisión jurídica | Hechos revisados, evidencia y motivo de escalamiento |
| Pendiente revisión jurídica | RegistrarValoracion | Tratamiento definido | Abogado autorizado, conclusión ficticia explícita, evidencia y decisión |
| Tratamiento definido | MantenerSeguimiento | En seguimiento | Decisión de tratamiento registrada; seguimiento de obligaciones fuera de demo |
| En revisión operativa | DescartarJustificadamente | Descartada | **No utilizado en guion;** requiere causa/evidencia, no borra cambio |

- En el recorrido de demostración **solo** se exige ruta `Pendiente revisión operativa → En revisión operativa → Pendiente revisión jurídica → Tratamiento definido`.
- `Pendiente información`, `Descartada`, `Cerrada`, rectificación y transiciones de tareas pertenecen al modelo V1, pero no deben fabricarse sin ratificación ni implementación de capacidades asociadas.
- Novedad `Tratamiento definido` puede alimentar preparación de una comunicación revisada; no requiere forzar `Cerrada`.
- Analista no puede crear valoración jurídica y abogado no puede saltarse revisión operativa.

## 6. Publicación y versión — subconjunto ME-05

| Origen | Acción | Destino | Guarda y efecto |
|---|---|---|---|
| (No existe) | CrearBorrador | Borrador | Seguimiento y destinatario de A, contenido y autores registrados; no visible |
| Borrador | SolicitarAutorizacion | Pendiente autorización | Congelar snapshot exacto (contenido/destinatario, lista preparadores); revisión jurídica exigida para este fixture |
| Pendiente autorización | AprobarVersion | Autorizada | Coordinador habilitado, `personaId` distinto de todo preparador, versión fija; NO visible aún |
| Pendiente autorización | RechazarVersion | Rechazada | Aprobador habilitado + motivo; nueva corrección es nueva versión |
| Autorizada | PublicarLocalmente | Publicada | Confirmar selección de versión vigente en API protegida y commit consistente |
| Autorizada | FallaPublicacion | Autorizada | Registrar intento fallido; no externalizar ni marcar `Publicada` |
| Pendiente autorización/Autorizada | IntentarModificarSnapshot | — | Rechazar mutación; para cambiar contenido/destinatario crear versión nueva |

`Publicada → Retirada/Reemplazada` se modela en RF-CAT §16.3, pero se excluye del guion actual. Si Fase 3 incluye tablas de versiones futuras, no asumir automáticamente flujos completos de retirada. Mantener `0..1` versión vigente en publicación. Aprobación de versión anterior **nunca se hereda** por una nueva.

**Separación crucial:** una versión puede permanecer `Publicada` internamente mientras DEC-03/DEC-04 hace que el portal ya no la permita consultar. Estado ≠ permiso actual.

## 7. Matriz de operaciones / actores (solo guion, sin asumir privilegios universales)

| Operación | Analista | Abogado | Preparador | Coordinador | Externo A/B |
|---|---:|---:|---:|---:|---:|
| Registrar y activar seguimiento | Permiso de demo | No por defecto | No | Según permiso explícito | No |
| Incorporar fixture/comparar | Permiso de demo | Consulta interna si autorizado | No | No por defecto | No |
| Iniciar revisión/escalar | Sí, si asignado | No por defecto | No | No | No |
| Registrar valoración jurídica | No | Sí, si habilitado | No | No por defecto | No |
| Crear y someter versión | No por defecto | No por defecto | Sí | No por defecto | No |
| Aprobar versión | No | No por defecto | No | Sí, si persona distinta | No |
| Publicar versión autorizada | No | No | No por defecto | Sí, si habilitado | No |
| Leer publicación | Solo con permiso interno | Solo con permiso interno | Solo con permiso interno | Solo con permiso interno | Sí, si todas las condiciones contextuales |
| Suspender cliente/finalizar seguimiento | Permiso interno de demo explícito | No por defecto | No | Según permiso explícito | No |

`Sí` en esta matriz se refiere a **rol elegible**, no a que cualquier persona con ese nombre pueda operar sobre todo recurso. Se requiere autorización contextual en cada caso. La facultad de administrar ámbitos y estados debe cerrarse en Fase 4.

## 8. Diagramas de estados

Incluidos también en `diagramas/`:

- `DOM-ME-NOVEDAD.mmd`
- `DOM-ME-PUBLICACION.mmd`
- `DOM-ME-SEGUIMIENTO.mmd`

## 9. Pruebas de guardas mínimas

| ID | Dado / cuando | Entonces | Referencia |
|---|---|---|---|
| MG-01 | OBS-001 primera comparable de A | Baseline sin novedad | AT-03 |
| MG-02 | A compara segunda OBS; B comienza baseline en OBS-002 | Solo A obtiene NOV-A-001 | AT-04/06 |
| MG-03 | Analista intenta registrar juicio jurídico | Denegar transición | AT-08 (+ negativa) |
| MG-04 | Versión Borrador externa | Denegar lectura | AT-09 |
| MG-05 | Preparador y aprobador comparten personaId | Denegar aprobación, registrar intento | AT-10 (+ negativa) |
| MG-06 | Versión Autorizada pero no publicada | Denegar lectura; estado correcto | AT-10 |
| MG-07 | Falla publicación local | Mantener Autorizada; no seleccionar vigente | Complementaria |
| MG-08 | A es suspendido, aunque su publicación está Publicada | Bloquear lectura sin alterar publicación | AT-13 |
| MG-09 | Seguimiento A Finalizado con publicación Publicada | Bloquear lectura; conservar historia | AT-14 |
| MG-10 | Edición material posterior a solicitud | Nueva versión + aprobación propia | AT-18 |

**Control de consistencia:** estas tablas son especificación candidata de la demostración, no evidencia de ejecución ni validación de todas las rutas de ME-01/ME-03/ME-05 de V1.
