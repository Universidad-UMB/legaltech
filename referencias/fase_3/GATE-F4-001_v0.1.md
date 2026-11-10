---
documento: GATE-F4-001
version: 0.1
fecha: 2026-11-10
estado: transferencia del diseño de datos a API y seguridad
---
# GATE-F4-001 — Entrada a Fase 4: API, autenticación y seguridad

## Entregas listas como **diseño candidato**
- 24 tablas lógicas/físicas especificadas, tipos y nulabilidad en `DATA-DIC-001` y DDL de referencia.
- Modelo ER por núcleos: datos judiciales, identidad/ámbitos y publicaciones.
- FKs de pertenencia cliente/proceso, UK de novedad, alcance, índices, triggers y diseño de transacción de publicación.
- Estrategia Alembic y plan de pruebas negativas, concurrencia y rollback.
- Decisiones técnicas y legales pendientes explícitas.

## Preguntas que Fase 4 SÍ debe cerrar

| F4-ID | Pregunta | Resultado mínimo |
|---|---|---|
| F4-01 | ¿Cómo inicia/cierra sesión la cuenta DEMO y dónde viaja token? | OpenAPI, expiración/revocación, protección CSRF si cookie, evitar fugas |
| F4-02 | ¿Qué permiso requiere cada operación? | Matriz rol × operación × estado × ámbito; sin rol universal |
| F4-03 | ¿Cómo se identifica el recurso autorizado? | `tenant` derivado de cuenta y consulta restringida; ninguna FK equivale a permiso |
| F4-04 | ¿Qué cuerpos, DTO, respuestas, estados HTTP y errores? | OpenAPI 3.1 y errores consistentes sin enumeración de recursos |
| F4-05 | ¿Qué idempotencia HTTP? | Clave de request donde aplique; 409/200/201 consistentes; no reusar sesión fallida |
| F4-06 | ¿Cómo demostrar publicación segura? | Caso de uso atómico versión+puntero+auditoría, con fallos inyectados |
| F4-07 | ¿Cómo se tratan conflictos de suspensión/fin? | Contrato de instante de autorización, 403/404 sin BOLA |
| F4-08 | ¿Cuáles RNF son obligatorios en prototipo? | Seguridad, validación, auditoría, testabilidad, mantenimiento y alcance local |
| F4-09 | ¿Cómo operar reintentos y errores de fuente? | Sin 'no changes' falso; códigos diferenciados y trazabilidad |
| F4-10 | ¿Qué permanece sin definir? | Diferenciar DEMO vs V1 y no completar políticas jurídico-legal sin aprobación |

## No implementar todavía
- No generar CRUD universal por tabla.
- No exponer DTO con `client_id` arbitrario para operaciones externas.
- No agregar RLS/productivo, motor de permisos genérico ni múltiples services solo porque existan 24 tablas.
- No escribir endpoints de reset ni secretos de seeds para producción.

## Puerta de entrega a agente

Cerrar API/SEC y TEST, aceptar ADR/DATA/DOMAIN candidatos, ejecutar DDL como Alembic real y pruebas de integración sobre PostgreSQL. Hasta entonces el diseño es revisable y apto para seguir analizando, no código supuestamente aprobado.
