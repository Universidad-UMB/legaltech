# Documentación de LegalTech

Este directorio centraliza la documentación extensa del proyecto. Los contratos ejecutables, fixtures, evidencias de gobierno y código permanecen en sus directorios de primer nivel para que las herramientas puedan consumirlos sin confundirlos con documentación narrativa.

## Lectura recomendada

1. [README principal](../README.md): propósito, capacidades y estado del producto.
2. [Entrega final](delivery/ENTREGA-FINAL.md): arquitectura implementada, ejecución y resultados registrados.
3. [Plan de desarrollo](development/plan/PLAN-DEV-001_v0.1.md): alcance de los incrementos.
4. [Tickets INC-00..07](development/tickets/): requisitos y gates por incremento.
5. [Estrategia de pruebas](testing/TEST-001_v0.1.md): cobertura y criterios de verificación.
6. [Guía REST](operations/DEMO-REST.md): recorrido reproducible de la demo sintética.

## Secciones

### Producto

[`product/`](product/) contiene la conciliación de especificaciones y la descripción del conjunto de datos del prototipo.

### Decisiones

[`decisions/`](decisions/) contiene las decisiones de la fase de implementación. Los ADR de arquitectura previos permanecen dentro de [`references/fase_2/ADR/`](references/fase_2/ADR/) para conservar el paquete histórico completo.

### Desarrollo

[`development/`](development/) reúne el plan, los ocho tickets y las matrices de trazabilidad entre requisitos, operaciones y pruebas.

### Pruebas

[`testing/`](testing/) contiene la estrategia y los manifiestos canónicos de aceptación, negativos HTTP y escenarios de datos. Los tests ejecutables están en [`backend/tests/`](../backend/tests/).

### Operación

[`operations/`](operations/) contiene la guía REST y la documentación del orquestador. La instalación y los comandos técnicos del servicio están en [`backend/README.md`](../backend/README.md).

### Entregas

[`delivery/`](delivery/) contiene el resumen final, la evidencia de INC-00 a INC-07 y el [registro de esta reorganización](delivery/REORGANIZACION-2026-11-11.md).

### Referencias

[`references/`](references/) conserva sin reorganización interna los materiales de las fases 0 a 4 y el análisis original. Su contenido puede describir rutas correspondientes al momento histórico en que fue producido.

### Archivo

[`archive/`](archive/) conserva el índice de la fase 6 y los manifiestos históricos de checksums. Esos manifiestos acreditan el contenido y las rutas de los paquetes originales; no se reescriben para simular que describen la estructura actual.

## Artefactos externos a `docs/`

- [`contratos/API-001.openapi.yaml`](../contratos/API-001.openapi.yaml): contrato HTTP canónico.
- [`fixtures/`](../fixtures/): datos sintéticos consumidos por la aplicación.
- [`governance/APROBACION-DEMO-001.json`](../governance/APROBACION-DEMO-001.json): evidencia de aprobación gestionada fuera del trabajo del agente.
- [`AGENT.md`](../AGENT.md) y [`AGENTS.md`](../AGENTS.md): reglas operativas visibles desde la raíz.
