# Retrospective: S-BRANCH-CONFIG

## Summary
- **Story:** S-BRANCH-CONFIG — Configurable development branch
- **Started:** 2026-02-11
- **Completed:** 2026-02-11
- **Size:** S
- **Commits:** 5 (scope + schema + skills + onboarding + manifest)

## What Went Well
- Caught product bug before first client used it
- Backward-compatible schema change
- Clean mechanical replacement — 30 references, zero breakage

## What Could Improve
- Should have been caught during E14 (distribution epic) — project-specific values need audit before distribution

## Heutagogical Checkpoint

### What did you learn?
- Internal dev conventions leak into distributed artifacts silently

### What would you change about the process?
- Add pre-publish audit for project-specific values in skills_base

### Are there improvements for the framework?
- Consider lint rule for hardcoded branch names in distributed skills

### What are you more capable of now?
- Skills now respect per-project branch config via manifest

## Patterns
- PAT-E-266: Distributed skills must be project-agnostic — audit for hardcoded project-specific values before publishing

## Action Items
- None
