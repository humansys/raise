# Implementation Plan: S16.3 Docs Update Skill

## Overview
- **Story:** S16.3
- **Size:** S (downgraded from M — no CLI command, skill only)
- **Created:** 2026-02-09
- **Revised:** 2026-02-09 (removed CLI command per PAT-172)

## Tasks

### Task 1: `/docs-update` skill definition
- **Description:** Create `.claude/skills/docs-update/SKILL.md` with proper YAML frontmatter (name, description, metadata tags). Skill steps: (1) run `raise memory build` for fresh graph + diff, (2) read last-diff.json to identify affected modules (fall back to all if no diff), (3) for each module run `raise memory context mod-X --format json` to get graph truth, (4) read current module doc frontmatter, (5) compare machine-owned fields (depends_on, depended_by, components, public_api) and show diffs, (6) HITL gate before applying frontmatter changes, (7) if structural changes detected, propose narrative updates with separate HITL gate.
- **Files:** `.claude/skills/docs-update/SKILL.md`
- **TDD Cycle:** N/A (skill is a prompt file — validate by `raise skill validate`)
- **Verification:** `uv run raise skill validate docs-update` + manual review
- **Size:** S
- **Dependencies:** None

### Task 2: Manual integration test
- **Description:** Invoke `/docs-update` against real raise-commons project. Verify it builds graph, identifies module drift, shows correct before/after diffs, and applies changes with HITL gate. Check that human-owned fields are untouched.
- **Verification:** Demo the skill working end-to-end on real project data
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1 — skill definition
2. Task 2 — integration test (final validation)

## Risks
- **Graph data completeness:** `raise memory context` may not expose all needed fields (e.g., `depended_by` not in JSON output). Mitigation: verify JSON shape before writing skill steps; if missing, read index.json directly.
- **Frontmatter editing precision:** Skill uses Edit tool on YAML frontmatter — need clear instructions to preserve field order and not corrupt markdown body. Mitigation: skill instructions specify exact edit boundaries (between `---` delimiters only).

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | Integration test |
