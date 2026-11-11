# Reorganización documental — 2026-11-11

## Propósito

Centralizar la documentación extensa del repositorio sin cambiar el comportamiento, la arquitectura interna ni el nombre del directorio `backend/`.

## Cambios

- Se creó `docs/README.md` como índice documental.
- Se reescribió el README raíz con una presentación funcional del producto.
- Tickets, trazabilidad, especificaciones de prueba y referencias históricas se trasladaron bajo `docs/`.
- La guía REST y los reportes de incrementos salieron de `backend/`; el código, las migraciones, los tests y las herramientas internas conservaron su organización.
- La documentación del orquestador se trasladó a `docs/operations/orchestration/`; sus scripts y tests permanecieron en `orchestration/`.
- Los manifiestos de checksums se conservaron sin modificar en `docs/archive/checksums/` como evidencia de los paquetes originales.
- Se actualizaron validadores, pruebas y enlaces que consumían las rutas anteriores.

## Artefactos no modificados

- `governance/APROBACION-DEMO-001.json`
- `.autopilot/state.json`
- `contratos/API-001.openapi.yaml`
- `fixtures/`
- `backend/app/`
- `backend/migrations/`

## Verificación

| Verificación | Resultado |
|---|---|
| Validador documental | PASS: 35 operaciones, 18 AT, 36 negativos HTTP, 39 datos, 14 RNF y 8 tickets |
| Tests del orquestador | PASS: 10 pruebas |
| Ruff y formato del backend | PASS |
| Mypy | PASS: 75 archivos |
| Pytest del backend | PASS: 67 pruebas |
| OpenAPI runtime | PASS: 35 operaciones coincidentes |
| Docker Compose | PASS: configuración válida del proyecto aislado `legaltech-backend` |
| Integridad de movimientos | PASS: referencias, tickets, trazabilidad, manifiestos y checksums conservan contenido exacto |
| Enlaces Markdown locales | PASS |

No se realizó commit, push, merge, despliegue ni limpieza de contenedores o volúmenes.
