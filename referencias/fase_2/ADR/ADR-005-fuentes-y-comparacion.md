# ADR-005 — Adaptador de observaciones sintéticas, comparación determinista

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** G03/G04; DOM-R06..12/24; D1-02/03/16; AT-03/04/05/06/15.

## Contexto
No está verificada autorización técnica/jurídica de fuentes judiciales reales ni equivalencia de identidades de actuaciones entre fuentes. El prototipo exige cambios repetibles ACT-06 y brechas de cobertura explícitas.

## Decisión candidata
El puerto pequeño `ObservationSource` se implementa únicamente por `DemoFixtureObservationSource`, sin llamadas de red. La salida tipada incluye `estado` (exitosa completa, incompleta, fallida), `source_id`, `observed_at`, `received_at`, versión de identidad y actuaciones sintéticas cuando proceda. La comparación determinista solo usa dos snapshots completos, comparables y ordenados del mismo proceso; calcula incorporaciones por diferencia de claves, conserva procedencia y no crea novedades jurídicas. `tracking` determina baseline/elegibilidad por seguimiento; `novelties` genera tratamiento privado de A.

## Alternativas
Scraping real de inmediato: descartado hasta evidencia de autorización y viabilidad. LLM para comparación básica: innecesario y no determinista. Comparar observaciones parciales como listas vacías: rechazado por riesgo de falso «sin cambios».

## Consecuencias
Test con `OBS-001` (ACT01..05), `OBS-002` (ACT01..06), fallida e incompleta. B inicia en OBS-002 sin novedad histórica. La política de deduplicación entre pares sucesivos y la identidad real de actuaciones quedan fuera del fixture y necesitan nuevo análisis V1.
