# Entrega — Fase 1: Modelado de dominio del backend LegalTech

**Versión:** 0.1-candidata  
**Fecha de corte:** 2026-11-10  
**Estado:** especificación propuesta; no equivale a autorización para implementar todo V1 ni a aprobación externa.

## Inventario

| Archivo | Uso |
|---|---|
| `DOMAIN-001_v0.1.md` | Lenguaje ubicuo, contextos, agregados conceptuales, reglas DOM-R01..R24, casos, límites y criterios de salida |
| `DOM-ME-001_v0.1.md` | Transiciones y guardas de cliente, seguimiento, adquisición, novedad, publicación y autorización básica |
| `DEC-F1-001_v0.1.md` | Registro de propuestas/políticas y bloqueos reales para fases 2–4 |
| `DOM-TRZ-001_v0.1.csv` | Trazabilidad 18 criterios PROTO-AT a reglas/contextos/UC y evidencia futura |
| `diagramas/DOM-ME-*.mmd` | Diagramas Mermaid de estados del alcance demostrativo |
| `diagramas/DOM-CONTEXTOS.mmd` | Mapa conceptual de dependencias |

## Orden recomendado de lectura

1. `SCOPE-001_v0.1.md` de Fase 0 (no incluido por duplicado).
2. `DOMAIN-001_v0.1.md` §§1–6 y 8–10.
3. `DOM-ME-001_v0.1.md` (subconjuntos, guardas y exclusiones).
4. `DOM-TRZ-001_v0.1.csv` para comprobar cobertura y expectativas de pruebas.
5. `DEC-F1-001_v0.1.md` para resolver bloqueos antes de implementaciones autónomas.

## Origen y precedencia

Fuentes originales del usuario: `HANDOFF_Arquitectura_Backend_LegalTech_v0.1(1).zip` con RF-CAT-001 v0.8, RF-DEC-001 v0.4, PROTO-001 v0.1 y TOBE-001 v0.2 + BPMN-01..04; y `FASE_0_LegalTech_Backend_v0.1.zip`. Si alguna regla contradice fuente, **registrar conflicto y resolverlo explícitamente** antes de cambiar fuente original. El modelo v0.1 es un refinamiento propuesto, no documentación aprobada.

## Calidad y resultado

- Lenguaje ubicuo consistente: proceso ≠ seguimiento ≠ observación ≠ cambio ≠ novedad ≠ publicación.
- Ámbitos y pertenencia al cliente definidos en reglas explícitas, no asumidos por UI.
- Comparación determinística y línea base por seguimiento.
- Separación de revisiones, artefacto exacto y autorización por persona.
- Condiciones de fallo y transacciones conceptuales documentadas.
- Matriz de 18 AT (planificados, **no ejecutados**).

**Dictamen:** Fase 1 documentada en modalidad *candidata*, suficiente como insumo para comenzar **Fase 2 (evaluación arquitectónica y ADR)**. Aún no delegar implementación integral al agente sin aceptación del dominio y los artefactos de arquitectura, datos, API, seguridad y pruebas.
