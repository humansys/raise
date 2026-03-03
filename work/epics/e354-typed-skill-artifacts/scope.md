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

## In Scope

- Pydantic base model for skill artifacts (common fields)
- `story-design` artifact schema (pilot type)
- Validation pipeline: schema → governance → refs → write
- Graph ingestion of `.raise/artifacts/*.yaml`
- Human doc generation from YAML (Markdown)
- Storage layout: `.raise/artifacts/`, `.raise/schemas/`
- Skill SKILL.md `output_type` declaration pattern

## Out of Scope

- Migration tooling for `work/epics/` historical artifacts
- Pro/Enterprise backend or `rai login`
- All artifact types beyond `story-design` (future epics expand)
- Confluence publishing of generated docs
- Cross-repo pattern aggregation

## Planned Stories (Tentative)

1. Base artifact model + storage layout
2. `story-design` schema + validation
3. Governance semantic linting rules
4. Graph ingestion pipeline
5. Human doc generation
6. Pilot: wire `rai-story-design` skill to produce typed artifact

## Done Criteria

- `rai-story-design` produces a valid `.raise/artifacts/s{N}.{M}-design.yaml`
- Pydantic validates structure, governance rules validate content
- `rai graph build` ingests artifacts as nodes with ref edges
- Human-readable Markdown generated from artifact without information loss
