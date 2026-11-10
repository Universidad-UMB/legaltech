# ADR-006 — Versionado inmutable y publicación local atómica

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** DOM-R13..19/23; D1-07/08/09/10; AT-08..14/18.

## Contexto
La interpretación del prototipo debe revisarla un abogado (salvaguarda PR-F1), y toda versión debe ser aprobada por una persona diferente de sus preparadores (PR-F1, DEC-09 aún no ratificada). Autorizar no equivale a hacer disponible.

## Decisión candidata
`Publication` agrupa versiones; cada versión lleva snapshot exacto de contenido, ámbito y destinatario, colección de preparadores por `personaId` y estado. Al someter, el snapshot queda congelado; modificar contenido exige nueva versión y autorización. Aprobación valida rol, tratamiento, versión y personas, y se guarda con evidencia. Operación de publicación local cambia esa versión `Autorizada → Publicada` **y** actualiza el puntero de versión vigente en una sola transacción. Lectura externa recupera exclusivamente la vigente y revalida identidad/ámbito/estado del cliente y seguimiento.

## Alternativas
Marcar un booleano `publicada` mutable en documento actual permitiría editar contenido aprobado; publicar mediante una segunda petición HTTP interna rompería atomicidad. Eventos asíncronos/outbox serían necesarios solo con entrega externa futura confirmable; no ahora.

## Consecuencias
Fallo entre estado y puntero hace rollback total, sin visibilidad externa. Seguimiento finalizado o cliente suspendido dejan versión publicada internamente pero la ocultan de acceso externo. PDF final, firma, informe mixto y notificaciones reales están fuera del incremento. Fase 3 determina esquema de versiones/puntero; Fase 4 define endpoints/errores.
