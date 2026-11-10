# ADR-002 — Organización por funcionalidad y dependencias dirigidas

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** DOMAIN-001 §3/4/5; DOM-R01..24.

## Contexto
La lógica de línea base y los cambios comunes deben separarse de novedades/publicaciones privadas de cada cliente. El framework, ORM y las rutas no deben convertirse en autoridad de negocio.

## Decisión candidata
Package-by-feature: `identity`, `clients`, `tracking`, `observations`, `comparison`, `novelties`, `publications`, `portal`, `audit`. Dentro de cada módulo, `api → application → domain` y dependencias hacia interfaces propias; `infrastructure` implementa puertos. `bootstrap` compone servicios. DTO HTTP Pydantic no atraviesa hacia entidades de dominio y ORM no se devuelve a clientes.

## Contratos transversales
- `Principal` = identidad autenticada; `personaId` para segregación.
- `AuthorizedTrackingRef` / comprobación contextual de seguimiento y tenant antes de lecturas externas.
- `ComparableObservation` = referencia de observación validada y comparable.
- `ChangeDetected` no determina el juicio jurídico ni publicación.
- `ReviewedNovelty` es condición para producir versión autorizable.
- `PublicationReadModel` solo se construye tras validar acceso, vigencia y estado.

Los nombres son conceptos orientadores, **no APIs Python ya acordadas**. Evitar patrones genéricos y pasarelas sin caso de uso real.

## Alternativas
Agrupar por capas globales (`routers/`, `services/`, `models/`) dificulta ownership al crecer; modelar cada contexto como proyecto independiente sobredimensiona. Se prefiere módulo cohesivo en un paquete único.

## Consecuencias y pruebas
Chequeos automáticos impiden que `domain` importe FastAPI/SQLAlchemy o que `api` importe ORM; las revisiones verifican que ningún módulo actualiza agregados ajenos. La composición de portal integra consultas sin adoptar propiedad de estados de otros módulos.
