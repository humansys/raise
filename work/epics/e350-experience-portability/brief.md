---
epic_id: "E350"
title: "Rai Experience Portability"
status: "in_progress"
created: "2026-03-04"
tracker: "RAISE-364"
---

# Epic Brief: Rai Experience Portability

## Hypothesis
For development teams who onboard new developers to RaiSE projects,
the experience portability system is a distribution mechanism
that ensures every developer gets the full Rai experience (identity, memory, patterns, skills, settings) from `rai init` alone.
Unlike the current state where artifacts are manually copied or missing, our solution makes the Rai experience reproducible and consistent across machines.

## Success Metrics
- **Leading:** New developer runs `rai init` and has working sessions with full context in < 5 minutes
- **Lagging:** Zero "missing context" or "stale memory" reports from F&F developers

## Appetite
M — 5 stories (already decomposed in Jira: RAISE-365 through RAISE-368 + RAISE-377)

## Scope Boundaries
### In (MUST)
- Inventory all artifacts that shape the Rai experience beyond skills
- Classify: universal (ships with rai) vs project-specific (rai init) vs personal (per-dev)
- `rai init` generates CLAUDE.md, hooks, settings from `.raise/` canonical source
- `.gitignore` sanitized for multi-developer parallel work
- MEMORY.md regenerated on `rai graph build`

### In (SHOULD)
- `rai skill sync` — detect stale skills after upgrade
- Documentation for new developer onboarding

### No-Gos
- IDE-specific configurations beyond Claude Code
- Migrating existing developer state between machines

### Rabbit Holes
- Over-engineering the distribution pipeline — `rai init` regeneration is sufficient
- Trying to sync personal calibration/sessions — those are explicitly per-developer
