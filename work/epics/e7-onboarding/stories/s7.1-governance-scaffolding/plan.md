# Implementation Plan: S7.1 Governance Scaffolding CLI

## Overview
- **Story:** S7.1
- **Size:** S
- **Created:** 2026-02-08

## Tasks

### Task 1: Create governance template assets + scaffold function
- **Description:** Create `rai_base/governance/` with parser-compatible markdown templates (prd.md, vision.md, guardrails.md, backlog.md, architecture/system-context.md, architecture/system-design.md). Add `__init__.py` files for importlib.resources. Then add `GovernanceScaffoldResult` model and `scaffold_governance()` function to `onboarding/governance.py` — copies templates via `importlib.resources`, renders `{project_name}`, per-file idempotency (follows bootstrap.py pattern). Unit tests for scaffold function.
- **Files:**
  - `src/raise_cli/rai_base/governance/__init__.py` (create)
  - `src/raise_cli/rai_base/governance/prd.md` (create)
  - `src/raise_cli/rai_base/governance/vision.md` (create)
  - `src/raise_cli/rai_base/governance/guardrails.md` (create)
  - `src/raise_cli/rai_base/governance/backlog.md` (create)
  - `src/raise_cli/rai_base/governance/architecture/__init__.py` (create)
  - `src/raise_cli/rai_base/governance/architecture/system-context.md` (create)
  - `src/raise_cli/rai_base/governance/architecture/system-design.md` (create)
  - `src/raise_cli/onboarding/governance.py` (modify)
  - `tests/test_governance_scaffold.py` (create)
- **TDD Cycle:** RED (test scaffold creates files, renders project_name, skips existing) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/test_governance_scaffold.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: Integrate into init_command + skill recommendation
- **Description:** Call `scaffold_governance()` from `init_command()` after bootstrap/skills, before message output. Add governance result to output messages (Shu: detailed, Ri: concise). Add skill recommendation line based on detected project type: `/project-create` for greenfield, `/project-onboard` for brownfield. Update `_get_project_message()` to include both.
- **Files:**
  - `src/raise_cli/cli/commands/init.py` (modify)
  - `tests/test_init.py` (modify — add assertions for governance scaffolding and skill recommendation)
- **TDD Cycle:** RED (test init produces governance/ and recommends skill) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/test_init.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Integration test (M1 gate) + manual validation
- **Description:** Integration test: `scaffold_governance()` → `raise memory build` → verify governance nodes (requirement, outcome, guardrail) exist in graph. This is the M1 milestone gate from the epic scope. Then manual validation: run `raise init` on a temp directory and verify the full flow.
- **Files:**
  - `tests/test_governance_scaffold.py` (modify — add integration test)
- **TDD Cycle:** RED (test scaffold → build → nodes) → GREEN (fix any template/parser mismatches) → REFACTOR
- **Verification:** `pytest tests/test_governance_scaffold.py::test_scaffold_then_build_produces_nodes -v` + manual `raise init` on temp dir
- **Size:** S
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — foundation (assets + function)
2. Task 2 — integration into CLI (depends on 1)
3. Task 3 — M1 gate validation + manual test (depends on 1, 2)

## Risks
- Template/parser mismatch: mitigated by Task 3 integration test catching it before we move to S7.2

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
