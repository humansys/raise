# Implementation Plan: Session Token Protocol

## Overview
- **Story:** RAISE-137
- **Story Points:** 2 SP
- **Story Size:** S (Simple/Moderate)
- **Created:** 2026-02-15

## Tasks

### Task 1: Create ActiveSession Model and Backward Compat Migration
- **Description:** Add `ActiveSession` Pydantic model to profile.py with schema change in `DeveloperProfile` (`current_session` → `active_sessions: list[ActiveSession]`). Implement backward compatibility migration that detects old `current_session` format, converts to `ActiveSession`, and saves.
- **Files:**
  - `src/rai_cli/onboarding/profile.py` (modify)
  - `tests/onboarding/test_profile.py` (modify)
- **TDD Cycle:**
  - **RED:** Write test for `ActiveSession` model validation (session_id, started_at, project, agent). Write test for backward compat migration (load old format, expect migration).
  - **GREEN:** Implement `ActiveSession` model. Add migration logic to `load_developer_profile()`.
  - **REFACTOR:** Extract migration to `_migrate_current_session()` helper if complex.
- **Verification:**
  - `pytest tests/onboarding/test_profile.py::test_active_session_model -v`
  - `pytest tests/onboarding/test_profile.py::test_backward_compat_migration -v`
  - `pyright src/rai_cli/onboarding/profile.py` (0 errors)
- **Size:** M (multiple changes: model, migration, schema)
- **Dependencies:** None

---

### Task 2: Implement resolve_session_id() Function
- **Description:** Create `src/rai_cli/session/resolver.py` with `resolve_session_id(session_flag, env_var) -> str`. Resolution order: `--session` flag > `RAI_SESSION_ID` env var > `RaiSessionNotFoundError`. Normalize both "SES-177" and "177" to "SES-177".
- **Files:**
  - `src/rai_cli/session/resolver.py` (create)
  - `tests/session/test_resolver.py` (create)
  - `src/rai_cli/exceptions.py` (modify — add `RaiSessionNotFoundError` if needed)
- **TDD Cycle:**
  - **RED:** Write tests for: (1) flag present → return normalized, (2) flag missing + env var present → return normalized, (3) both missing → error, (4) normalization ("177" → "SES-177").
  - **GREEN:** Implement `resolve_session_id()` with priority logic and normalization.
  - **REFACTOR:** Extract normalization to `_normalize_session_id()` helper.
- **Verification:**
  - `pytest tests/session/test_resolver.py -v`
  - `pyright src/rai_cli/session/resolver.py` (0 errors)
- **Size:** S (single focused function)
- **Dependencies:** None

---

### Task 3: Add --session and --agent Flags to CLI Commands
- **Description:** Add `--session` flag to `rai session close`. Add `--agent` flag to `rai session start`. Modify `session start` to return session ID in output ("Session SES-NNN started (agent)"). Modify `session close` to use `resolve_session_id()` when `--session` provided.
- **Files:**
  - `src/rai_cli/cli/commands/session.py` (modify)
  - `tests/cli/commands/test_session.py` (modify)
- **TDD Cycle:**
  - **RED:** Write CLI integration test for `rai session start --agent claude-code` (captures output, asserts "Session SES-NNN started"). Write test for `rai session close --session SES-177` (mocks resolver, asserts correct call).
  - **GREEN:** Add `--agent` option to `start()`, update output. Add `--session` option to `close()`, call `resolve_session_id()`.
  - **REFACTOR:** Extract output formatting to helper if needed.
- **Verification:**
  - `pytest tests/cli/commands/test_session.py::test_session_start_with_agent -v`
  - `pytest tests/cli/commands/test_session.py::test_session_close_with_session_flag -v`
  - `pyright src/rai_cli/cli/commands/session.py` (0 errors)
- **Size:** M (multiple commands, output changes)
- **Dependencies:** Task 2 (needs `resolve_session_id()`)

---

### Task 4: Update Session Start/Close to Use active_sessions
- **Description:** Modify `start_session()` and `close_session()` (or equivalent) in profile.py to add/remove from `active_sessions` list instead of setting single `current_session`. Implement `is_stale()` check and warning when starting a session if stale sessions exist.
- **Files:**
  - `src/rai_cli/onboarding/profile.py` (modify)
  - `tests/onboarding/test_profile.py` (modify)
- **TDD Cycle:**
  - **RED:** Write test for `start_session()` adding to `active_sessions`. Write test for `close_session()` removing from list. Write test for stale warning (>24h).
  - **GREEN:** Modify `start_session()` to append `ActiveSession`. Modify close to filter out session. Add stale check.
  - **REFACTOR:** Clean up any now-unused `current_session` references.
- **Verification:**
  - `pytest tests/onboarding/test_profile.py::test_start_adds_to_active_sessions -v`
  - `pytest tests/onboarding/test_profile.py::test_close_removes_from_active_sessions -v`
  - `pytest tests/onboarding/test_profile.py::test_stale_session_warning -v`
  - `pyright src/rai_cli/onboarding/profile.py` (0 errors)
- **Size:** M (list management, stale logic)
- **Dependencies:** Task 1 (needs `ActiveSession` model)

---

### Task 5: Add Session ID to --context Bundle Output
- **Description:** Modify `bundle.py` (or wherever context bundle is assembled) to include the session ID in the output when `--context` flag is used. Format: "Session: SES-NNN" in a visible location (e.g., after "Developer:" line).
- **Files:**
  - `src/rai_cli/session/bundle.py` (modify)
  - `tests/session/test_bundle.py` (modify)
- **TDD Cycle:**
  - **RED:** Write test asserting "Session: SES-177" appears in context bundle output.
  - **GREEN:** Add session ID to bundle assembly logic.
  - **REFACTOR:** Ensure placement doesn't break existing parsers (additive only).
- **Verification:**
  - `pytest tests/session/test_bundle.py::test_session_id_in_context -v`
  - `rai session start --project . --context | grep "Session: SES-"` (manual smoke test)
  - `pyright src/rai_cli/session/bundle.py` (0 errors)
- **Size:** S (single output change)
- **Dependencies:** Task 4 (needs active_sessions to get current session ID)

---

### Task 6 (Final): Manual Integration Test
- **Description:** Validate the session token protocol works end-to-end with running software. Start two sessions in separate terminals, verify each gets unique SES-NNN, close one using `--session` flag, verify context bundle shows session ID, test `RAI_SESSION_ID` env var fallback.
- **Verification:**
  - Terminal 1: `rai session start --project /path/to/project --agent terminal-1` → captures SES-NNN
  - Terminal 2: `rai session start --project /path/to/project --agent terminal-2` → captures SES-MMM (different)
  - Terminal 1: `rai session close --session SES-NNN --project /path/to/project --summary "test"`
  - Terminal 2: `export RAI_SESSION_ID=SES-MMM && rai session close --project /path/to/project --summary "test"` (env var)
  - Check `~/.rai/developer.yaml` — `active_sessions` list reflects operations
  - Test backward compat: manually edit `developer.yaml` to use old `current_session` format, run `rai session start`, verify migration occurs
- **Size:** XS (manual validation)
- **Dependencies:** Tasks 1-5 (all features implemented)

---

## Execution Order

1. **Task 1** (foundation — model + migration)
2. **Task 2** (resolver logic)
3. **Task 3, Task 4** (parallel — CLI flags + profile updates can proceed independently)
4. **Task 5** (context bundle — needs active_sessions from Task 4)
5. **Task 6** (final integration test)

---

## Risks

| Risk | Mitigation |
|------|------------|
| Backward compat migration corrupts existing profiles | Write defensive migration with backup. Test with real `~/.rai/developer.yaml` before merging. |
| Session ID normalization breaks existing data | Accept both "SES-177" and "177" formats. Normalization is additive, doesn't invalidate existing IDs. |
| Context bundle change breaks downstream parsers | Test with `/rai-session-start` skill. Make change additive (append, don't replace). |
| Stale session detection too aggressive (false positives) | Use 24h threshold (industry standard per RES-SESSION-ISO-001). Make threshold configurable later if needed. |

---

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | Model + migration + tests |
| 2 | S | -- | Resolver function + tests |
| 3 | M | -- | CLI flags + output |
| 4 | M | -- | Profile list management |
| 5 | S | -- | Context bundle update |
| 6 | XS | -- | Integration test (manual) |

**Estimated total:** ~2-3 hours (AI-assisted, with TDD overhead)

---

## Acceptance Criteria Mapping

| Criteria | Task(s) |
|----------|---------|
| `rai session start` returns session ID | Task 3 |
| `rai session start` accepts `--agent` flag | Task 3 |
| `rai session close` accepts `--session` flag | Task 3 |
| `resolve_session_id()` with priority resolution | Task 2 |
| `developer.yaml` stores `active_sessions` list | Task 1, 4 |
| `rai session start` adds to `active_sessions` | Task 4 |
| `rai session close` removes from `active_sessions` | Task 4 |
| Backward compat migration | Task 1 |
| Session ID in `--context` output | Task 5 |
| Stale session warning | Task 4 |
| Normalization ("177" → "SES-177") | Task 2 |

All acceptance criteria covered.

---

**Plan complete.** Next: `/rai-story-implement`
