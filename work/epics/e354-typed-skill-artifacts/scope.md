# Epic Scope: E354 — Typed Skill Artifacts

> **Date:** 2026-03-03
> **Branch:** `epic/e354/typed-skill-artifacts`
> **Jira:** [RAISE-402](https://humansys.atlassian.net/browse/RAISE-402)

---

## Objective

Transform skill outputs from free-form Markdown to typed YAML artifacts with Pydantic schema validation, governance-rule semantic linting, knowledge graph ingestion, and generated human-readable docs.

## Design Decisions (Locked)

| ID | Decision | Reference |
|----|----------|-----------|
| D1 | YAML denso, docs humanos generados | `work/research/skill-artifacts/decisions.md` |
| D2 | Un artefacto por ejecución de skill | |
| D3 | Migración incremental bajo demanda | |
| D4 | Ingesta directa al grafo | |
| D5 | Schema evolution aditivo (backward-compatible only) | |
| D6 | Rollout piloto → path crítico | |
| AD1 | New `src/rai_cli/artifacts/` module | `design.md` |
| AD2 | Pydantic validators as governance rules (no engine) | `design.md` |
| AD3 | `raise.output_type` in SKILL.md frontmatter | `design.md` |
| AD4 | Replace (not transition) for pilot skill | `design.md` |

## In Scope (MUST)

- Pydantic base model for skill artifacts (common fields)
- `story-design` artifact schema (pilot type)
- Validation pipeline: schema → Pydantic validators → refs → write
- Graph ingestion of `.raise/artifacts/*.yaml`
- Human doc generation from YAML (Markdown)
- Storage layout: `.raise/artifacts/`
- Skill SKILL.md `raise.output_type` declaration
- Pilot: `rai-story-design` replaces Markdown with YAML artifact

## Out of Scope

- Migration tooling for `work/epics/` historical artifacts
- Pro/Enterprise backend or `rai login`
- All artifact types beyond `story-design` (future epics expand)
- Confluence publishing of generated docs
- Cross-repo pattern aggregation
- `.raise/schemas/` JSON Schema export (nice-to-have, not blocking)

## Stories

| ID | Jira | Story | Size | Depends |
|----|------|-------|------|---------|
| S354.1 | [RAISE-418](https://humansys.atlassian.net/browse/RAISE-418) | Base artifact model + storage | S | — |
| S354.2 | [RAISE-419](https://humansys.atlassian.net/browse/RAISE-419) | story-design schema + governance validators | S | S354.1 |
| S354.3 | [RAISE-420](https://humansys.atlassian.net/browse/RAISE-420) | Graph ingestion (load_artifacts in GraphBuilder) | S | S354.1 |
| S354.4 | [RAISE-421](https://humansys.atlassian.net/browse/RAISE-421) | Doc generation (YAML → Markdown renderer) | S | S354.2 |
| S354.5 | [RAISE-422](https://humansys.atlassian.net/browse/RAISE-422) | Pilot: wire rai-story-design to produce typed artifact | M | S354.2, S354.4 |
| S354.6 | [RAISE-423](https://humansys.atlassian.net/browse/RAISE-423) | `rai artifact validate` CLI command | S | S354.2 |

S354.3 and S354.4 can run in parallel (independent consumers).

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Build the minimal E2E path first (model → schema → docs → pilot), with graph ingestion as a parallel track.

### Execution Order

| # | Story | Rationale | Enables |
|---|-------|-----------|---------|
| 1 | S354.1 — Base model + storage | Foundation — all stories depend on this | S354.2, S354.3 |
| 2 | S354.2 — story-design schema | First real artifact type, proves the model | S354.4, S354.5 |
| 3-4 | S354.3 — Graph ingestion | Independent consumer, parallel with S354.4 | — |
| 3-4 | S354.4 — Doc generation | Independent consumer, parallel with S354.3 | S354.5 |
| 5 | S354.5 — Pilot wiring | E2E integration, closes the loop | Epic done |

Critical path: S354.1 → S354.2 → S354.4 → S354.5

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|-----------------|
| **M1: Schema validates** | S354.1, S354.2 | Create `StoryDesignArtifact` in Python, write YAML to `.raise/artifacts/`, read back, Pydantic validates. Tests pass. |
| **M2: Consumers work** | S354.3, S354.4 | `rai graph build` shows artifact nodes. Markdown generated from YAML matches content. |
| **M3: E2E pilot** | S354.5 | `rai-story-design` produces YAML artifact end-to-end: validated, ingested, docs generated. |

### Progress Tracking

| Story | Status | Milestone |
|-------|--------|-----------|
| S354.1 Base model + storage | done | M1 |
| S354.2 story-design schema | done | M1 |
| S354.3 Graph ingestion | done | M2 |
| S354.4 Doc generation | done | M2 |
| S354.5 Pilot wiring | in progress | M3 |
| S354.6 rai artifact validate | pending | M3 |

### Sequencing Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Base model needs rework after schema story reveals missing fields | Schedule slip | S354.1 design validates against 3+ historical story-designs before implementation |
| Parallel stories (S354.3/S354.4) create merge conflicts | Minor rework | Different modules, minimal overlap. Resolve at M2. |
| Pilot wiring scope larger than expected (skill rewrite) | M → L story | Timeboxed: if SKILL.md changes exceed output section, split into sub-tasks |

## Done Criteria

1. `rai-story-design` produces a valid `.raise/artifacts/s{N}.{M}-design.yaml`
2. Pydantic validates structure, `@model_validator` catches semantic issues
3. `rai graph build` ingests artifacts as nodes with ref edges
4. Markdown generated from YAML without information loss
5. `raise.output_type` declared in SKILL.md and consumed by system
