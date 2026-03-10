---
epic_id: "E347"
jira_key: "RAISE-347"
shaped_by: "Emilio"
date: "2026-03-03"
domain: "Visibilidad / control"
---

# Problem Brief: Backlog Automation

## 1. Dominio
**Visibilidad / control** — el estado del trabajo no es confiable ni accesible.

## 2. Stakeholder Primario
**El desarrollador guiando a Rai en trabajo concurrente** (múltiples épicas, worktrees).

Stakeholder secundario: el equipo/organización que necesita visibilidad en Jira/Confluence para contribuir asincrónicamente.

## 3. Estado Actual (Gap)
El desarrollador guiando a Rai **no puede confiar en el estado del backlog, operar sin fricción, ni escalar visibilidad al equipo** porque el estado vive fragmentado entre Jira, archivos locales y CLAUDE.local.md.

## 4. Causa Raíz (3 Whys)
1. **¿Por qué fragmentado?** — Crecimiento orgánico: FileAdapter se creó primero, Jira se agregó después, nunca se unificaron.
2. **¿Por qué no se unificaron?** — La prioridad era features (memory, discovery, server), no infraestructura de backlog.
3. **¿Por qué ahora sí?** — La escala del trabajo (6+ épicas v2.2) y el crecimiento del equipo (Kurigage cliente activo) hacen insostenible la fragmentación.

**Raíz:** El backlog creció orgánicamente (file-first, Jira después) y la unificación se postergó por priorizar features. Ahora, con 6+ épicas en v2.2 y un equipo cliente activo, la fragmentación es insostenible.

## 5. Early Signal (4 semanas)
Al iniciar sesión, Rai sabe exactamente dónde estamos sin que el desarrollador corrija datos stale.

## 6. Hipótesis
Si hacemos que `rai backlog` sea el único path para leer y escribir estado de trabajo — transparente al consumidor, confiable siempre — entonces Rai tendrá contexto preciso al inicio de cada sesión, medido por cero correcciones manuales de estado stale en las primeras 4 semanas.

## 7. Decisiones de Diseño (del problem shaping)

| Decisión | Elección | Rationale |
|----------|----------|-----------|
| Offline mode (Jira down) | **Fail fast** | Zero divergence. Una fuente de verdad. No cache local. |
| backlog.md cuando hay Jira | **Mirror read-only** | Se regenera vía `rai backlog sync`, nunca se edita directo. |
| Skill → backlog | **Vía CLI (`rai backlog`)** | Un solo path, auditable, consistente. Skills no saben qué adapter hay. |
| Session-start → estado | **Query live vía `rai backlog`** | Estado real, no snapshot stale. Falla explícita si adapter no responde. |
| Adapter default | **Configurable en manifest.yaml** | Auto-detect si uno solo, default si configurado, `-a` para override. |

### Principio arquitectónico

**El adapter protocol es la abstracción.** Skills, hooks, session-start y humanos solo hablan con `rai backlog` CLI. No saben ni les importa si detrás hay Jira, FileAdapter, o cualquier otro backend. El contrato es: siempre responde o falla explícitamente.

```
Consumidor (skill/hook/session/humano)
        ↓
   rai backlog CLI
        ↓
   Adapter resolution (manifest.yaml default / auto-detect / -a flag)
        ↓
   ┌─────────────────┬──────────────────┐
   │ McpJiraAdapter   │ FilesystemAdapter │
   │ (Jira = verdad)  │ (backlog.md = verdad) │
   └─────────────────┴──────────────────┘
```

Con Jira: Jira es fuente de verdad, backlog.md es mirror read-only.
Sin Jira: backlog.md es fuente de verdad (open source default).
