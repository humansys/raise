# Implementation Plan: S16.3 Docs Update Skill

## Overview
- **Story:** S16.3
- **Size:** M
- **Created:** 2026-02-09

## Tasks

### Task 1: Domain module — docs updater with Pydantic models
- **Description:** Create `src/raise_cli/docs/` module with the core updater logic. Define Pydantic models (`FrontmatterDiff`, `ModuleUpdate`, `UpdateResult`). Implement `compute_updates()` that takes a `UnifiedGraph` and module doc paths, reads current frontmatter, compares against graph truth (`code_imports` → `depends_on`, reverse edges → `depended_by`, `code_exports` → `public_api`, `code_components` → `components`), and returns a list of `ModuleUpdate` with per-field diffs. Implement `apply_updates()` that rewrites frontmatter YAML in module docs preserving field order. Does NOT touch human-owned fields (`constraints`, `status`, `purpose`).
- **Files:** `src/raise_cli/docs/__init__.py`, `src/raise_cli/docs/models.py`, `src/raise_cli/docs/updater.py`
- **TDD Cycle:** RED (test compute_updates with known graph vs doc mismatch) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/test_docs_updater.py`
- **Size:** M
- **Dependencies:** None

### Task 2: CLI command — `raise docs update`
- **Description:** Create `src/raise_cli/cli/commands/docs.py` with a `docs_app` Typer sub-app. Add `update` command with `--dry-run`, `--modules`, and `--index` flags. Thin wrapper: loads graph from index, calls `compute_updates()`, either prints diff (dry-run) or calls `apply_updates()`. Register `docs_app` in `main.py`.
- **Files:** `src/raise_cli/cli/commands/docs.py`, `src/raise_cli/cli/main.py`
- **TDD Cycle:** RED (test CLI invocation with --dry-run shows diffs) → GREEN (implement) → REFACTOR
- **Verification:** `pytest tests/test_docs_cli.py`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: `/docs-update` skill definition
- **Description:** Create `.claude/skills/docs-update/SKILL.md` with proper YAML frontmatter (name, description, metadata tags). Skill steps: (1) run `raise memory build` for fresh graph + diff, (2) run `raise docs update --dry-run` to preview, (3) run `raise docs update` to apply frontmatter, (4) if diff shows structural changes, read affected module docs and propose narrative updates with inference, (5) HITL gate before writing narrative changes. Register in `.claude/settings.local.json` if needed.
- **Files:** `.claude/skills/docs-update/SKILL.md`
- **TDD Cycle:** N/A (skill is a prompt file, not code — validate by inspection)
- **Verification:** `uv run raise skill validate docs-update` + manual review of skill content
- **Size:** S
- **Dependencies:** Task 2

### Task 4: Manual Integration Test
- **Description:** Run `raise memory build` then `raise docs update --dry-run` against the real raise-commons project. Verify it detects real drift between graph truth and current module doc frontmatter. Apply updates, inspect results. Then invoke `/docs-update` skill to verify the full orchestrated flow.
- **Verification:** Demo the command working end-to-end on real project data
- **Size:** XS
- **Dependencies:** Tasks 1-3

## Execution Order
1. Task 1 — domain logic (foundation)
2. Task 2 — CLI command (depends on T1)
3. Task 3 — skill definition (depends on T2)
4. Task 4 — integration test (final validation)

## Risks
- **YAML frontmatter rewriting:** Preserving field order and comments when rewriting. Mitigation: use `ruamel.yaml` or manual string manipulation for frontmatter-only rewrite (avoid full parse/dump cycle that reorders fields).
- **`depended_by` computation:** Currently declared manually in frontmatter. Need to compute from reverse `depends_on` edges in graph. Mitigation: graph already has `depends_on` edges — just reverse them.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | XS | -- | Integration test |
