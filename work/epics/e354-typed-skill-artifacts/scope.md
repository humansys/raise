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

| ID | Story | Size | Depends |
|----|-------|------|---------|
| S354.1 | Base artifact model + storage (SkillArtifact, ArtifactType, reader/writer) | S | — |
| S354.2 | story-design schema + Pydantic governance validators | S | S354.1 |
| S354.3 | Graph ingestion (load_artifacts in GraphBuilder) | S | S354.1 |
| S354.4 | Doc generation (YAML → Markdown renderer) | S | S354.2 |
| S354.5 | Pilot: wire rai-story-design to produce typed artifact | M | S354.2, S354.4 |

S354.3 and S354.4 can run in parallel (independent consumers).

## Done Criteria

1. `rai-story-design` produces a valid `.raise/artifacts/s{N}.{M}-design.yaml`
2. Pydantic validates structure, `@model_validator` catches semantic issues
3. `rai graph build` ingests artifacts as nodes with ref edges
4. Markdown generated from YAML without information loss
5. `raise.output_type` declared in SKILL.md and consumed by system
