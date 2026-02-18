# Progress: F128.2 — Decouple Init from Claude Paths

## Status
- **Started:** 2026-02-18
- **Current Task:** 5 of 5
- **Status:** Complete

## Completed Tasks

### Task 1: get_default_skill_dir() — skills/locator.py
- **Commit:** 40f977d
- **Size:** S
- **Notes:** Clean TDD cycle. Added `ide_config` kwarg, resolves from `config.skills_dir`. 16/16 tests.

### Task 2: scaffold_skills() — onboarding/skills.py
- **Commit:** 14f14c2
- **Size:** S
- **Notes:** Same pattern. Antigravity test scaffolds to `.agent/skills/`. 14/14 tests.

### Task 3: UnifiedGraphBuilder.load_skills() — context/builder.py
- **Commit:** 32ed611
- **Size:** S
- **Notes:** Added `ide_config` to `__init__`, stored as instance attr. 90/90 builder tests pass.

### Task 4: generate_claude_md() — onboarding/claudemd.py
- **Commit:** 07c19f2
- **Size:** XS
- **Notes:** Content already IDE-agnostic. Added `ide_config` param for API consistency only. No behavioral change.

### Task 5: Quality gates + integration test
- **Size:** XS
- **Notes:** 2028 passed, 17 skipped, 90.45% coverage. Ruff clean. Pyright 0 errors.

## Discoveries
- `config/paths.py:get_claude_memory_path()` is IDE user-state, not project structure — correctly excluded from scope (4 points, not 5)
- `claudemd.py` content was already IDE-agnostic — only the file path (in init.py) is Claude-specific
- Pattern: `ide_config: IdeConfig | None = None` as keyword-only arg with `get_ide_config()` default — consistent across all 4 functions

## Blockers
- None
