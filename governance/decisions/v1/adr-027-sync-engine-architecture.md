---
id: "ADR-027"
title: "Sync Engine Architecture - Local-First Hub-and-Spoke"
date: "2026-02-14"
status: "Accepted"
epic: "E-DEMO"
---

# ADR-027: Sync Engine Architecture - Local-First Hub-and-Spoke

## Contexto

Backlog sync entre RaiSE (local governance/backlog.md + memory graph) y JIRA requiere una arquitectura de sincronización. Opciones:

1. **Peer-to-peer:** JIRA ↔ RaiSE bidireccional directo
2. **Hub-and-spoke:** Memory graph como hub central, JIRA como spoke
3. **Event sourcing:** Todos los cambios como eventos append-only
4. **CRDT:** Conflict-free replicated data types

Tensiones:
- **Simplicity:** Hub-and-spoke es más simple que peer-to-peer o CRDT
- **Source of truth:** Local debe ser autoritativo para Rai (queries rápidos, token-efficient)
- **Team collaboration:** JIRA debe ser autoritativo para equipo
- **Conflict resolution:** Necesario para bidirectional (deferred to V3)

**Research foundation:** 184+ sources across 6 research outputs

## Decisión

**Implement local-first, hub-and-spoke architecture with field-level ownership for MVP (one-way sync). Defer bidirectional sync and conflict resolution to V3/raise-pro.**

**Architecture:**
```
governance/backlog.md + memory graph (SQLite)
(Local — Rai's source of truth, always queryable, token-efficient)
               ↓
         Sync Strategy
      (One-way: Local → JIRA)
               ↓
         JIRA Cloud
(Team's source of truth, collaboration surface)
```

**MVP Scope (E-DEMO):**
- **Full granularity sync:** Epic + Story + Task levels
- Local writes immediately to backlog.md + memory graph
- Manual sync command: `rai backlog sync --provider jira --direction push`
- Idempotent operations (safe to re-run sync)
- Entity properties track sync state (last_sync_at, rai_epic_id, rai_story_id, rai_task_id)
- Task extraction from `plan.md` → JIRA subtasks

**JIRA Hierarchy:**
```
JIRA Epic (E-DEMO)
  └── JIRA Story (S-DEMO.1)
        └── JIRA Subtask (T-DEMO.1.1)
        └── JIRA Subtask (T-DEMO.1.2)
        └── JIRA Subtask (T-DEMO.1.3)
```

**Deferred to V3:**
- Bidirectional sync (JIRA → Local pull)
- Conflict resolution (three-way merge, field-level precedence)
- Webhooks (real-time sync triggers)
- Polling reconciliation (periodic drift detection)

## Field-Level Ownership (V3 Design, Document Now)

When implementing bidirectional sync in V3:

| Field | Owner | Strategy | Rationale |
|-------|-------|----------|-----------|
| `title`, `description` | Both | Three-way merge (Git algorithm) | Collaborative editing |
| `assignee`, `external_status`, `priority` | Team | LWW (external wins) | Team owns collaboration |
| `current_story`, `progress`, `workflow_state` | Rai | LWW (Rai wins) | Rai owns internal workflow |
| `tasks`, `learnings`, `session_context` | Rai | No sync (local only) | Internal to Rai |
| `comments`, `attachments` | Both | Append-only | Never conflict |

## Forge Vision (V3 Intelligence Infrastructure)

**Strategic Context:** This MVP is designed as the foundation for **Rai in Forge** — hosted intelligence that aggregates data across projects/teams.

**Architecture Evolution:**
```
MVP (E-DEMO):
  Local Dev (RaiSE CLI) → JIRA (one-way)

V3 (Forge):
  Local Devs (RaiSE CLI) ↔ JIRA ↔ Remote Devs (JIRA only)
                          ↕️
                    Rai in Forge
              (Cross-project intelligence)
```

**Forge Capabilities (Future):**
1. **Cross-project pattern recognition:** "OAuth tasks slip 2x across 3 projects"
2. **Systemic insights:** "Teams syncing tasks to JIRA have 25% better estimation"
3. **Reuse recommendations:** "E-DEMO architecture similar to E-AUTH (raise-gtm)"
4. **Blocker detection:** "5 teams blocked on same dependency"
5. **Team health metrics:** "Project X has WIP too high (5 epics in implement)"

**Why Design for Forge Now:**
- Internal IDs (E-DEMO) are stable across projects → pattern recognition works
- Full granularity (epic/story/task) → Forge has execution-level visibility
- Bidirectional schema ready → remote devs can update JIRA, Rai stays in sync
- Entity properties → metadata travels with JIRA items across tools

**Design Decisions Informed by Forge:**
- Stable internal IDs (not JIRA-dependent)
- Full task granularity (execution patterns need this)
- Normalized schema (cross-project aggregation requires it)
- JSON output mode (Forge consumes structured data)

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Local queries are fast and token-efficient (no API calls during session-start) |
| ✅ Positivo | MVP is simple (one-way sync, no conflict resolution needed) |
| ✅ Positivo | Clear ownership (local is Rai's truth, JIRA is team's truth) |
| ✅ Positivo | Research-backed (converging evidence from 6 research streams, 184+ sources) |
| ✅ Positivo | Extensible (field-level ownership defined, ready for V3) |
| ⚠️ Negativo | Manual sync required (no real-time updates) — mitigated by lifecycle events in V3 |
| ⚠️ Negativo | One-way only (JIRA changes don't flow back) — acceptable for demo, fixed in V3 |
| ⚠️ Negativo | Sync state complexity (entity properties tracking) — well-documented in research |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| **Peer-to-peer (JIRA ↔ RaiSE direct)** | No central hub = complex multi-backend support. Doesn't scale to GitLab/Odoo. |
| **CRDTs (Conflict-free Replicated Data Types)** | Overkill for coarse-grained backlog entities. Production abandonment cases (Cinapse, Figma). HIGH research evidence against (3 sources). |
| **Event sourcing** | Adds complexity without benefit for backlog sync. Better for audit trails (not our primary need). |
| **JIRA as source of truth** | Breaks local-first principle. Rai would need API calls during session-start (slow, token-expensive). |

---

<details>
<summary><strong>Referencias</strong></summary>

**Research outputs:**
- `/work/research/bidirectional-sync/recommendation.md` - Local-first, hub-and-spoke, three-way merge, field-level ownership (HIGH confidence, 28 sources)
- `/work/research/offline-first-sync/recommendation.md` - Local-first delta sync, sequence IDs, exponential backoff (HIGH confidence, 32 sources)
- `/work/research/pm-sync-boundaries/recommendation.md` - Active items only, epic + story levels (HIGH confidence, 34 sources)

**Key sources:**
- [Martin Fowler: Distributed Systems Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/) (Very High)
- [Why Cinapse Moved Away From CRDTs](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync) (High)
- [The Hard Things About Sync - Joy Gao](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync) (High)

**Implementation:**
- Sync state storage: `.raise/rai/sync-state.jsonl` (JSONL for append-only history)
- Entity properties: JIRA Cloud API entity properties (32KB JSON storage, JQL-queryable)
- Idempotency: Check entity properties before creating (skip if `rai_epic_id` already exists)

</details>
