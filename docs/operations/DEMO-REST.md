# Guía REST de demostración

Esta guía ejecuta el flujo con las cuentas y datos sintéticos del fixture. El backend no consulta fuentes judiciales ni envía correo, genera PDF o procesa texto con LLM/OCR.

## Preparar el entorno

Desde PowerShell en `backend/`:

```powershell
uv sync --frozen
docker compose --project-name legaltech-backend up -d db
docker compose --project-name legaltech-backend --profile tools run --rm migrate
docker compose --project-name legaltech-backend up -d --build api
uv run python -m scripts.bootstrap_demo
```

El bootstrap solicita la contraseña sintética sin mostrarla. Se usa para las ocho cuentas de demostración. No guardes contraseñas ni tokens en el repositorio ni en capturas/logs. La API local está en `http://127.0.0.1:8001`; `/docs` muestra el contrato runtime.

## Crear el contexto de vigilancia

Autentica `admin.demo` mediante `POST /api/v1/auth/sessions` y conserva el `access_token` solo en la sesión local del cliente HTTP:

```json
{
  "username": "admin.demo",
  "password": "<contraseña sintética ingresada localmente>"
}
```

Con el bearer token, crea el proceso ficticio y los seguimientos por API:

```http
POST /api/v1/internal/processes
Authorization: Bearer <token-local>
Content-Type: application/json

{"radicado":"00000000000000000000001","label":"Proceso ficticio 1"}
```

```http
POST /api/v1/internal/trackings
Authorization: Bearer <token-local>
Content-Type: application/json

{"client_id":"<UUID de Alfa>","process_id":"<UUID de PROC-001>"}
```

Crea también el seguimiento Beta para el mismo proceso y el seguimiento `SEG-A-002` para `PROC-002`; activa los tres con `POST /api/v1/internal/trackings/{tracking_id}/activate`. Los UUID se obtienen de las respuestas. Después agrega asignaciones internas y ámbitos externos que correspondan:

```powershell
uv run python -m scripts.seed_authorization_context
```

Este comando solo agrega asignaciones/ámbitos faltantes y requiere que los códigos de seguimiento coincidan con el fixture.

## Adquirir, comparar y evaluar

Autentica `analyst.demo`. Para cada adquisición usa una `request_key` nueva de al menos ocho caracteres:

```http
POST /api/v1/internal/acquisition-runs
Authorization: Bearer <token-local>
Content-Type: application/json

{"process_id":"<UUID de PROC-001>","fixture_code":"OBS_001","request_key":"demo-obs001-01"}
```

Guarda el `observation_id` de OBS-001, adóptalo como baseline de `SEG-A-001` y repite la adquisición con `fixture_code` `OBS_002`. Compara el par y evalúa en el seguimiento antes de adoptar la nueva observación:

```http
POST /api/v1/internal/comparisons
Authorization: Bearer <token-local>
Content-Type: application/json

{"old_observation_id":"<UUID OBS-001>","new_observation_id":"<UUID OBS-002>","rule_version":"demo-v1"}
```

```http
POST /api/v1/internal/trackings/{tracking_id}/evaluations
Authorization: Bearer <token-local>
Content-Type: application/json

{"comparison_id":"<UUID de comparación>"}
```

El resultado sintético incorpora solo `ACT-06` como `ADDED` y produce `NOV-A-001` para Alfa. Adoptar OBS-002 como primera baseline de Beta no genera novedades retrospectivas. Un intento de adelantar el cursor de Alfa antes de evaluar responde `409` y conserva la baseline.

## Revisión humana y publicación

`analyst.demo` inicia y escala la revisión operativa con `POST /api/v1/internal/novelties/{novelty_id}/start-operative-review` y `/escalate`. `lawyer.demo` registra la valoración humana con `/legal-review`. Los cuerpos de escalación y valoración incluyen texto sintético para `decision` y `evidence_note`.

`preparer.demo` crea una publicación textual con `POST /api/v1/internal/publications`, la somete mediante `/api/v1/internal/publication-versions/{version_id}/submit`, y una cuenta coordinadora de otra persona la aprueba con `/decision`. `preparer.alt.demo` comparte la identidad humana del preparador y recibe `403`. Después del visto bueno, `/publish` fija el puntero vigente en la misma transacción.

Consulta `GET /api/v1/portal/trackings/{tracking_id}/current-publication` con `reader.alfa.demo`. Alfa puede leer su publicación; Beta y la cuenta Alfa sin ámbito sobre `SEG-A-002` reciben el mismo `404` genérico. Un seguimiento autorizado sin publicación recibe `200` con `available=false`. Las adquisiciones fallidas/incompletas informan cobertura y no significan `NO_CHANGES`.

## Verificación reproducible

La suite repite el flujo completo, confirma las 18 etapas de aceptación, ejercita 36 negativos HTTP y las restricciones de PostgreSQL, verifica la persistencia al recrear la aplicación, y compara las rutas/esquemas runtime con el OpenAPI canónico. Ejecuta:

```powershell
.\scripts\ci.ps1
```

El reporte con comandos, resultados y límites está en [`delivery/increments/INC-07.md`](../delivery/increments/INC-07.md).
