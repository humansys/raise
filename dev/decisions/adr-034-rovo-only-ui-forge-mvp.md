---
id: "ADR-034"
title: "Rovo-Only UI for Forge MVP"
date: "2026-03-27"
status: "Proposed"
---

# ADR-034: Rovo-Only UI for Forge MVP

## Contexto

El Forge app MVP tiene deadline de 3 semanas (Apr 16, 2026). Hay 3 opciones de
UI: Custom UI (React en iframe), UI Kit 2 (componentes nativos Atlassian), o
Rovo agents como única interfaz (chat conversacional). El equipo tiene experiencia
limitada en Forge UI y máxima urgencia de entrega.

## Decisión

Usar Rovo agents como la única UI del MVP. No Custom UI, no UI Kit panels.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Zero código de UI — se elimina ~40% del trabajo estimado |
| ✅ Positivo | UX nativa — usuarios ya conocen Rovo chat en Jira/Confluence |
| ✅ Positivo | El "aha moment" es conversacional por naturaleza |
| ⚠️ Negativo | No hay dashboards visuales ni tablas de datos en MVP |
| ⚠️ Negativo | Interacción limitada a patrones conversacionales |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Custom UI (React iframe) | Demasiado código para 3 semanas. Overhead de iframe. |
| UI Kit 2 (native) | Más rápido que Custom UI pero requiere componentes React. |
| Híbrido (Rovo + issue panel) | Aumenta scope sin valor claro para el demo. |

---

<details>
<summary><strong>Referencias</strong></summary>

- R4-RAISE-760: Forge Platform Deep-Dive, Sección 3
- R3-RAISE-760: MVP Value Slice — "aha moment" es conversacional

</details>
