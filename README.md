# LegalTech — vigilancia de procesos judiciales

LegalTech es un prototipo de backend para organizar el seguimiento de procesos judiciales, detectar cambios entre observaciones y controlar la revisión humana y la publicación de novedades para clientes. El proyecto busca que cada actuación tenga trazabilidad, separación entre clientes y una publicación explícitamente revisada antes de llegar al portal externo.

## Qué permite hacer

- Administrar clientes, procesos judiciales y seguimientos.
- Cargar adquisiciones exclusivamente desde fixtures sintéticos.
- Comparar observaciones e identificar actuaciones nuevas.
- Someter novedades a revisión operativa y jurídica humana.
- Preparar, aprobar y publicar versiones inmutables de una comunicación.
- Consultar publicaciones vigentes desde un portal externo aislado por cliente y alcance.
- Auditar transiciones relevantes sin exponer credenciales ni datos judiciales reales.

## Flujo funcional

1. Un equipo interno registra el cliente, el proceso y su seguimiento.
2. El prototipo incorpora una observación sintética y establece una línea base.
3. Las observaciones posteriores se comparan para detectar novedades elegibles.
4. Personas distintas realizan la revisión operativa, jurídica y de aprobación.
5. La versión aprobada se publica de forma atómica.
6. El cliente consulta únicamente la publicación vigente de los seguimientos autorizados.

## Estado del proyecto

Los incrementos INC-00 a INC-07 implementan un prototipo funcional con FastAPI y PostgreSQL. El contrato canónico contiene 35 operaciones HTTP y la trazabilidad contempla 18 escenarios de aceptación, 36 negativos HTTP y 39 escenarios de datos. La evidencia detallada se conserva en [la entrega final](docs/delivery/ENTREGA-FINAL.md) y en los [reportes por incremento](docs/delivery/increments/).

Este repositorio no es un producto jurídico en producción. No consulta fuentes judiciales reales, no utiliza LLM u OCR, no envía correos y no genera PDF. Todas las identidades, procesos, actuaciones y decisiones utilizadas por la demo son sintéticas.

## Organización

- [`backend/`](backend/README.md): servicio FastAPI, migraciones, pruebas y herramientas de ejecución local.
- [`docs/`](docs/README.md): documentación de producto, desarrollo, pruebas, operación, entregas y referencias históricas.
- [`contratos/`](contratos/API-001.openapi.yaml): contrato OpenAPI canónico.
- [`fixtures/`](fixtures/): datos sintéticos reproducibles utilizados por la demo.
- [`governance/`](governance/): evidencia versionada de decisiones y aprobaciones.
- [`orchestration/`](orchestration/): automatización y comprobaciones del flujo incremental.

## Arquitectura general

El backend es un monolito modular. El dominio se organiza por capacidades —identidad, clientes, seguimientos, adquisiciones, comparaciones, novedades, publicaciones y portal— y mantiene separadas las reglas de negocio, los casos de uso, la persistencia y la API HTTP. PostgreSQL almacena el estado transaccional y Alembic administra las migraciones.

## Ejecución local

El entorno local utiliza Python 3.12 o 3.13, `uv` y Docker Compose. Los servicios Docker usan el proyecto aislado `legaltech-backend`, PostgreSQL se publica en `127.0.0.1:55432` y la API en `127.0.0.1:8001`.

La instalación, migración, carga de datos y validación están descritas en el [README técnico del backend](backend/README.md). El recorrido funcional de la API está en la [guía REST de la demo](docs/operations/DEMO-REST.md).

## Documentación

El punto de entrada es el [índice documental](docs/README.md). Allí se distingue la documentación vigente de las referencias históricas, las especificaciones de prueba y los artefactos ejecutables que permanecen fuera de `docs/`.
