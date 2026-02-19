# Implementation Plan: RAISE-202 — Roo Code agent support

## Overview
- **Story:** RAISE-202
- **Story Points:** S (3 SP)
- **Created:** 2026-02-19

## Tasks

### Task 1: Add roo.yaml agent config
- **Description:** Create `src/rai_cli/agents/roo.yaml` with Roo Code paths and detection markers. Follows identical structure to `windsurf.yaml` / `antigravity.yaml`.
- **Files:** `src/rai_cli/agents/roo.yaml` (create)
- **TDD Cycle:** No TDD — pure data file; validated by Task 2 tests
- **Verification:** File exists, valid YAML, contains `agent_type: roo`, `skills_dir: .roo/skills`, `instructions_file: .roo/rules/raise.md`, markers include `.roo/rules`, `.roo`, `.rooignore`
- **Size:** XS
- **Dependencies:** None

### Task 2: Extend agents.py — Literal, Enum, BUILTIN_AGENTS
- **Description:** Add `"roo"` to `BuiltinAgentType` Literal, `AgentChoice` enum, and `BUILTIN_AGENTS` dict in `src/rai_cli/config/agents.py`. Update `get_agent_config` if needed (no change expected — registry lookup is generic).
- **Files:** `src/rai_cli/config/agents.py` (modify)
- **TDD Cycle:**
  - RED: Update `test_five_builtin_agents` → `test_six_builtin_agents` expecting `"roo"` in registry
  - RED: Add `test_roo_registry_values` asserting paths and markers
  - RED: Add `AgentChoice.roo` assertion in `TestAgentChoice`
  - GREEN: Add `"roo"` to Literal, enum, and BUILTIN_AGENTS
- **Verification:** `pytest tests/config/test_agents.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Integration test — rai init --agent roo
- **Description:** Add test in `tests/cli/commands/test_init.py` verifying `rai init --agent roo` scaffolds `.roo/skills/` and `.roo/rules/raise.md`. Follow the pattern of `test_agent_windsurf_produces_windsurf_structure`.
- **Files:** `tests/cli/commands/test_init.py` (modify)
- **TDD Cycle:**
  - RED: Add `test_agent_roo_produces_roo_structure` — assert `.roo/skills/rai-session-start/SKILL.md` exists, `.roo/rules/raise.md` exists
  - RED: Add `test_roo_detect_recognizes_roo_directory` — create `.roo/` dir, run `--detect`, assert Roo Code detected
  - GREEN: Tasks 1+2 already cover implementation; tests should pass
- **Verification:** `pytest tests/cli/commands/test_init.py -k "roo" -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 4 (Final): Manual Integration Test
- **Description:** Run `rai init --agent roo` in a temp directory. Verify `.roo/skills/` contains the expected skill dirs and `.roo/rules/raise.md` exists with content. Run `rai skill list` from the temp dir.
- **Verification:** Live demo — skills scaffold correctly, instructions present, no errors
- **Size:** XS
- **Dependencies:** Tasks 1–3

## Execution Order
1. Task 1 — roo.yaml (no deps, start here)
2. Task 2 — agents.py (depends on Task 1 YAML being loadable)
3. Task 3 — integration tests (depends on Task 2 being wired)
4. Task 4 — manual integration test (final gate)

## Risks
- `BuiltinAgentType` Literal change: pyright may require explicit cast in call sites → check with `pyright` after Task 2
- Agent registry YAML loading: registry loads from package, ensure `roo.yaml` is included in `MANIFEST.in` or `pyproject.toml` package data → verify during Task 1

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — roo.yaml | XS | — | |
| 2 — agents.py | S | — | |
| 3 — integration tests | S | — | |
| 4 — manual integration | XS | — | |
