---
title: Bugfix Lifecycle
description: Fix bugs with a structured 7-phase pipeline — from reproduction through root cause analysis to verified fix and retrospective.
---

RaiSE v2.4 introduces a **structured bugfix pipeline**: 7 atomic skills orchestrated by a single run command, with 3 human-in-the-loop gates that prevent cascading errors. This replaces the monolithic `/rai-bugfix` from v2.3.

## Why a Pipeline?

Bugs fail differently than features. A feature can be built incrementally; a bug fix that starts from the wrong root cause wastes the entire effort. The pipeline addresses this with **gates at the critical decision points**:

1. **After scoping** — Is this the right problem?
2. **After analysis** — Is this the right root cause and strategy?
3. **After fixing** — Does the fix actually work?

## Quick Start

```
/rai-bugfix-run RAISE-251
```

That's it. The orchestrator detects which phase to start from (or resumes from where you left off), runs all phases inline, and pauses at each gate for your review.

## The 7 Phases

```
/rai-bugfix-start     → Reproduce, scope the bug
/rai-bugfix-triage    → Classify in 4 dimensions
                      ── GATE 1: Scope & Classification ──
/rai-bugfix-analyse   → Root cause analysis (5 Whys, Ishikawa, or direct)
                      ── GATE 2: Root Cause & Strategy ──
/rai-bugfix-plan      → Decompose fix into TDD tasks
/rai-bugfix-fix       → Execute fix with tests
                      ── GATE 3: Fix Verification ──
/rai-bugfix-review    → Retrospective, pattern extraction
/rai-bugfix-close     → Push branch, create MR, verify artifacts
```

### Phase 1: Start

Creates `work/bugs/RAISE-{N}/scope.md` with reproduction steps, environment details, and expected vs actual behavior.

### Phase 2: Triage

Classifies the bug in 4 dimensions:

| Dimension | Values | Purpose |
|-----------|--------|---------|
| **Bug Type** | Logic, Data, Integration, Config, Regression, Performance | What kind of defect |
| **Severity** | Critical, High, Medium, Low | Impact on users |
| **Origin** | Design, Implementation, Environment, External | Where the defect was introduced |
| **Qualifier** | Flaky, Edge-case, Silent, Blocking, Cascading | Behavioral characteristic |

### Phase 3: Analyse

Root cause analysis using signal-driven method selection:

- **Direct** — Cause is obvious from reproduction
- **5 Whys** — Cause is not obvious, needs iterative questioning
- **Ishikawa** — Multiple potential causes, needs systematic exploration

Produces `analysis.md` with root cause, evidence, and multiple fix approaches with trade-offs.

### Phase 4: Plan

Decomposes the selected fix approach into atomic TDD tasks — each task has a test to write first (RED), implementation (GREEN), and optional refactor.

### Phase 5: Fix

Executes the plan: write tests, implement fix, verify the bug no longer reproduces. Commits after each task.

### Phase 6: Review

Retrospective: what caused the bug, what did we learn, are there patterns to extract? Produces `retro.md` and optionally adds patterns via `rai pattern add`.

### Phase 7: Close

Pushes the bug branch, creates a merge request, transitions Jira to Done, verifies all artifacts exist.

## The 3 Gates

Gates are **mandatory** — they cannot be skipped, even at Ri mastery level.

### Gate 1: Scope & Classification

Presented after phases 1-2. You verify:

- Is this the right problem?
- Does the reproduction match what users reported?
- Is the classification correct?

**Responses:** `y` (continue) · `edit` (correct scope/classification) · `reject` (stop)

### Gate 2: Root Cause & Strategy

Presented after phase 3. This is the **highest-value gate** — it presents multiple fix approaches with trade-offs. Rai biases toward the simplest approach that fully addresses the root cause.

```
Fix approaches:
  A: Add gitignore entry for cache file — simple, 1 line
  B: Add cache validation + cleanup on startup — thorough, 40 LOC
  C: Redesign cache storage to use temp directory — most robust, 200 LOC

Recommended: A because the root cause is a missing gitignore entry
```

**Responses:** `a`/`b`/`c` (select approach) · `adjust` (refine strategy) · `reject` (re-analyse)

### Gate 3: Fix Verification

Presented after phase 5. You verify:

- Tests pass
- Bug no longer reproduces
- Changed files look correct

**Responses:** `y` (continue to review + close) · `reject` (review code, identify issues)

## Resume Support

The orchestrator detects existing artifacts and resumes from the most advanced phase. If a session is interrupted, just run `/rai-bugfix-run RAISE-251` again — it picks up where you left off.

## Using Individual Skills

Each phase is independently invocable for targeted work:

```
/rai-bugfix-triage      # Re-classify an already-scoped bug
/rai-bugfix-review      # Run retrospective on an already-fixed bug
```

## Artifacts

All artifacts live in `work/bugs/RAISE-{N}/`:

| File | Phase | Content |
|------|-------|---------|
| `scope.md` | start + triage | Reproduction, classification |
| `analysis.md` | analyse | Root cause, evidence, approaches |
| `plan.md` | plan | TDD task breakdown |
| `retro.md` | review | Retrospective, patterns |
