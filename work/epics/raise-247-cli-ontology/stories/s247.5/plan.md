# Implementation Plan: Merge publish+release, flatten singletons

## Overview
- **Story:** S247.5
- **Size:** S
- **Tasks:** 4
- **Derived from:** design.md § Target Interfaces + arch review findings
- **Created:** 2026-02-23
- **Arch review:** PASS WITH QUESTIONS — Q1/Q2 resolved (eliminate CLI plumbing tests, integrate muda cleanup in T1/T3)

## Arch Review Decisions

- **Q1:** Eliminate `tests/publish/test_cli.py` entirely — domain logic already tested in `test_check.py`/`test_version.py`. CLI integration tests are plumbing muda (PAT-E-444).
- **Q2:** Integrate test muda cleanup into T1 and T3 (no separate task).

## Test Muda Cleanup (integrated into tasks)

| File | Action | In Task |
|------|--------|---------|
| `tests/publish/test_cli.py` | Delete entire file | T1 |
| `tests/cli/commands/test_base.py` | Migrate 4 tests to point at `rai info` | T3 |
| `tests/cli/commands/test_profile.py` → `test_profile_no_args_shows_help` | Rewrite (behavior changes) | T3 |
| `tests/cli/commands/test_profile.py` → `test_profile_show_help` | Delete (plumbing muda) | T3 |

## Tasks

### Task 1: Merge publish commands into release group

**Objective:** Move `check` and `release` commands from `publish.py` into `release.py` as `check` and `publish`. Delete CLI plumbing tests.

**RED — Write Failing Test:**
- **File:** `tests/cli/test_release.py`
- **Test function:** `test_release_publish_requires_bump_or_version`
- **Setup:** Given the CLI app
- **Action:** Invoke `rai release publish` with no args
- **Assertion:** exits non-zero with error about --bump or --version required

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/release.py`
- Move `check_command`, `release_command` (renamed to `publish_command`), and private helpers (`_find_project_paths`, `_read_current_version`, `_display_results`) from `publish.py`
- Add imports: `re`, `subprocess`, `date`, `BumpType`, `bump_version`, `is_pep440`, `sync_version_files`, `CheckResult`, `run_checks`
- Register as `@release_app.command("check")` and `@release_app.command("publish")`

**CLEANUP — Test muda:**
- Delete `tests/publish/test_cli.py` — domain logic covered by `test_check.py`/`test_version.py`

**Verification:**
```bash
pytest tests/cli/test_release.py tests/publish/ -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenario "publish commands absorbed into release group"

---

### Task 2: Convert publish.py to deprecation shim

**Objective:** Replace `publish.py` with a thin deprecation shim that warns and delegates to the new `release` commands.

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/publish.py`
- Replace entire file with shim pattern (same as `memory.py`): `_deprecation_warning` + lazy import from `release` module + delegate
- `publish check` → warns → calls `release.check_command`
- `publish release` → warns → calls `release.publish_command`

**Verification:**
```bash
rai publish check --help 2>&1  # should show deprecation on stderr
rai release check --help       # should work directly
```

**Size:** XS
**Dependencies:** Task 1
**AC Reference:** Scenario "publish commands absorbed into release group" (backward-compat part)
**Note:** No tests for shim per PAT-E-444.

---

### Task 3: Flatten base→info and profile

**Objective:** Create `rai info` top-level command, make `rai profile` (no subcommand) show profile directly, clean up test muda.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_base.py` — change invocations from `["base", "show"]` to `["info"]`
- **File:** `tests/cli/commands/test_profile.py` — rewrite `test_profile_no_args_shows_help` to expect profile output (or helpful message when no profile), delete `test_profile_show_help`
- **Assertion:** `rai info` exits 0 with version info; `rai profile` exits 0 with profile data

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/info.py` (new) — move `show` logic + helpers from `base.py`
- **File:** `src/rai_cli/cli/main.py` — import and register `app.command("info")(info_command)`
- **File:** `src/rai_cli/cli/commands/base.py` — convert to deprecation shim (`base show` → warns → calls `info_command`)
- **File:** `src/rai_cli/cli/commands/profile.py` — change to `invoke_without_command=True`, add callback that calls `show()` when no subcommand

**CLEANUP — Test muda:**
- Delete `test_profile_show_help` (plumbing)
- Update mock paths in test_base.py from `rai_cli.cli.commands.base._get_project_root` to `rai_cli.cli.commands.info._get_project_root`

**Verification:**
```bash
pytest tests/cli/commands/test_base.py tests/cli/commands/test_profile.py -v
```

**Size:** S
**Dependencies:** None (parallel with T1-T2)
**AC Reference:** Scenarios "base show flattened to rai info" + "profile show flattened to rai profile"

---

### Task 4 (Final): Integration Verification

**Objective:** Validate all new commands work end-to-end, all deprecation shims warn correctly.

**Verification:**
```bash
# New commands work
rai release check --help
rai release publish --help
rai release list --help
rai info
rai profile

# Deprecation shims warn
rai publish check --help 2>&1 | grep -i deprecated
rai publish release --help 2>&1 | grep -i deprecated
rai base show 2>&1 | grep -i deprecated

# Full test suite + gates
pytest tests/cli/ tests/publish/ -v
pyright src/rai_cli/cli/commands/release.py src/rai_cli/cli/commands/publish.py src/rai_cli/cli/commands/info.py src/rai_cli/cli/commands/profile.py src/rai_cli/cli/commands/base.py
ruff check src/rai_cli/cli/commands/
```

**Size:** XS
**Dependencies:** T1, T2, T3

## Execution Order

1. **T1** (merge publish→release) + **T3** (flatten base+profile) — parallel, independent
2. **T2** (publish shim) — depends on T1
3. **T4** (integration verification) — depends on all

```
T1 (merge) ──→ T2 (shim) ──┐
T3 (flatten) ────────────────┼──→ T4 (verify)
```

## Risks
- **Typer `invoke_without_command` + existing `show` subcommand:** Need to verify both `rai profile` and `rai profile show` work. Low risk — well-documented Typer pattern.
- **Import paths in shims:** Lazy imports must use correct paths after move. Low risk — same pattern as S1-S3.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1: merge publish→release + muda cleanup | S | -- | |
| T2: publish shim | XS | -- | |
| T3: flatten base+profile + muda cleanup | S | -- | |
| T4: integration verify | XS | -- | |
