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
