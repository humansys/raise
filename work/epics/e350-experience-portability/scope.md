---
epic_id: "E350"
tracker: "RAISE-364"
status: "in_progress"
release: "2.2.0a1"
adr: "ADR-044"
---

# E350: Rai Experience Portability — Scope

## Objective
Make the Rai experience fully reproducible: any developer runs `git clone` + `rai init` + `rai graph build` and gets an instance of Rai with the same behavior, context, and capabilities as the original.

## Value
Unblocks parallel development (sprint 4+). Eliminates dependency on Emilio's machine as Rai's "source of truth."

## In Scope (MUST)
- Artifact inventory and classification (base/project/personal)
- Three-level pattern model: base (package) + project (git) + personal (per-dev)
- Destill 727 patterns into ~50 base first-principles
- MEMORY.md regeneration on `rai graph build` (hook)
- CLAUDE.md always generated from `.raise/` sources, never hand-edited
- Sanitize `.gitignore` for multi-developer parallel work
- Enhanced `rai init` (idempotent: first-time + update)
- Jira credentials separated from project config

## In Scope (SHOULD)
- `rai skill sync` — detect stale skills after upgrade
- `rai pattern promote` — explicit promotion from personal to project
- Diff preview in `rai init` before destructive changes

## Out of Scope
- IDE plugins beyond Claude Code → deferred to RAISE-128
- Cross-machine state migration → no use case yet
- Personal calibration sharing → explicitly per-developer
- `rai upgrade` as separate command → `rai init` is idempotent (ADR-044 D4)
- `rai sync` command → hooks handle it (ADR-044 D1)
- Organization-level config layer → premature (ADR-044)

## Stories

### Critical Path (Sprint 4 blocker)
| ID | Tracker | Summary | Size | Depends |
|----|---------|---------|------|---------|
| S350.1 | RAISE-365 | Inventory & classify artifacts — audit what constitutes the Rai experience | S | — |
| S350.2 | RAISE-455 | Sanitize git state — .gitignore, clean tracking, rai init adds personal/ | S | S350.1 |
| S350.3 | RAISE-454 | MEMORY.md + CLAUDE.md regeneration — hooks + derived artifacts | M | S350.1 |

### Post-Critical
| ID | Tracker | Summary | Size | Depends |
|----|---------|---------|------|---------|
| S350.4 | RAISE-366 | Pattern destillation & 3-level model — base/project/personal | L | S350.1 |
| S350.5 | RAISE-368 | Enhanced rai init — idempotent, regenerate all derived artifacts | M | S350.3, S350.4 |
| S350.6 | RAISE-377 | rai skill sync — detect stale skills post-upgrade | S | S350.5 |
| S350.7 | RAISE-223 | Jira credentials separation — per-dev vs per-repo | S | S350.2 |

## Done Criteria
- [ ] New developer runs `git clone` + `rai init` + `rai graph build` → full Rai experience
- [ ] `rai graph build` regenerates MEMORY.md automatically
- [ ] `rai init` regenerates CLAUDE.md from `.raise/` sources
- [ ] Patterns in 3 levels (base + project + personal), base destilled
- [ ] `.gitignore` prevents personal state from leaking
- [ ] Zero merge conflicts on patterns during parallel work

## Risks
| Risk | L | I | Mitigation |
|------|---|---|------------|
| Pattern destillation takes longer than estimated | M | M | Timebox 3h, archive when in doubt |
| Generated CLAUDE.md loses valuable info from current | L | H | Diff before overwrite, backup |
| Hook side-effects in graph build | L | M | Tests, isolated hook module |

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-03-04

### Strategy
**Dependency-driven + quick wins.** S350.1 (inventory) unlocks everything — it's the foundation. After that, three streams can run in parallel. Quick wins first (git sanitize) to unblock Gustavo immediately.

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S350.1: Inventory & classify | S | None | M1 | Foundation — every other story needs the classification |
| 2 | S350.2: Sanitize git state | S | S350.1 | M1 | Quick win — unblocks multi-dev immediately |
| 3‖ | S350.3: MEMORY.md + CLAUDE.md regen | M | S350.1 | M2 | Parallel with S350.2 — fixes the reported bug |
| 3‖ | S350.4: Pattern destillation | L | S350.1 | M3 | Parallel with S350.2/3 — longest story, start early |
| 4 | S350.7: Jira credentials separation | S | S350.2 | M2 | Quick win after git sanitize — independent stream |
| 5 | S350.5: Enhanced rai init | M | S350.3, S350.4 | M4 | Merge point — integrates regeneration + patterns |
| 6 | S350.6: rai skill sync | S | S350.5 | M4 | Capstone — last piece of idempotent init |

### Parallel Work Streams

```
Time →

Stream A (Git):    S350.1 ──► S350.2 ──► S350.7
                      │
Stream B (Context):   ├────► S350.3 ──────────┐
                      │                        ├──► S350.5 ──► S350.6
Stream C (Patterns):  └────► S350.4 ──────────┘

M1: Git-safe        M2: Context alive    M3: Patterns    M4: Full portability
(S350.1+2)          (+S350.3+7)          (+S350.4)       (+S350.5+6)
```

**Merge point:** S350.5 (Enhanced init) cannot start until both S350.3 and S350.4 complete. This is the integration story that wires everything together.

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|-----------------|
| **M1: Git-safe** | S350.1, S350.2 | New dev clones repo without receiving personal artifacts. `.gitignore` clean. Inventory documented. |
| **M2: Context alive** | +S350.3, S350.7 | `rai graph build` regenerates MEMORY.md. `rai init` regenerates CLAUDE.md. Jira creds separated. |
| **M3: Patterns portable** | +S350.4 | Base patterns ship with package. `rai pattern add` → personal. `rai pattern promote` → project. 727 patterns classified. |
| **M4: Full portability** | +S350.5, S350.6 | `git clone` + `rai init` + `rai graph build` = full Rai experience. Skill sync detects drift. All done criteria met. |

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S350.1 Inventory | S | Done | S | Merged 3326fdac |
| S350.2 Git sanitize | S | Done | S | Merged c69a9315 |
| S350.3 Regeneration | M | Done | M | Merged 217a42f9 |
| S350.4 Patterns | L | Done | M | Merged 8221619f |
| S350.5 Enhanced init | M | Pending | — | |
| S350.6 Skill sync | S | Pending | — | |
| S350.7 Jira creds | S | Pending | — | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| S350.4 (patterns, L) delays merge point for S350.5 | M/H | Start early in parallel; timebox destillation |
| S350.3 and S350.4 touch overlapping code (memory/patterns) | L/M | Different modules; review merge conflicts at S350.5 |
| Jira stories need updating to match new breakdown | L/L | Update in bulk before starting S350.1 |
