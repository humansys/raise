# Implementation Plan: S247.4 — Kill Redundancies

## Overview
- **Story:** S247.4
- **Size:** XS
- **Tasks:** 3
- **Created:** 2026-02-23
- **Updated:** 2026-02-23 (post arch review Q1-Q3)

## Architecture Review Decisions
- Q1: Clean `CalibrationInput` + `append_calibration` from `memory/__init__.py` (not just memory.py)
- Q2: No migration needed — `calibration.jsonl` readers still active
- Q3: Remove calibration line from session-close skills (not replace)

## Tasks

### Task 1: Remove 3 commands from memory.py + clean orphaned exports

**Objective:** Delete `generate`, `add-calibration`, `add-session` commands, clean imports, clean orphaned exports from `memory/__init__.py`.

**Files:**
- `src/rai_cli/cli/commands/memory.py` — delete generate (L247-278), add-calibration (L363-469), add-session (L472-532), clean imports (CalibrationInput, MemoryScope, SessionInput, append_calibration, append_session, get_memory_dir_for_scope), update docstring to reflect shim-only state
- `src/rai_cli/memory/__init__.py` — remove `CalibrationInput` and `append_calibration` from imports and `__all__` (Q1)

**Verification:**
```bash
pytest tests/cli/commands/test_memory.py -v
ruff check src/rai_cli/cli/commands/memory.py src/rai_cli/memory/__init__.py
pyright src/rai_cli/cli/commands/memory.py src/rai_cli/memory/__init__.py
```

**Size:** S

### Task 2: Remove/update tests + fix onboarding test

**Objective:** Delete dead test classes, delete dedicated test file, fix onboarding assertion.

**Files:**
- `tests/cli/commands/test_memory.py` — delete `TestAddCalibration` and `TestAddSession` classes
- `tests/cli/commands/test_memory_generate.py` — delete entire file
- `tests/onboarding/test_memory_md.py` — update assertion that checks for "raise memory generate"

**Verification:**
```bash
pytest tests/cli/commands/test_memory.py tests/onboarding/test_memory_md.py -v
```

**Size:** S
**Dependencies:** T1

### Task 3: Update references (skills + docs)

**Objective:** Clean all external references to deleted commands.

**Files:**
- `.claude/skills/rai-session-close/SKILL.md` — remove calibration lines entirely (Q3)
- `.agent/skills/rai-session-close/SKILL.md` — same (Q3)
- `dev/happy-path-guide.md` — remove add-calibration + add-session rows
- `dev/happy-path-guide-es.md` — same
- `docs/src/content/docs/docs/cli/index.mdx` — remove add-calibration + add-session sections

**Verification:**
```bash
grep -r "add-calibration\|add-session\|memory generate" .claude/skills/ .agent/skills/ dev/happy-path-guide*.md docs/src/content/docs/docs/cli/index.mdx | grep -v "node_modules" && echo "REFERENCES REMAIN" || echo "CLEAN"
```

**Size:** S
**Dependencies:** None (parallel with T1/T2)

## Execution Order
1. T1 (delete commands + clean exports) + T3 (update refs) — parallel
2. T2 (delete tests) — after T1

## Risks
- Imports shared with remaining commands — verify before deleting

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
