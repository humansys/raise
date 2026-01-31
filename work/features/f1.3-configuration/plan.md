---
feature_id: "F1.3"
title: "Configuration System - Implementation Plan"
created: "2026-01-31"
status: "ready"
total_estimate: "6-8 hours"
---

# Implementation Plan: F1.3 Configuration System

> **Feature**: Configuration System (5 SP)
> **Design**: [design.md](./design.md)

---

## Task Breakdown

### Task 1: XDG Directory Helpers

**Description**: Create XDG-compliant directory helper functions

**Deliverables**:
- `src/raise_cli/config/paths.py` with:
  - `get_config_dir() -> Path`
  - `get_cache_dir() -> Path`
  - `get_data_dir() -> Path`
- Tests in `tests/config/test_paths.py`

**Implementation**:
```python
# Each function:
# 1. Check for XDG_*_HOME env var
# 2. Fall back to standard location if not set
# 3. Append "/raise" to the base path
# 4. Return Path object (don't create directories)
```

**Verification**:
- [ ] All three functions implemented with docstrings
- [ ] Tests verify default paths (~/.config/raise, etc.)
- [ ] Tests verify XDG env var override (set XDG_CONFIG_HOME, verify path changes)
- [ ] `pyright --strict` passes
- [ ] `ruff check` passes

**Dependencies**: None (independent)

**Estimate**: 1-2 hours

---

### Task 2: RaiseSettings Pydantic Model

**Description**: Create configuration settings class using Pydantic BaseSettings

**Deliverables**:
- `src/raise_cli/config/settings.py` with:
  - `RaiseSettings` class
  - All fields from design spec
- Tests in `tests/config/test_settings.py`

**Implementation**:
```python
# Key aspects:
# 1. BaseSettings with SettingsConfigDict
# 2. env_prefix="RAISE_"
# 3. All fields with correct types and defaults
# 4. Field validators where needed (e.g., verbosity range)
```

**Verification**:
- [ ] RaiseSettings class with all fields from design spec
- [ ] Model config includes env_prefix, toml_file settings
- [ ] Default values match design spec
- [ ] Tests verify field types and defaults
- [ ] Tests verify validation (e.g., invalid verbosity rejected)
- [ ] `pyright --strict` passes
- [ ] `ruff check` passes

**Dependencies**: None (independent)

**Estimate**: 2 hours

---

### Task 3: Configuration Cascade Tests

**Description**: Create integration tests verifying the 5-level precedence cascade

**Deliverables**:
- `tests/config/test_cascade.py` with integration tests

**Implementation**:
```python
# Test each precedence level:
# 1. CLI args override everything
# 2. Env vars override file configs
# 3. pyproject.toml overrides user config
# 4. User config (~/.config/raise/config.toml) overrides defaults
# 5. Defaults used when nothing else set

# Use tmp_path fixture for file-based configs
# Use monkeypatch fixture for env vars
```

**Verification**:
- [ ] Test: CLI args win over env vars
- [ ] Test: Env vars win over pyproject.toml
- [ ] Test: pyproject.toml wins over user config
- [ ] Test: User config wins over defaults
- [ ] Test: Defaults used when no overrides
- [ ] All tests pass
- [ ] Coverage >90% on RaiseSettings class

**Dependencies**: Task 2 (needs RaiseSettings to exist)

**Estimate**: 2 hours

---

### Task 4: CLI Integration

**Description**: Integrate RaiseSettings with CLI context

**Deliverables**:
- Modified `src/raise_cli/cli/main.py`:
  - Create `RaiseSettings` instance in main CLI callback
  - Override with CLI arg values (--format, -v/-q)
  - Store in `ctx.obj["settings"]`
- Tests in `tests/cli/test_main.py` (update existing)

**Implementation**:
```python
# In main CLI callback:
# 1. Gather CLI args (format, verbosity from options)
# 2. Create settings = RaiseSettings(output_format=format, verbosity=verbosity, ...)
# 3. Store in ctx.obj["settings"] = settings
# 4. Keep existing ctx.obj["format"] for backward compat (or migrate?)
```

**Verification**:
- [ ] CLI creates RaiseSettings instance with CLI overrides
- [ ] Settings stored in ctx.obj
- [ ] Tests verify CLI args override settings correctly
- [ ] Existing F1.2 tests still pass
- [ ] `pyright --strict` passes
- [ ] `ruff check` passes

**Dependencies**: Task 2 (needs RaiseSettings), Task 1 (might use XDG helpers for user config path)

**Estimate**: 1-2 hours

---

### Task 5: Component Catalog Documentation

**Description**: Update component catalog with new configuration components

**Deliverables**:
- Updated `dev/components.md` with:
  - RaiseSettings entry
  - XDG helpers entry

**Implementation**:
```markdown
# Add entries for:
# - src/raise_cli/config/settings.py (RaiseSettings)
# - src/raise_cli/config/paths.py (XDG helpers)
# Include: location, purpose, public API, dependencies, added date
```

**Verification**:
- [ ] Component catalog has RaiseSettings entry
- [ ] Component catalog has XDG helpers entry
- [ ] Entries follow existing format
- [ ] Links to ADRs included (ADR-002, ADR-004)

**Dependencies**: Tasks 1, 2, 4 (document what's implemented)

**Estimate**: 30 minutes

---

## Execution Order

### Phase 1: Core Implementation (Parallel)
1. **Task 1** (XDG helpers) - Independent
2. **Task 2** (RaiseSettings) - Independent

### Phase 2: Integration & Verification (Sequential)
3. **Task 3** (Cascade tests) - Depends on Task 2
4. **Task 4** (CLI integration) - Depends on Task 2

### Phase 3: Documentation
5. **Task 5** (Component catalog) - Depends on Tasks 1, 2, 4

**Parallelization opportunity**: Tasks 1 and 2 can be done in parallel.

---

## Verification Strategy

### Per-Task Verification
- Each task has specific checklist (see task sections above)
- All code must pass: `pyright --strict`, `ruff check`, `pytest`
- No task marked complete until verification passes

### Feature-Level Verification (Gate)
After all tasks complete, verify against F1.3 acceptance criteria:
- [ ] All "Must Have" items from design.md satisfied
- [ ] Test coverage >90% overall
- [ ] Integration tests prove cascade works end-to-end
- [ ] Component catalog updated
- [ ] No regressions (F1.2 tests still pass)

---

## Rollback Plan

If any task fails verification after 3 attempts:
1. Document the blocker in `work/features/f1.3-configuration/blockers.md`
2. Determine if it's a design issue or implementation issue
3. If design issue: Update design.md and restart task
4. If implementation issue: Pair debug or escalate
5. If critical blocker: Park feature and escalate to Emilio

---

## Progress Tracking

**Status Legend**: ⬜ Not started | 🟡 In progress | ✅ Complete | ❌ Blocked

| Task | Status | Actual Time | Notes |
|------|--------|-------------|-------|
| Task 1: XDG helpers | ✅ | ~20 min | All tests pass, 100% coverage, pyright + ruff clean |
| Task 2: RaiseSettings | ✅ | ~25 min | 24 tests pass, 100% coverage, all quality checks pass |
| Task 3: Cascade tests | ✅ | ~30 min | 11 cascade tests, full 5-level precedence verified, TOML support added |
| Task 4: CLI integration | ✅ | ~20 min | 12 CLI tests, settings integrated with ctx.obj, backward compatible |
| Task 5: Documentation | ⬜ | - | - |

**Update this table as tasks progress.**

---

## Notes

### Design Decisions Referenced
- ADR-002: Pydantic for validation (why we use BaseSettings)
- ADR-004: XDG directories (why we follow this standard)

### Assumptions
- Pydantic v2 and pydantic-settings already in pyproject.toml (from F1.1)
- CLI context infrastructure exists from F1.2
- Tests use pytest fixtures (tmp_path, monkeypatch)

### Open Questions
- **Q**: Should we auto-create user config file on first run?
  - **A**: Deferred to "Should Have" - not required for F1.3 completion

---

**Plan Version**: 1.0
**Created**: 2026-01-31
**Ready for Implementation**: Yes
