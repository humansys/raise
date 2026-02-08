# Implementation Plan: Architecture Knowledge Layer

## Overview
- **Story:** discover-describe
- **Story Points:** 5 SP (revised down from 8 — CLI command removed)
- **Size:** M (4 tasks, skill-driven approach)
- **Created:** 2026-02-07
- **Revised:** 2026-02-08 — Removed CLI command + describer module. Architecture docs are AI-synthesized via skill, not templated by CLI. Rationale: deterministic templates produce shallow docs; a new contributor needs real explanations. The CLI stays deterministic where it matters (graph building, querying). Documentation generation is a skill — an AI-assisted activity.
- **Design:** `work/stories/discover-document/design.md`
- **Research:** `work/research/architecture-knowledge-layer/`

## Design Deviation

The original design specified a `raise discover describe` CLI command with a `describer.py` module. After review, we determined:

1. **The CLI command adds no meaningful value** — architecture docs are generated infrequently and benefit from AI prose synthesis, not template assembly
2. **Useful onboarding docs need genuine explanations** — a new developer needs to understand *why* modules exist and *how* they fit, not just see dependency tables
3. **Inference economy is served better** — the skill reads JSON files directly and synthesizes rich docs, avoiding a CLI intermediary that would produce shallow output

**What stays:** Schema extension (Task 1), graph builder integration (Task 2) — both deterministic, both CLI-useful.
**What changes:** The `/discover-describe` skill generates docs directly (Task 3), no `describer.py` or CLI command.

## Tasks

### Task 1: Extend Graph Schema (module + depends_on)

- **Description:** Add `module` to NodeType and `depends_on` to EdgeType in context/models.py. This is the foundation — the graph must represent module-level knowledge and inter-module dependencies.
- **Files:**
  - `src/raise_cli/context/models.py` — Add to Literal types
  - `tests/context/test_models.py` — Test new types are valid
- **TDD Cycle:** RED (test module node creation) → GREEN (add to Literal) → REFACTOR
- **Verification:** `pytest tests/context/ -x -q`
- **Size:** XS
- **Dependencies:** None

### Task 2: Graph Builder — Architecture Doc Extraction

- **Description:** Extend UnifiedGraphBuilder with `load_architecture()` method that parses `governance/architecture/modules/*.md` YAML frontmatter and creates `module` nodes with `depends_on` edges in the unified graph. Wire into `build()` pipeline.
- **Files:**
  - `src/raise_cli/context/builder.py` — Add `load_architecture()` method
  - `tests/context/test_builder.py` — Test module nodes and depends_on edges appear in graph
- **TDD Cycle:**
  - RED: Test graph contains module nodes after build with fixture arch docs
  - GREEN: Implement YAML frontmatter parsing + node/edge creation
  - RED: Test depends_on edges are created between modules
  - GREEN: Wire edge creation from frontmatter `depends_on` field
- **Verification:** `pytest tests/context/test_builder.py -x -q -k module`
- **Size:** M
- **Dependencies:** Task 1 (needs NodeType/EdgeType)

### Task 3: Create `/discover-describe` Skill + Generate Docs

- **Description:** Create the skill file at `.claude/skills/discover-describe/SKILL.md` that orchestrates architecture doc generation. Then immediately dogfood: run the skill on raise-commons to generate `governance/architecture/` docs. The skill reads `work/discovery/components-validated.json`, analyzes source tree structure and imports, and produces:
  - `governance/architecture/index.md` — compact index (<2K tokens)
  - `governance/architecture/modules/*.md` — per-module docs with YAML frontmatter + rich prose
- **Files:**
  - `.claude/skills/discover-describe/SKILL.md` — Create
  - `governance/architecture/index.md` — Generated
  - `governance/architecture/modules/*.md` — Generated (~11 files)
- **Verification:**
  - All modules documented with genuine explanatory prose
  - YAML frontmatter is valid (type, name, purpose, depends_on, depended_by, components)
  - Compact index under 2K tokens
  - A new developer reading the docs would understand module purpose and relationships
- **Size:** L
- **Dependencies:** Task 1 (frontmatter uses module type vocabulary)

### Task 4: Integration Verification

- **Description:** End-to-end validation: rebuild graph with architecture docs, verify module nodes and depends_on edges appear, verify queries return module relationships.
- **Verification:**
  - `raise memory build` succeeds with module nodes in graph
  - `raise memory query "discovery dependencies"` returns module relationships
  - All tests pass: `pytest --cov=src --cov-fail-under=90`
  - Linting clean: `ruff check . && ruff format --check .`
  - Type check clean: `pyright --strict src/`
- **Size:** S
- **Dependencies:** Tasks 2, 3

## Execution Order

```
Task 1 (XS) — Schema extension
    ↓
Task 2 (M) ──┬── Task 3 (L)   ← parallel after Task 1
              ↓
         Task 4 (S) — Integration verification
```

1. **Task 1** — Foundation (schema)
2. **Tasks 2 + 3** — Can start in parallel (graph builder + skill/docs are independent)
3. **Task 4** — Integration validates everything together

## Risks

| Risk | Mitigation |
|------|------------|
| Schema change breaks existing graphs | PAT-152: rebuild graph after schema change. Include in Task 4. |
| AI-generated docs are inaccurate | Dogfood immediately (Task 3); human reviews output before commit |
| YAML frontmatter format inconsistency | Define schema in skill; validate in graph builder |
| Compact index exceeds 2K tokens | Module map table is the core — terse purpose descriptions |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | XS | -- | |
| 2 | M | -- | Graph builder integration |
| 3 | L | -- | Skill + dogfood (core work) |
| 4 | S | -- | Integration verification |
