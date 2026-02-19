# Implementation Plan: RAISE-166 — Memory Query Semantic Density

## Overview
- **Story:** RAISE-166
- **Epic:** RAISE-168 (Neurosymbolic Memory Density)
- **Size:** S
- **Created:** 2026-02-18

## Design Decisions (from interactive session)

Format compact: Markdown-KV flat, one fact per line.
```
# Memory: session management (3 results, keyword_search)
**component** comp-cli.commands.session-module: CLI commands for session management.
**pattern** PAT-E-313: REST-like token protocol for CLI session management...
**story** story-f9-4: F9.4 Session Emitters — Emit session_event from /session-close
[+15 more — use --limit 25 to see all]
```

| Decision | Choice | Evidence |
|----------|--------|----------|
| Structure | Markdown-KV flat | ImprovingAgents: top performer for entity descriptions |
| Fields | type + id + content only | Source/created are noise for AI consumer |
| Header | 1 line: query, count, strategy | TOON principle: shape metadata upfront |
| Content truncation | 150 chars | Compact = scanning; human format for detail |
| Truncation footer | Only when results clipped, with count + hint | Transparency without noise |

## Tasks

### Task 1: Add `total_available` to query metadata
- **Description:** Modify `_keyword_search` and `_concept_lookup` to track total matching concepts before limit is applied. Add `total_available` field to `UnifiedQueryMetadata`. This enables the truncation footer.
- **Files:** `src/rai_cli/context/query.py`, `tests/context/test_query.py`
- **TDD Cycle:** RED (test that metadata has total_available > limit when results truncated) → GREEN (add field, track count) → REFACTOR
- **Verification:** `pytest tests/context/test_query.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Add `--format compact` formatter
- **Description:** Add `_format_compact()` function in memory.py. Format: header line + one Markdown-KV line per result + optional truncation footer. Content truncated at 150 chars. Wire `--format` option to accept "compact" value.
- **Files:** `src/rai_cli/cli/commands/memory.py`, `tests/cli/commands/test_memory.py`
- **TDD Cycle:** RED (test compact format output matches expected structure) → GREEN (implement formatter + wire flag) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_memory.py -v`
- **Size:** S
- **Dependencies:** Task 1 (needs total_available for truncation footer)

### Task 3: Fix concept_lookup strategy default
- **Description:** The JIRA says concept_lookup silently falls back to keyword_search returning 0 results first. Verify the current behavior, ensure keyword_search is the reliable default (it already is in code — `UnifiedQueryStrategy.KEYWORD_SEARCH`), and ensure concept_lookup only activates via explicit `--strategy concept_lookup`. If there's a silent fallback in the engine, remove it.
- **Files:** `src/rai_cli/context/query.py`, `tests/context/test_query.py`
- **TDD Cycle:** RED (test that concept_lookup with non-existent ID returns empty, does NOT fallback to keyword_search) → GREEN (verify/fix) → REFACTOR
- **Verification:** `pytest tests/context/test_query.py -v`
- **Size:** XS
- **Dependencies:** None

### Task 4: Manual integration test
- **Description:** Run `rai memory query` with all three formats (human, compact, json) and verify output. Test truncation footer with low --limit. Test concept_lookup explicitly.
- **Verification:** Demo all three formats interactively
- **Size:** XS
- **Dependencies:** Tasks 1, 2, 3

## Execution Order
1. Task 1 + Task 3 (parallel — independent)
2. Task 2 (depends on Task 1)
3. Task 4 (final validation)

## Risks
- **concept_lookup "bug" may already be fixed**: The code shows keyword_search as default. The JIRA describes a problem from SES-205 — need to verify current state before changing anything.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | May be verify-only |
| 4 | XS | -- | Integration test |
