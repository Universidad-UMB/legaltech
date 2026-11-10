# ADR-004 — Identidad local de prueba y autorización contextual

- **Estado:** Propuesto para aprobación de autores
- **Fecha:** 2026-11-10
- **Impulsores:** DEC-01/03/04 (seleccionadas por autores, no ratificadas); DOM-R01..05/16/19; AT-10/12/13/14/17.

## Contexto
Un selector de rol frontend no garantiza identidad. Personas diferentes pueden compartir el rol o tener varias cuentas. Un proceso judicial común no autoriza ver tratamientos de otro cliente.

## Decisión candidata
Para el prototipo **local**: contraseñas sintéticas almacenadas con hash Argon2id, login que crea token bearer opaco aleatorio; DB conserva solo digest del token, cuenta, expiración y estado de revocación. Cada solicitud protegida resuelve cuenta y permisos vigentes en servidor, sin confiar en tenant/rol recibido en HTTP. Autorización de recurso verifica rol, tenant, seguimiento, ámbito, estados cliente/seguimiento y publicación vigente según operación. Segregación por `personaId`, no por alias ni `accountId`.

## Alternativas
JWT auto-contenido con claims estáticos puede dejar permisos obsoletos si no se consulta DB igualmente; IdP externo/OIDC requiere configuración y dependencia no necesaria para demo; credenciales fijas o roles seleccionables por navegador se rechazan. Un IdP se reconsiderará para V1.

## Consecuencias y límites
Se requiere tabla de sesión o equivalente en DATA-001; caducidad/revocación y login en API-001. No guardar token en logs ni definir política insegura de almacenamiento navegador; definir cookies, CSRF y CORS si se integra SPA. No usar datos judiciales reales, no declarar listo para Internet. Tests de BOLA, control por propiedad, uso de sesión expirada y suspensión posterior a emisión.

Fuente: https://owasp.org/projects/api-security-project/
