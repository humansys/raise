# Implementation Plan: Publish Skill

## Overview
- **Story:** HF-2
- **Story Points:** 5 SP
- **Size:** M
- **Created:** 2026-02-14
- **Design:** `work/hotfixes/hf-2-publish-skill/design.md`
- **Research:** `work/research/RES-PUBLISH-001/`

## Tasks

### Task 0: Pre-requisite — Fix PEP 440 version + CHANGELOG.md
- **Description:** Fix version drift and PEP 440 compliance. Update `pyproject.toml` from `2.0.0-alpha.7` to `2.0.0a7`. Update `__init__.py` from `2.0.0-alpha.1` to `2.0.0a7`. Create initial `CHANGELOG.md` in Keep a Changelog format with an `[Unreleased]` section summarizing work done so far.
- **Files:**
  - `pyproject.toml` — version field
  - `src/rai_cli/__init__.py` — `__version__`
  - `CHANGELOG.md` — create
- **TDD Cycle:** N/A (config + doc only)
- **Verification:** `uv run python -c "from rai_cli import __version__; print(__version__)"` prints `2.0.0a7`. `grep version pyproject.toml` matches.
- **Size:** XS
- **Dependencies:** None

### Task 1: Version module — parsing, validation, bumping
- **Description:** Create `src/rai_cli/publish/version.py` with PEP 440 version parsing, validation, and bump logic. Pure functions, no side effects. Support bump types: `major`, `minor`, `patch`, `alpha`, `beta`, `rc`, `release`.
- **Files:**
  - `src/rai_cli/publish/__init__.py` — create (empty)
  - `src/rai_cli/publish/version.py` — create
  - `tests/publish/__init__.py` — create (empty)
  - `tests/publish/test_version.py` — create
- **TDD Cycle:**
  - RED: Test `parse_version("2.0.0a7")` returns structured parts. Test `is_pep440("2.0.0-alpha.7")` returns False. Test `bump_version("2.0.0a7", "alpha")` returns `"2.0.0a8"`. Test all bump type transitions from design table.
  - GREEN: Implement with `packaging.version.Version` for parsing + custom bump logic
  - REFACTOR: Ensure type annotations complete
- **Verification:** `uv run pytest tests/publish/test_version.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Changelog module — parsing and updating
- **Description:** Create `src/rai_cli/publish/changelog.py` with functions to: check if CHANGELOG.md has unreleased entries, move unreleased entries to a versioned section with date, read current changelog content.
- **Files:**
  - `src/rai_cli/publish/changelog.py` — create
  - `tests/publish/test_changelog.py` — create
- **TDD Cycle:**
  - RED: Test `has_unreleased_entries(content)` returns True/False correctly. Test `promote_unreleased(content, "2.1.0", "2026-02-14")` moves entries under versioned header.
  - GREEN: Implement with string/regex operations on markdown content
  - REFACTOR: Edge cases (empty unreleased, no changelog file)
- **Verification:** `uv run pytest tests/publish/test_changelog.py -v`
- **Size:** S
- **Dependencies:** None (parallel with Task 1)

### Task 3: Check module — quality gate runner
- **Description:** Create `src/rai_cli/publish/check.py` with a `run_checks()` function that executes all 10 quality gates sequentially, collecting results. Each gate is a function that returns pass/fail with a message. Uses `subprocess.run` for external commands.
- **Files:**
  - `src/rai_cli/publish/check.py` — create
  - `tests/publish/test_check.py` — create
- **TDD Cycle:**
  - RED: Test individual gate functions return correct CheckResult. Test `run_checks()` aggregates results. Test that a failing gate produces non-zero exit.
  - GREEN: Implement gates as separate functions, aggregate in `run_checks()`
  - REFACTOR: Extract gate protocol/interface
- **Verification:** `uv run pytest tests/publish/test_check.py -v`
- **Size:** M
- **Dependencies:** Task 1 (version validation gate uses version module), Task 2 (changelog gate uses changelog module)

### Task 4: CLI commands — `rai publish check` and `rai publish release`
- **Description:** Create `src/rai_cli/cli/commands/publish.py` with Typer commands. Wire `publish_app` into `main.py`. `check` command calls `run_checks()` and displays Rich-formatted results. `release` command orchestrates: check → prompt bump type → version bump → changelog update → commit → tag → push (with confirmation).
- **Files:**
  - `src/rai_cli/cli/commands/publish.py` — create
  - `src/rai_cli/cli/main.py` — modify (add publish_app)
  - `tests/publish/test_cli.py` — create (Typer test runner)
- **TDD Cycle:**
  - RED: Test `rai publish check` returns exit code 0 when all pass. Test `rai publish release --dry-run --bump patch` shows plan without executing. Test `publish_app` is registered.
  - GREEN: Implement commands, wire into main
  - REFACTOR: Consistent output formatting
- **Verification:** `uv run pytest tests/publish/test_cli.py -v` and `uv run rai publish check --help`
- **Size:** M
- **Dependencies:** Task 3 (check module)

### Task 5: `/rai-publish` skill
- **Description:** Create `.claude/skills/rai-publish/SKILL.md` with guided release workflow. Steps: review changes since last release, suggest bump type, run check, confirm and execute release. Register in skill index.
- **Files:**
  - `.claude/skills/rai-publish/SKILL.md` — create
- **TDD Cycle:** N/A (skill file, no code tests)
- **Verification:** Skill appears in skill list, content follows skill template structure
- **Size:** S
- **Dependencies:** Task 4 (skill references CLI commands)

### Task 6: Manual Integration Test
- **Description:** End-to-end validation:
  1. Run `rai publish check` — verify all gates execute and report
  2. Run `rai publish release --dry-run --bump alpha` — verify plan output
  3. Verify `--help` output for both commands
  4. Run full test suite to confirm no regressions
- **Verification:** Both commands work interactively, `uv run pytest -x -q` passes, `uv run pyright src/` clean, `uv run ruff check src/` clean
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order
1. Task 0 — PEP 440 fix (pre-requisite, unblocks everything)
2. Task 1, Task 2 — (parallel, no dependencies on each other)
3. Task 3 — Check module (depends on 1 + 2)
4. Task 4 — CLI commands (depends on 3)
5. Task 5 — Skill (depends on 4)
6. Task 6 — Integration test (depends on all)

## Risks
| Risk | Mitigation |
|------|------------|
| `packaging` library not in deps | Check if already a dependency; add if needed |
| `twine` not installed for check gate | Add as dev dependency or use `uv run twine` |
| Git operations in release command are destructive | `--dry-run` default for first release; explicit confirmation before push |
| Subprocess calls in check module are hard to test | Mock subprocess.run in unit tests; real commands only in integration test |

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 0 | XS | -- | |
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | M | -- | |
| 4 | M | -- | |
| 5 | S | -- | |
| 6 | XS | -- | Integration test |
