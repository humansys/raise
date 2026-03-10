# Implementation Plan: RAISE-165 — Session Startup Overhead Reduction

## Overview
- **Story:** RAISE-165
- **Size:** S
- **Created:** 2026-02-18
- **Design:** ADR-012 (IDE Context Architecture)

## Tasks

### Task 1: Write consolidated CLAUDE.md
- **Description:** Rewrite CLAUDE.md with 5 sections: Rai Identity (compressed from core.md + perspective.md), Process Rules (from MEMORY.md), Branch Model (from MEMORY.md), CLI Quick Reference (from cli-reference.md in MK-KV compact), File Operations (existing). Add header comment marking it as generated artifact and `/rai-session-start` instruction.
- **Files:** `CLAUDE.md`
- **TDD Cycle:** N/A (content file, no code)
- **Verification:** Manual review — all 5 sections present, line count ≤100, all behavioral primes preserved from source files
- **Size:** S
- **Dependencies:** None

### Task 2: Delete hook and clean up memory dir
- **Description:** Delete `.claude/scripts/session-init.sh`. Replace `~/.claude/projects/-home-emilio-Code-raise-commons/memory/MEMORY.md` with single redirect line. Delete `~/.claude/projects/-home-emilio-Code-raise-commons/memory/cli-reference.md`.
- **Files:** `.claude/scripts/session-init.sh` (delete), `~/.claude/.../memory/MEMORY.md` (replace), `~/.claude/.../memory/cli-reference.md` (delete)
- **TDD Cycle:** N/A (file operations, no code)
- **Verification:** `ls .claude/scripts/session-init.sh` returns not found. `cat ~/.claude/.../memory/MEMORY.md` shows redirect. cli-reference.md gone.
- **Size:** XS
- **Dependencies:** Task 1 (CLAUDE.md must exist before removing old sources)

### Task 3: Remove identity primes from CLI context bundle
- **Description:** In `src/rai_cli/session/bundle.py`: remove `_format_identity_primes` function (lines 222-245) and its call in `assemble_context_bundle` (lines 488-491). Update module docstring to remove "identity primes" reference. In `tests/session/test_bundle.py`: remove `TestFormatIdentityPrimes` class, update `test_full_bundle_contains_all_sections` to assert identity primes are NOT in bundle, remove `_format_identity_primes` from import.
- **Files:** `src/rai_cli/session/bundle.py`, `tests/session/test_bundle.py`
- **TDD Cycle:** RED (update test to assert `"# Identity Primes" not in bundle`) → GREEN (remove function + call) → REFACTOR (clean imports)
- **Verification:** `pytest tests/session/test_bundle.py -v`
- **Size:** S
- **Dependencies:** None (can run in parallel with Task 1-2)

### Task 4: Manual Integration Test
- **Description:** Run `rai session start --project "$(pwd)" --context` and verify: (1) no `# Identity Primes` section in output, (2) `# Governance Primes` still present, (3) `# Behavioral Primes` still present. Then start a new Claude Code conversation on this project and verify: (4) CLAUDE.md loads with all 5 sections visible in system prompt, (5) no hook output appears, (6) Rai identity is primed (values, boundaries visible).
- **Verification:** All 6 checks pass
- **Size:** XS
- **Dependencies:** Tasks 1, 2, 3

## Execution Order
1. Task 3 (Python change — TDD, independent)
2. Task 1 (CLAUDE.md consolidation)
3. Task 2 (cleanup — depends on Task 1)
4. Task 4 (integration test — depends on all)

## Risks
- **MEMORY.md recreation:** Claude Code may recreate MEMORY.md with default content. Mitigation: leave file with redirect content rather than deleting.
- **Behavioral regression:** Compressed identity might miss a prime. Mitigation: checklist comparison of source files vs CLAUDE.md content in Task 1 verification.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
| 3 | S | -- | |
| 4 | XS | -- | Integration test |
