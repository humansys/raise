# Progress: RAISE-170 — Temporal Decay and Pattern Scoring

## Status
- **Started:** 2026-02-19 09:30 (approx)
- **Current Task:** 2 of 6
- **Status:** In Progress

## Completed Tasks

### Task 1: Composite scorer in query.py
- **Completed:** 2026-02-19
- **Commit:** c613f6c
- **Notes:**
  - Added `_wilson_lower_bound()`, `calculate_relevance_score()` (composite), scoring constants
  - Foundational exemption checks both `"foundational"` and `"base"` keys (PAT-E-153 backward compat)
  - Call site in `_keyword_search()` updated to pass `concept.metadata`
  - 21 new tests (wilson math, decay, foundational exemption, ordering integration)
  - pyright 0 errors, ruff clean, 46 tests passing

### Task 2: PatternReinforcement model + reinforce_pattern() in writer.py
- **Completed:** 2026-02-19
- **Commit:** eb76666
- **Notes:** Atomic JSONL rewrite (tmp+rename). Vote 0 returns state without modifying file.

### Task 3: rai memory reinforce CLI command
- **Completed:** 2026-02-19
- **Commits:** 9bf5f28, 61f4a60 (vote interface fix)
- **Notes:** Vote as `--vote INT` option (not positional) — avoids Click `-1` flag ambiguity.

### Task 4: Query ordering verification
- **Completed:** 2026-02-19
- **Notes:** TestKeywordSearchOrdering tests from Task 1 cover this. 2 tests passing.

### Task 5: Update rai-story-review skill
- **Completed:** 2026-02-19
- **Commit:** a09cc33
- **Notes:** Step 4.6 added. Skill v1.1.0 → v1.2.0.

### Task 6: Manual Integration Test
- **Completed:** 2026-02-19
- **Notes:**
  - `rai memory query` — correct ordering, foundational patterns first on keyword match
  - `rai memory reinforce PAT-E-183 --vote 1 --from RAISE-170` — correct output with wilson≈0.21
  - Vote 0 N/A — file unchanged ✓
  - `rai memory build && rai memory query` — PAT-E-183 surfaced first after evaluation
  - Pre-existing test_version failure confirmed unrelated to RAISE-170
  - 101 tests passing, pyright 0 errors, ruff clean

## Status
- **Completed:** 2026-02-19
- **Current Task:** 6 of 6 (DONE)
- **Status:** Complete

## Blockers
- None

## Discoveries
- `builder.py._memory_record_to_node()` already copies all JSONL fields to metadata generically —
  `positives/negatives/evaluations` accessible after `rai memory build` without loader changes.
- JSONL uses `"foundational": true`, writer.py uses `entry["base"] = True` — both need checking.
- `--vote INT` as named option is the Pythonic way to handle negative integers in Click/Typer.
- wilson≈0.21 with 1 positive evaluation is correctly conservative (small sample).
