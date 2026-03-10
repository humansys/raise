# Retrospective: S-RENAME (raise → rai)

## Summary
- **Story:** S-RENAME
- **Started:** 2026-02-11
- **Completed:** 2026-02-11
- **Estimated:** ~60 min (5 SP, M-sized)
- **Actual:** ~25 min
- **Files changed:** 554 (214 code + 340 docs)
- **Tests:** 1696 passed, 92.67% coverage

## What Went Well
- **Disambiguation heuristic** worked perfectly — zero false positives on "RaiSE" framework name or `.raise/` directory
- **Inside-out strategy** (dir rename → imports → symbols → config → docs) minimized broken states
- **PAT-151 three-pass pattern** applied cleanly: batch sed (80%), targeted fixes (15%), comprehensive grep audit (5%)
- **Single test run** validated everything — no back-and-forth debugging
- Committing after the code layer (before docs) created a clean checkpoint

## What Could Improve
- The old `raise` entry point in `.venv/bin/raise` became stale after rename — the `raise` command used in telemetry calls failed until switched to `uv run rai`. Should have anticipated this and switched earlier.
- The design.md and plan.md got partially rewritten by the doc-layer sed (backtick `raise` → `rai` hit references to the old state). Not harmful but made the plan/design less useful as historical documents showing the "before" state.

## Heutagogical Checkpoint

### What did you learn?
- Large mechanical renames with a clear disambiguation heuristic are fast and safe. The key is defining the heuristic BEFORE starting, not discovering edge cases mid-rename.
- `git mv` + `sed` + `grep audit` is a proven three-tool pattern for codebase renames.

### What would you change about the process?
- Freeze design/plan documents from the doc-layer sed pass — they document intent, not current state.
- After entry point rename, immediately re-install (`uv sync`) and verify the new command works before proceeding to doc updates.

### Are there improvements for the framework?
- Consider a "rename checklist" as a reference for future mechanical renames (entry points, env vars, TOML tables, XDG dirs, skills, docs).

### What are you more capable of now?
- Confident that the disambiguation heuristic (CLI command vs framework name vs directory) can be applied consistently across ~550 files without errors.

## Patterns

### PAT-NEW: Entry point stale after rename
After renaming a CLI entry point in pyproject.toml, the old command in .venv/bin/ becomes stale. Always re-install and verify the new command works immediately after pyproject.toml changes.

### PAT-NEW: Disambiguation heuristic before mechanical rename
Define a clear heuristic table (what changes / what stays / why) BEFORE starting a rename. The heuristic is the quality gate — without it, false positives on similar terms are inevitable.

## Improvements Applied
- None needed for framework skills — the process worked well.

## Action Items
- [x] All code renamed
- [x] All skills updated
- [x] All docs updated
- [x] Audit pass clean
- [x] Full validation green
