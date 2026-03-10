# Implementation Plan: RAISE-235 — Skill Sync on Upgrade

## Overview
- **Story:** RAISE-235
- **Feature Size:** M (5-8 SP)
- **Created:** 2026-02-20
- **Design:** `design.md` (10 decisions, dpkg three-hash + manifest)

## Tasks

### Task 1: Skill Manifest — Pydantic Models + Load/Save

- **Description:** Create `skill_manifest.py` with Pydantic models for the skills manifest (`SkillManifest`, `SkillEntry`) and load/save functions. Add `MANIFESTS_DIR` constant to `paths.py`.
- **Files:**
  - Create: `src/rai_cli/onboarding/skill_manifest.py`
  - Modify: `src/rai_cli/config/paths.py` (add constant)
  - Create: `tests/onboarding/test_skill_manifest.py`
- **TDD Cycle:**
  - RED: Test `SkillEntry` model validation, `save_skill_manifest`, `load_skill_manifest`, missing file returns empty manifest, corrupt file returns empty manifest
  - GREEN: Implement models + JSON persistence to `.raise/manifests/skills.json`
  - REFACTOR: Ensure Pydantic strict types
- **Verification:** `pytest tests/onboarding/test_skill_manifest.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Hash Computation Utility

- **Description:** Add `compute_file_hash()` and `compute_content_hash()` helpers to `skill_manifest.py`. SHA256, returns hex digest string.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skill_manifest.py`
  - Modify: `tests/onboarding/test_skill_manifest.py`
- **TDD Cycle:**
  - RED: Test hash of known content, hash of file on disk, deterministic output
  - GREEN: `hashlib.sha256` wrapper
  - REFACTOR: —
- **Verification:** `pytest tests/onboarding/test_skill_manifest.py -v`
- **Size:** XS
- **Dependencies:** Task 1

### Task 3: Three-Hash Detection Logic

- **Description:** Implement `classify_skill()` function that takes (hash_distributed, hash_on_disk, hash_new) and returns a `SkillSyncAction` enum: `CURRENT`, `AUTO_UPDATE`, `KEEP_USER`, `CONFLICT`, `NEW`, `LEGACY_FIRST_ENCOUNTER`. This is the pure dpkg algorithm — no I/O, fully testable.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skill_manifest.py`
  - Modify: `tests/onboarding/test_skill_manifest.py`
- **TDD Cycle:**
  - RED: Test all 6 states from the decision matrix (design.md D2). Test legacy case (hash_distributed=None). Test edge: all three hashes equal.
  - GREEN: Implement enum + classifier function
  - REFACTOR: —
- **Verification:** `pytest tests/onboarding/test_skill_manifest.py -v`
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Update SkillScaffoldResult Model

- **Description:** Add new fields to `SkillScaffoldResult`: `skills_updated`, `skills_conflicted`, `skills_kept`, `skills_overwritten`, `skills_current`. Keep backward-compat fields.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skills.py`
  - Modify: `tests/onboarding/test_skills.py`
- **TDD Cycle:**
  - RED: Test new fields exist with defaults, old fields still work
  - GREEN: Add fields to model
  - REFACTOR: —
- **Verification:** `pytest tests/onboarding/test_skills.py -v`
- **Size:** XS
- **Dependencies:** None (parallel with Tasks 1-3)

### Task 5: Refactor scaffold_skills() with Manifest + Detection

- **Description:** Core change. Replace the "skip if exists" logic with three-hash detection. On first run: install + record in manifest. On subsequent runs: classify each skill, auto-update untouched files, skip customized. Write manifest after every run. Handle legacy projects (no manifest). Non-interactive mode only (no conflict prompts yet — conflicts default to keep).
- **Files:**
  - Modify: `src/rai_cli/onboarding/skills.py`
  - Modify: `tests/onboarding/test_skills.py`
- **TDD Cycle:**
  - RED: Test fresh install writes manifest. Test second run with no changes = all current. Test upstream update + untouched file = auto-update. Test upstream update + customized file = keep (default). Test new skill added in newer version = installed. Test legacy project without manifest = conservative.
  - GREEN: Rewrite `scaffold_skills()` core loop using `classify_skill()` + manifest
  - REFACTOR: Extract helper functions if loop gets complex
- **Verification:** `pytest tests/onboarding/test_skills.py -v && pyright src/rai_cli/onboarding/skills.py`
- **Size:** L
- **Dependencies:** Tasks 1, 2, 3, 4

### Task 6: Interactive Conflict Resolution (TTY)

- **Description:** Implement `prompt_skill_conflict()` function that shows diff and prompts user for action (keep/overwrite/diff/backup+overwrite/keep-all/overwrite-all). Uses `sys.stdin.isatty()` to detect TTY. Non-TTY defaults to keep.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skills.py`
  - Create: `tests/onboarding/test_skill_conflict.py`
- **TDD Cycle:**
  - RED: Test non-TTY returns keep. Test each action option (mock input). Test "keep-all" and "overwrite-all" batch shortcuts. Test diff output format.
  - GREEN: Implement prompt with `input()` + diff via `difflib.unified_diff`
  - REFACTOR: —
- **Verification:** `pytest tests/onboarding/test_skill_conflict.py -v`
- **Size:** M
- **Dependencies:** Task 5

### Task 7: Wire Conflict Resolution into scaffold_skills()

- **Description:** Connect `prompt_skill_conflict()` to the `CONFLICT` case in `scaffold_skills()`. Track batch state (keep-all / overwrite-all) across the loop. Update manifest based on user's choice.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skills.py`
  - Modify: `tests/onboarding/test_skills.py`
- **TDD Cycle:**
  - RED: Test conflict + user chooses overwrite = file updated + manifest updated. Test conflict + user chooses keep = file preserved. Test conflict + backup = .bak created + file updated. Test overwrite-all applies to remaining conflicts.
  - GREEN: Wire prompt into scaffold loop
  - REFACTOR: —
- **Verification:** `pytest tests/onboarding/test_skills.py -v`
- **Size:** S
- **Dependencies:** Task 6

### Task 8: CLI Flags (--dry-run, --force, --skip-updates)

- **Description:** Add three flags to `rai init` command. Pass them through to `scaffold_skills()`. `--dry-run` prints summary table and exits. `--force` overrides all conflicts. `--skip-updates` keeps all existing files (legacy behavior).
- **Files:**
  - Modify: `src/rai_cli/cli/commands/init.py`
  - Modify: `src/rai_cli/onboarding/skills.py` (add params to signature)
  - Create: `tests/cli/commands/test_init_skill_sync.py`
- **TDD Cycle:**
  - RED: Test --dry-run produces table output, doesn't write files. Test --force overwrites all. Test --skip-updates keeps all. Test flags are mutually exclusive where needed.
  - GREEN: Add typer options, pass to scaffold_skills
  - REFACTOR: —
- **Verification:** `pytest tests/cli/commands/test_init_skill_sync.py -v`
- **Size:** M
- **Dependencies:** Task 7

### Task 9: Dry-Run Output Formatter

- **Description:** Implement the dry-run summary table: skill name, status (new/updated/conflict/current/unmanaged), proposed action. Return exit code 0 (all current) or 1 (updates available). Use rich or simple formatting based on TTY.
- **Files:**
  - Modify: `src/rai_cli/onboarding/skills.py`
  - Modify: `tests/cli/commands/test_init_skill_sync.py`
- **TDD Cycle:**
  - RED: Test table output contains expected skill names and statuses. Test exit code 0 when current. Test exit code 1 when updates available.
  - GREEN: Format table from SkillScaffoldResult
  - REFACTOR: —
- **Verification:** `pytest tests/cli/commands/test_init_skill_sync.py -v`
- **Size:** S
- **Dependencies:** Task 8

### Task 10: Quality Gates + Existing Test Compat

- **Description:** Run full test suite, pyright, ruff. Fix any regressions in existing `test_skills.py` tests. Ensure backward compatibility of `SkillScaffoldResult` old fields.
- **Files:**
  - Modify: `tests/onboarding/test_skills.py` (adapt existing tests if needed)
  - Any files with type errors or lint issues
- **TDD Cycle:** N/A — verification pass
- **Verification:** `pytest && pyright && ruff check src/`
- **Size:** S
- **Dependencies:** Tasks 1-9

### Task 11 (Final): Manual Integration Test

- **Description:** Validate end-to-end on this project:
  1. Run `rai init --dry-run` — verify output shows skill statuses
  2. Modify one skill, run `rai init` — verify it detects customization and keeps it
  3. Run `rai init --force` — verify it overwrites
  4. Verify `.raise/manifests/skills.json` exists with correct content
  5. Verify non-TTY behavior (pipe to cat)
- **Verification:** Demo the story working interactively
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
Task 1 (manifest models)        Task 4 (result model update)
      ↓                               ↓
Task 2 (hash utils)                   |
      ↓                               |
Task 3 (detection logic)              |
      ↓                               ↓
Task 5 (core refactor) ←─────────────┘
      ↓
Task 6 (conflict prompt)
      ↓
Task 7 (wire conflict into scaffold)
      ↓
Task 8 (CLI flags)
      ↓
Task 9 (dry-run formatter)
      ↓
Task 10 (quality gates)
      ↓
Task 11 (manual integration test)
```

Tasks 1-3 and Task 4 can run in parallel. Everything else is sequential.

## Risks

| Risk | Mitigation |
|------|------------|
| Existing tests break when scaffold_skills behavior changes | Task 10 dedicated to fixing regressions |
| Plugin transforms complicate hash computation | Hash post-transform content (already in design D3) |
| Interactive prompts hard to test | Mock `input()` and `sys.stdin.isatty()` |
| init.py has complex multi-agent loop | Only modify the skill scaffolding call site, not the agent loop |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 — Manifest models | S | -- | |
| 2 — Hash utils | XS | -- | |
| 3 — Detection logic | S | -- | |
| 4 — Result model | XS | -- | |
| 5 — Core refactor | L | -- | Highest risk |
| 6 — Conflict prompt | M | -- | |
| 7 — Wire conflict | S | -- | |
| 8 — CLI flags | M | -- | |
| 9 — Dry-run formatter | S | -- | |
| 10 — Quality gates | S | -- | |
| 11 — Integration test | XS | -- | |
