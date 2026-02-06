# F14.13: Framework Ontology Cleanup

> Pre-distribution cleanup of terminology inconsistencies.

## Context

Before distributing Rai to F&F users, we need consistent terminology across active documentation. Scan revealed:

- CLAUDE.md contradicts glossary on kata levels
- 35 files reference old `graph` commands (now `memory`)
- 114 files use deprecated kata level names
- 61 files use deprecated SAR/CTX terminology

## Scope

### In Scope

**Fix terminology in active docs only:**

1. **Core Docs**
   - CLAUDE.md — Fix terminology section, update architecture paths
   - README.md — Verify terminology
   - CONTRIBUTING.md — Verify terminology

2. **Framework Reference**
   - framework/reference/glossary.md — Source of truth (verify self-consistency)
   - framework/reference/constitution.md
   - framework/reference/work-cycles.md
   - framework/vision.md

3. **Governance**
   - governance/solution/vision.md
   - governance/solution/guardrails.md
   - governance/projects/raise-cli/prd.md
   - governance/projects/raise-cli/vision.md
   - governance/projects/raise-cli/design.md
   - governance/projects/raise-cli/backlog.md

4. **Dev Docs**
   - dev/components.md
   - dev/architecture-overview.md
   - dev/parking-lot.md

5. **Rai Identity**
   - .raise/rai/identity/core.md
   - .raise/rai/identity/perspective.md
   - .claude/RAI.md

### Out of Scope

**Historical artifacts (document history, don't rewrite):**
- dev/sessions/* — Session logs
- dev/decisions/v1/* — Superseded ADRs
- dev/decisions/v2/* — Keep as-is (decisions were valid at time)
- work/research/* — Completed research
- work/analysis/* — Completed analysis
- work/proposals/* — Old proposals

### Archive Candidates

**Move to `archive/` directory:**

| Current Location | Reason |
|------------------|--------|
| dev/sessions/* | Historical session logs, not active |
| dev/agents/v0/* | Old agent prompts, not in use |
| dev/meta/* | Old kata schemas with deprecated terms |
| work/tracking/session-log.md | Replaced by `.raise/rai/memory/sessions/` |
| work/tracking/ontology-backlog.md | Stale, most items resolved |
| work/tracking/issues-decisions.md | Stale tracking |
| work/tracking/dependencies-blockers.md | Stale tracking |
| work/proposals/* | Old roadmaps, superseded |

## Terminology Fixes Required

### Critical (CLAUDE.md vs Glossary conflict)

| Current (CLAUDE.md) | Should Be | Source |
|---------------------|-----------|--------|
| "Kata levels L0-L3 → Principio/Flujo/Patrón/Técnica" | Remove — both deprecated | Glossary v2.3 |

### graph → memory

| Current | Should Be |
|---------|-----------|
| `raise graph build` | `raise memory build` |
| `raise graph query` | `raise memory query` |
| `governance/graph/` | `governance/memory/` (in architecture) |

### Role Consistency

Keep both "Orchestrator" and "RaiSE Engineer" — both are valid per glossary.

## Done Criteria

- [x] CLAUDE.md terminology section matches glossary
- [x] CLAUDE.md architecture paths match actual code structure
- [x] No `graph build/query` references in active docs (README, vision.md, guardrails-stack.md)
- [x] Archive directory created with historical artifacts (88 files)
- [x] Active docs use consistent terminology

## Size

**XS** — ~15 files to update, ~10 to archive

## Dependencies

None — standalone cleanup.
