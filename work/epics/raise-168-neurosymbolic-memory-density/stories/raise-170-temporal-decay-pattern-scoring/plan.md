# Implementation Plan: RAISE-170 — Temporal Decay and Pattern Scoring

## Overview
- **Story:** RAISE-170
- **Story Points:** M (5 SP)
- **Feature Size:** M
- **Created:** 2026-02-19

## Pre-Implementation Notes

### Grounding Discoveries

**builder.py copies all JSONL fields to metadata** (`_memory_record_to_node()` lines 1206-1208):
`core_fields = {"id", "type", "content", "created", "date"}` — everything else becomes metadata.
This means `positives`, `negatives`, `evaluations`, `last_evaluated` are **already accessible** in
`ConceptNode.metadata` after `rai memory build`. No separate loader changes needed.

**Foundational field name is `"foundational"`, not `"base"`**:
- Actual JSONL data uses `"foundational": true` (confirmed in `.raise/rai/memory/patterns.jsonl`)
- `bundle.py:61` checks `metadata.get("foundational") is True` ✓ — this works
- `writer.py:387` writes `entry["base"] = True` for new CLI-created patterns (writer bug, pre-existing)
- Scoring function MUST check both: `metadata.get("foundational") or metadata.get("base")`
- This follows PAT-E-153 (JSONL backward compat: read new key first, fall back to old)

**`calculate_relevance_score()` is called in exactly one place**: `query.py:330` inside `_keyword_search()`.
Current signature is `(content, keywords, created)` — need to add `metadata: dict[str, Any]`.

**No separate `bundle.py` for ordering** — query ordering lives in `_keyword_search()` which already
sorts by score descending (line 338). Task 4 confirms this works correctly with the new scorer.

---

## Tasks

### Task 1: Composite scorer in query.py
- **Description:** Replace `calculate_relevance_score()` with the composite formula from design.
  Add scoring constants, `_wilson_lower_bound()` private helper, and update the call site in
  `_keyword_search()` to pass `concept.metadata` as the 4th argument.
  Foundational exemption must check BOTH `metadata.get("foundational")` and `metadata.get("base")`.
- **Files:**
  - `src/rai_cli/context/query.py` — replace function, add helper, add constants, update call site
  - `tests/context/test_query.py` — add tests for new scorer
- **TDD Cycle:**
  - RED: Write tests for `_wilson_lower_bound()` (edge cases: 0 evaluations, all positive, all negative)
  - RED: Write tests for `calculate_relevance_score()` (foundational exemption, decay, wilson modifier, evaluations=0)
  - GREEN: Implement constants + `_wilson_lower_bound()` + new `calculate_relevance_score()`
  - REFACTOR: Ensure clean separation between wilson helper and scorer
- **Key test cases:**
  - `base=true` pattern: score = keyword_hits/max(len(kw),1), no decay
  - `foundational=true` pattern: same exemption (checks both keys)
  - 30-day-old pattern, evaluations=0: recency=0.5, modifier=1.0
  - Pattern with 3 pos / 7 neg (10 evals): wilson ≈ 0.10
  - Pattern with 0 evaluations: modifier = 1.0 (no penalty)
  - `0` vote: evaluations NOT incremented (tested in Task 2, but design verified here)
- **Verification:** `pytest tests/context/test_query.py -v && pyright src/rai_cli/context/query.py && ruff check src/rai_cli/context/query.py`
- **Size:** S
- **Dependencies:** None

### Task 2: PatternReinforcement model + reinforce_pattern() in writer.py
- **Description:** Add `PatternReinforcement` Pydantic model and `reinforce_pattern()` function.
  The function reads patterns.jsonl, finds the pattern by ID, updates reinforcement fields, rewrites atomically.
  Returns a `ReinforceResult` model with updated counts and computed wilson score.
  Vote 0 (N/A): returns current state WITHOUT updating evaluations or positives/negatives.
  Vote +1: increments positives + evaluations. Vote -1: increments negatives + evaluations.
  Always updates `last_evaluated` to today (for +1 and -1 only).
- **Files:**
  - `src/rai_cli/memory/writer.py` — add `PatternReinforcement` model, `ReinforceResult` model, `reinforce_pattern()` function
  - `tests/memory/test_writer.py` — add reinforce tests
- **TDD Cycle:**
  - RED: Write tests for `reinforce_pattern()` (+1, -1, 0, pattern-not-found, no-evaluations-field)
  - GREEN: Add Pydantic models + implement function (read-modify-rewrite JSONL atomically)
  - REFACTOR: Extract JSONL rewrite helper if useful
- **Key implementation notes:**
  - Read all lines, find by ID, parse JSON, update fields, write all lines back (no append)
  - Atomic write: write to temp file (`.jsonl.tmp`), then rename — prevents corruption
  - Pattern not found: raise `KeyError` with clear message
  - `evaluations` field absent in old patterns → default to 0 before incrementing
- **Verification:** `pytest tests/memory/test_writer.py -v && pyright src/rai_cli/memory/writer.py && ruff check src/rai_cli/memory/writer.py`
- **Size:** S
- **Dependencies:** None (can develop in parallel with Task 1)

### Task 3: `rai memory reinforce` CLI command
- **Description:** Add `@memory_app.command("reinforce")` to `memory.py`. Interface:
  `rai memory reinforce PAT-E-XXX +1|0|-1 [--from RAISE-170]`
  Calls `reinforce_pattern()` from writer.py. Outputs summary with wilson score.
  Flags patterns with wilson < SCORING_LOW_WILSON_THRESHOLD (0.15) with `↓ consider reviewing`.
  Vote 0: print `✓ PAT-E-XXX: N/A (not counted)` without any score update.
- **Files:**
  - `src/rai_cli/cli/commands/memory.py` — add `reinforce` command
  - `tests/cli/test_memory.py` — add CLI tests (use CliRunner)
- **TDD Cycle:**
  - RED: Write CLI integration test for `rai memory reinforce` (valid +1, valid -1, vote 0, bad pattern ID)
  - GREEN: Implement command using typer, call `reinforce_pattern()`
  - REFACTOR: Ensure output format matches design spec exactly
- **Expected output format:**
  ```
  ✓ PAT-E-183: positives=4, evaluations=5, wilson≈0.52
  ✓ PAT-E-094: negatives=1, evaluations=1, wilson≈0.03 ↓ consider reviewing
  ✓ PAT-E-151: N/A (not counted)
  ```
- **Note on `--from` flag:** Typer uses `story_id` param name, CLI flag is `--from`.
  Use `typer.Option(None, "--from")` to avoid collision with Python keyword `from`.
- **Verification:** `pytest tests/cli/test_memory.py -k reinforce -v && pyright src/rai_cli/cli/commands/memory.py && ruff check src/rai_cli/cli/commands/memory.py`
- **Size:** S
- **Dependencies:** Task 2 (reinforce_pattern must exist)

### Task 4: Query ordering verification + integration tests
- **Description:** Add integration tests that verify end-to-end query ordering with the new scorer.
  Build a mini graph with patterns of different ages, evaluation histories, and foundational status.
  Assert: foundational patterns score correctly (no decay), older patterns rank lower than newer ones
  with same keywords, high-wilson patterns rank above low-wilson ones with equal keyword matches.
  Also verify the wilson_lower_bound import is accessible from query.py tests.
- **Files:**
  - `tests/context/test_query.py` — add ordering integration tests
- **TDD Cycle:**
  - RED: Write ordering tests (foundational always above decayed, wilson modifier changes rank)
  - GREEN: Should pass after Task 1 — no new implementation needed
  - REFACTOR: Clean up test fixtures if duplicated from Task 1
- **Verification:** `pytest tests/context/ -v --cov=src/rai_cli/context/query --cov-report=term-missing`
- **Size:** XS
- **Dependencies:** Task 1

### Task 5: Update rai-story-review skill
- **Description:** Add pattern evaluation step to `.claude/skills/rai-story-review`.
  After retrospective, Rai evaluates patterns that were loaded at story-start using `rai memory reinforce`.
  Document the evaluation flow: patterns listed in session context behavioral section → evaluate each.
  Votes: +1 = implementation followed, 0 = N/A, -1 = implementation contradicted.
  This is the primary reinforcement signal collection point (RQ6 from RES-TEMPORAL-001).
- **Files:**
  - `.claude/skills/rai-story-review` — add evaluation step
- **TDD Cycle:** N/A (skill file, not code)
- **Verification:** `rai skill validate rai-story-review`
- **Size:** XS
- **Dependencies:** Task 3 (reinforce command must exist)

### Task 6 (Final): Manual Integration Test
- **Description:** Validate the full story end-to-end with running software.
  Test the complete flow: score a query, reinforce a pattern, rebuild, query again, observe score change.
- **Steps:**
  1. `rai memory query "planning estimation"` — note current ordering and scores
  2. `rai memory reinforce PAT-E-183 +1 --from RAISE-170` — confirm output format
  3. `rai memory reinforce PAT-E-151 0 --from RAISE-170` — confirm N/A output (no update)
  4. `rai memory build && rai memory query "planning estimation"` — verify scores updated
  5. Confirm foundational pattern score is NOT affected by decay (same score regardless of date)
  6. Run `pytest --cov=src/rai_cli --cov-report=term-missing` — confirm ≥ 90% coverage
  7. `pyright src/rai_cli/ && ruff check src/rai_cli/` — confirm no errors
- **Verification:** All above steps pass without errors
- **Size:** XS
- **Dependencies:** All previous tasks

---

## Execution Order

```
Task 1 ─────────────────────────────────────────┐
Task 2 ─────────────────────────────────────────┤→ Task 3 → Task 5
                                                 ↓
                                              Task 4 (after Task 1)
                                                 ↓
                                              Task 6 (final — all done)
```

Tasks 1 and 2 can be developed in parallel (no shared code).

## Risks

- **`from` keyword conflict in CLI**: `--from` flag clashes with Python keyword. Use `typer.Option(None, "--from")` with param name `story_id`.
- **JSONL atomic rewrite**: Must use temp-file-then-rename to prevent corruption on crash. Test with concurrent write scenarios.
- **Foundational field name mismatch**: writer.py writes `"base"`, JSONL has `"foundational"`. Scoring must check both. This is a pre-existing inconsistency — do NOT fix writer.py behavior in this story (scope).
- **Wilson with 0 denominator**: `n = pos + neg = 0` when evaluations=0 but we guard with `if evaluations == 0: return 1.0`. Still, need to ensure `n > 0` before dividing in wilson.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Composite scorer | S | -- | Core math logic |
| 2 — reinforce_pattern() | S | -- | Parallel with Task 1 |
| 3 — CLI command | S | -- | Depends on Task 2 |
| 4 — Ordering tests | XS | -- | Depends on Task 1 |
| 5 — Story-review skill | XS | -- | Depends on Task 3 |
| 6 — Integration test | XS | -- | Final gate |
