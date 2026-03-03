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
Si unificamos el backlog para que `rai backlog` sincronice estado bidireccionalmente con Jira y archivos locales, entonces Rai tendrá contexto preciso al inicio de cada sesión para el desarrollador, medido por cero correcciones manuales de estado stale en las primeras 4 semanas.
