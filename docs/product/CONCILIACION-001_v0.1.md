# CONCILIACION-001 — Contrato transversal, diferencias y supuestos a verificar

| Riesgo de divergencia | Fuentes | Resolución o tratamiento Fase 5 |
|---|---|---|
| Prototipo Vue en memoria vs backend persistente | PROTO-001 frente a SCOPE-001 | El prototipo backend es ampliación explícita ya planteada; mantener fixtures ficticios, no atribuir seguridad ni consulta real a versión original |
| Adopción adelanta cursor antes de evaluar | DOMAIN-001, API-001, DEC-F4-001 | Propuesta DF5-01: baseline libre de historial; posterior evaluación anterior a avance, con lock, 409 sin evaluación; aceptación obligatoria |
| `SEG-A-002` y máximo un seguimiento activo | DATA-DDL-001 índice parcial, AT-17 | Propuesta DF5-02: proceso PROC-002, mismo cliente Alfa, cuenta Alfa sin scope A2; AT-17 preservado |
| DEC-08/09 no ratificadas | RF-DEC-001, DEC-F1..4 | Salvaguardas de demostración explícitas, no política jurídica de V1; aceptación de autores DF5-03/04 |
| API referencia client_id y DDL tenant context | API-001, DATA-001, SEC-001 | Solo endpoints internos autorizados reciben client_id según DTO; cualquier portal toma tenant desde sesión/relaciones, NO el request |
| Criterio de respuesta por falta de publicación | API-001/SEC-001 | 200 available=false solo si principal tiene acceso y seguimiento/client activos; 404 para ajeno/suspendido/finalizado |
| Autorización de preparador/auditor | DOM-ME, DATA, SEC | persona distinta por person_id, cuenta asignada vigente, versión frozen hash, histórico inmutable |
| Error FastAPI 422 por defecto | OpenAPI 3.1.1 y RFC 9457 | Transformar errores al esquema problem+json definido; comparar OpenAPI runtime vs archivo fuente |
| SQL candidato vs migración real | DATA-DDL-001, DATA-MIG-001 | DDL es referencia, no ejecutar como atajo; Alembic revisado y pruebas reales sobre Postgres descartable en INC-00+ |
| Validación estática ≠ funcionamiento | Fases 0..4 | 18 AT + 36 API + 39 DB sólo especificadas; estado NOT_EXECUTED hasta CI/entorno real |
| Mismas observaciones pueden pertenecer a varios clientes | DATA-001, DOMAIN-001 | Observaciones públicas internas por proceso; cambios/novedades/reviews/versiones pertenecen a seguimiento; 404 por recurso |
| Identidades jurídicas y privacidad reales | RF-CAT, PROTO-001 | Sin scraping real, OCR, LLM, notificaciones productivas, PDF, datos reales, ni conclusiones jurídicas automatizadas en primer incremento |

**Registro de cambios:** toda contradicción nueva se eleva como bloqueo con artefacto/versión, asunto, alternativa, decisión de autores y pruebas de regresión. No resolver en silencio editando OpenAPI o DDL candidato.
