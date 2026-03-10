---
story_id: "S211.6"
title: "rai adapters list/check"
phase: "plan"
created: "2026-02-23"
---

# Implementation Plan: rai adapters list/check

## Overview
- **Story:** S211.6
- **Size:** S
- **Tasks:** 3
- **Derived from:** design.md § Target Interfaces
- **Created:** 2026-02-23

## Tasks

### Task 1: `rai adapters list` command + formatters

**Objective:** Create the adapters command group with `list` subcommand that shows all entry point groups with their registered adapters.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_adapters.py`
- **Test functions:**
  - `test_list_shows_registered_parsers` — invoke `list`, assert governance parsers appear in output
  - `test_list_shows_empty_groups` — assert groups with no adapters show "(none)"
  - `test_list_json_format` — invoke `list --format json`, assert valid JSON with tier + groups
- **Setup:** Typer `CliRunner` (same pattern as existing CLI tests)
- **Assertion:** Output contains known built-in adapter names (prd, vision, local, etc.)

**GREEN — Implement:**
- **Files:**
  - `src/rai_cli/cli/commands/adapters.py` — `adapters_app` Typer group, `ADAPTER_GROUPS` mapping, `list_command()`
  - `src/rai_cli/output/formatters/adapters.py` — `format_list_human()`, `format_list_json()`
  - `src/rai_cli/cli/main.py` — add `from .commands.adapters import adapters_app` + `app.add_typer(adapters_app, name="adapters")`
- **Integration:** `list_command()` iterates `ADAPTER_GROUPS`, calls `_discover()` per group, builds plain dicts, passes to formatter.

**Verification:**
```bash
pytest tests/cli/commands/test_adapters.py -v
rai adapters list
rai adapters list --format json
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenario "List adapters with none installed beyond built-ins"

---

### Task 2: `rai adapters check` command

**Objective:** Add `check` subcommand that validates each adapter against its Protocol via `isinstance()`.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_adapters.py`
- **Test functions:**
  - `test_check_all_builtins_pass` — invoke `check`, assert all built-in adapters show compliant
  - `test_check_json_format` — invoke `check --format json`, assert valid JSON with `all_passed` field
  - `test_check_broken_adapter_shows_error` — mock a broken entry point, assert error message in output
- **Assertion:** Built-ins pass. Broken adapter shows actionable error with group + name.

**GREEN — Implement:**
- **Files:**
  - `src/rai_cli/cli/commands/adapters.py` — `check_command()`
  - `src/rai_cli/output/formatters/adapters.py` — `format_check_human()`, `format_check_json()`
- **Logic:** For each group, `_discover()` loads classes. For each loaded class, `isinstance(cls, Protocol)` checks compliance. Failed loads (already caught by `_discover()` as warnings) are surfaced as failures.
- **Integration:** Reuses `ADAPTER_GROUPS` mapping from T1.

**Verification:**
```bash
pytest tests/cli/commands/test_adapters.py -v
rai adapters check
rai adapters check --format json
```

**Size:** S
**Dependencies:** T1 (command group + formatters exist)
**AC Reference:** Scenario "Check adapters validates Protocol compliance"

---

### Task 3 (Final): Integration Verification

**Objective:** Validate both commands work end-to-end, all tests pass, types + lint clean.

**Verification:**
```bash
pytest tests/ -x -q
pyright src/rai_cli/cli/commands/adapters.py src/rai_cli/output/formatters/adapters.py
ruff check src/rai_cli/cli/commands/adapters.py src/rai_cli/output/formatters/adapters.py
rai adapters list
rai adapters check
```

**Size:** XS
**Dependencies:** T1, T2

## Execution Order
1. T1 — `list` command + formatters + main.py registration (foundation)
2. T2 — `check` command (builds on T1)
3. T3 — Integration verification (final)

## Risks
- **`_discover()` is module-private:** Currently prefixed with `_`. Either import it directly (same package) or expose it. Low risk — it's in `adapters/registry.py`, commands are in `cli/commands/adapters.py`. Cross-package import of private function. **Mitigation:** Make `_discover` public or add a thin public wrapper. Decide during T1.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | S | -- | |
| T2 | S | -- | |
| T3 | XS | -- | Integration verification |
