# Implementation Plan: S-RENAME (raise → rai)

## Overview
- **Story:** S-RENAME
- **Story Points:** 5 SP
- **Size:** M
- **Created:** 2026-02-11
- **Pattern:** PAT-151 (3-pass rename: batch 80%, targeted 15%, audit 5%)

## Disambiguation Rule

Before each task, apply the heuristic from design.md:
- Python keyword `rai` → NO CHANGE
- Framework name "RaiSE" → NO CHANGE
- `.raise/` directory → NO CHANGE
- CLI command (`rai memory`, etc.) → RENAME to `rai`
- Python module (`rai_cli`, `from raise_cli`) → RENAME to `rai_cli`
- CLI-identity symbols (`RaiseError`, `RaiseSettings`, `RAISE_` env) → RENAME to `Rai*`/`RAI_`
- XDG paths (`~/.config/raise/`) → RENAME to `~/.config/rai/`

## Tasks

### Task 1: Rename Python module directory
- **Description:** `git mv src/rai_cli src/rai_cli`. This is the foundation — everything else depends on it.
- **Files:** `src/rai_cli/` → `src/rai_cli/` (229 files)
- **TDD Cycle:** No tests — pure git mv
- **Verification:** `ls src/rai_cli/__init__.py` exists, `ls src/rai_cli` fails
- **Size:** XS
- **Dependencies:** None

### Task 2: Batch rename Python imports and module references
- **Description:** sed-replace `rai_cli` → `rai_cli` across all `.py` files in `src/` and `tests/`. This is the 80% batch pass (PAT-151). Also update `from raise_cli` → `from rai_cli` and `import raise_cli` → `import rai_cli`.
- **Files:** ~78 source files + ~98 test files
- **TDD Cycle:** GREEN — `uv run pytest` must pass after this
- **Verification:** `uv run pytest` passes; `grep -rn 'raise_cli' --include='*.py' src/ tests/` returns 0 hits
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Rename CLI-identity symbols
- **Description:** Rename `RaiseError` → `RaiError`, `RaiseSettings` → `RaiSettings`, `env_prefix="RAISE_"` → `env_prefix="RAI_"`, TOML table `"raise"` → `"rai"`, XDG dir `"raise"` → `"rai"`. Apply the disambiguation rule — `RAISE_PROJECT_DIR` stays (it refers to `.raise/` dir).
- **Files:**
  - `src/rai_cli/exceptions.py` — class rename + all refs
  - `src/rai_cli/config/settings.py` — class rename, env_prefix, toml_table
  - `src/rai_cli/config/paths.py` — XDG `"raise"` → `"rai"` in `_get_xdg_dir` return
  - `src/rai_cli/cli/main.py` — Typer name, version string
  - All files importing `RaiseError` or `RaiseSettings`
  - `tests/config/test_cascade.py` — `[tool.raise]` → `[tool.rai]` in test fixtures
- **TDD Cycle:** GREEN — tests must pass
- **Verification:** `uv run pytest` passes; `grep -rn 'RaiseError\|RaiseSettings\|env_prefix="RAISE_"' --include='*.py'` returns 0 hits
- **Size:** M
- **Dependencies:** Task 2

### Task 4: Update pyproject.toml
- **Description:** Update package identity: `name = "rai-cli"`, entry point `rai = "rai_cli.cli.main:app"`, hatch build paths, coverage source, `[tool.raise]` → `[tool.rai]`. Regenerate lock file.
- **Files:** `pyproject.toml`, `uv.lock`
- **TDD Cycle:** GREEN — `uv run rai --help` must work
- **Verification:** `uv run rai --help` shows help; `uv run rai --version` shows `rai-cli version`; `uv run pytest` passes
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Update skills (`.claude/skills/` and `src/rai_cli/skills_base/`)
- **Description:** Replace `` `rai `` → `` `rai `` in CLI command references within SKILL.md files (both locations: `.claude/skills/` and `src/rai_cli/skills_base/`). ~122 occurrences across ~33 files. Apply disambiguation — keep "RaiSE" framework references.
- **Files:** `.claude/skills/*/SKILL.md`, `src/rai_cli/skills_base/*/SKILL.md`
- **TDD Cycle:** N/A (documentation)
- **Verification:** `grep -rn '` + "`" + `rai ` + "`" + `' .claude/skills/ src/rai_cli/skills_base/` returns 0 CLI command hits
- **Size:** M
- **Dependencies:** Task 4

### Task 6: Update docs, ADRs, and work artifacts
- **Description:** Targeted pass (PAT-151 15%) — update references to `rai` CLI command and `rai-cli` package in governance docs, ADRs, dev SOPs, research docs, and work artifacts. Apply disambiguation carefully — "RaiSE CLI" (the framework's CLI) stays, but `` `rai session` `` → `` `rai session` ``, `rai-cli` package → `rai-cli`.
- **Files:** `governance/*.md`, `dev/**/*.md`, `work/**/*.md`, `CONTRIBUTING.md`, `.claude/RAI.md`
- **TDD Cycle:** N/A (documentation)
- **Verification:** Manual audit of key docs
- **Size:** M
- **Dependencies:** Task 4

### Task 7: Audit pass — grep for stale terms
- **Description:** Final 5% audit (PAT-151). Comprehensive grep for stale references: `rai_cli`, `rai-cli`, `RaiseError`, `RaiseSettings`, `env_prefix="RAISE_"`, `[tool.raise]`. Exclude: Python `rai` keyword, "RaiSE" framework name, `.raise/` directory, `RAISE_PROJECT_DIR`. Fix any survivors.
- **Files:** Entire codebase
- **TDD Cycle:** N/A
- **Verification:** Audit grep returns only expected exclusions (Python `rai`, `.raise/`, "RaiSE")
- **Size:** S
- **Dependencies:** Tasks 5, 6

### Task 8: Full validation and manual integration test
- **Description:** Run full test suite, pyright, ruff. Test `rai` command interactively: `rai --help`, `rai --version`, `rai memory build`, `rai session start --context`. Verify `.raise/` directory detection still works.
- **Files:** None (validation only)
- **TDD Cycle:** N/A
- **Verification:** `uv run pytest` >90% coverage; `uv run pyright`; `uv run ruff check .`; `rai --help` works
- **Size:** S
- **Dependencies:** Task 7

## Execution Order

```
Task 1 (git mv)
  → Task 2 (batch imports)
    → Task 3 (symbol rename)
      → Task 4 (pyproject.toml)
        → Task 5 (skills) ──┐
        → Task 6 (docs)  ───┤  (parallel)
                             ↓
                      Task 7 (audit)
                             ↓
                      Task 8 (validation)
```

## Risks

- **False positives:** `rai` as Python keyword will appear in greps — must filter carefully
- **`.raise/` directory confusion:** The constant `RAISE_PROJECT_DIR = ".raise"` must NOT change — it refers to the framework directory, not the CLI name
- **Stale references in docs:** PAT-151 warns about long tail — audit pass (Task 7) is the safety net
- **Lock file conflicts:** `uv.lock` regeneration may have diff noise — expected

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 - git mv | XS | -- | |
| 2 - batch imports | M | -- | |
| 3 - symbol rename | M | -- | |
| 4 - pyproject.toml | S | -- | |
| 5 - skills | M | -- | |
| 6 - docs | M | -- | |
| 7 - audit | S | -- | |
| 8 - validation | S | -- | |
