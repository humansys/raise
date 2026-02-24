---
story: RAISE-136
title: Graph schema crash on unknown NodeType — graceful degradation
date-started: 2026-02-24
date-completed: 2026-02-24
size-estimated: XS
size-actual: S
time-estimated: 30 min
time-actual: ~60 min (includes /rai-debug + /rai-debug skill improvement)
---

## Summary

Bugfix story: `rai graph build` / `rai session start` hard crash when saved graph
contains nodes that fail deserialization. Fixed with a 9-line try/except in
`iter_concepts()`. 2 new tests (28 total in test_graph.py), all gates green.

**What changed:** `src/rai_cli/context/graph.py:iter_concepts()` — error boundary
wrapping `_reconstruct_node()`. Unknown/drifted nodes emit warning + skip instead
of crashing the process.

## What Went Well

- `/rai-debug` skill worked as intended for S-tier bug: Genchi Genbutsu led directly
  to the real crash site (`iter_concepts`, not `_reconstruct_node`)
- Quality review caught unused import that linting gate missed (tests/ not in scope)
- The session started with improving `/rai-debug` itself, then used it immediately —
  learning applied in the same session

## What to Improve

- Gate check: `ruff check src/ tests/` — not just `src/`. Added as PAT-E-484.
- Bug report description should be treated as symptom, not mechanism. The bug said
  "NodeType Literal rejects" but Literal had already been changed to str. Added as
  PAT-E-485.

## Heutagogical Checkpoint

1. **What did you learn?**
   Crash path was not where bug report pointed. Real issue: `GraphNode.model_validate`
   fails on any missing required field, not just unknown type. Genchi Genbutsu (going
   to see the code) was essential to find the real site.

2. **What would you change about the process?**
   Lint gate scope. Applied immediately as PAT-E-484 and will apply in future gates.

3. **Framework improvements?**
   `/rai-debug` updated this session (v2.1.0) — triage table, lite output for XS,
   story-plan integration. Used successfully on this very bug. Feedback loop works.

4. **What are you more capable of now?**
   Using `/rai-debug` as formal entry point for bugfix stories, not ad-hoc. The
   tier classification (XS/S/M/L) prevents both over- and under-analysis.

## Improvements Applied

- PAT-E-484: ruff gate scope (src/ + tests/)
- PAT-E-485: bug report mechanism ≠ root cause
- PAT-E-447 reinforced (quality review + arch review as combo)

## Parking Lot

- `iter_relationships()` has same missing error boundary — lower risk, separate XS
- Lint gate for tests/ — process improvement, not a code issue
