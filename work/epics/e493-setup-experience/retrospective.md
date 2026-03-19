# E493 Retrospective — Developer Setup Experience

**Date:** 2026-03-06
**Stories:** 5 completed, 1 moved to RAISE-501

## Metrics

| Story | Size | Time | Velocity | Notes |
|-------|------|------|----------|-------|
| S5 — CLI `.env` loading | S | 12 min | 1.67x | Clean TDD |
| S6 — Pipx install fix | S | 10 min | — | Investigation only, already working |
| S1 — Installation guide | S | 15 min | 2.33x | Docs-only |
| S2 — Profile export/import | M | 45 min | 2.0x | QR caught validation gap |
| S4 — Doctor developer checks | S (redefined) | 15 min | — | Reduced from M after discovering E352 |

**Total:** ~97 min active work for 5 stories.

## What Went Well

1. **TDD velocity** — RED-GREEN-REFACTOR consistently fast, especially for S5 and S2
2. **QR value** — Quality review on S2 caught `cast()` without runtime `isinstance` check (PAT-E-597)
3. **Scope reduction** — S4 was redefined from "create doctor from scratch" to "add 4 checks" after discovering E352 already existed in dev
4. **S3 extraction** — Transcript analysis revealed the need for a full situational router (RAISE-501), preventing us from shipping a half-solution

## What Didn't Go Well

1. **Worktree based on wrong branch** — Created from `main` instead of `dev`, missing 1270 commits including the entire doctor module (E352). Required merge with conflict resolution mid-epic
2. **Package rename blind spot** — `rai_cli` → `raise_cli` rename happened in dev. E493 code used old import paths. Took multiple rounds to find all patch string paths in tests
3. **Jira stories not transitioned** — 4 stories completed before anyone noticed Jira was still at "Backlog". Batch-transitioned at the end

## Patterns Captured

- **PAT-E-597:** `from __future__ import annotations` masks NameError for unimported names
- **PAT-E-598:** Bare except in error-isolation can hide import errors

## New Pattern: Worktree Branch Verification

**Always verify the worktree base branch matches `branches.development` from manifest.** Run `git log --oneline {dev_branch} --not HEAD | wc -l` before starting work. If > 0, merge dev first.

## Decisions

- S493.3 moved to RAISE-501 — universal entry point epic (from transcript analysis)
- S493.4 redefined from M to S after discovering E352 doctor already in dev
- Developer checks are WARN not ERROR — advisory only

## Recommendations

1. **For RAISE-501:** Start from the 6 scenarios identified in this epic's analysis. The transcript evidence is strong
2. **Worktree creation process:** Add a gate that verifies worktree is based on dev, not main
3. **Jira sync:** Transition stories as they complete, not in batch at the end
