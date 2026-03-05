# Retrospective: E354 — Typed Skill Artifacts

> **Date:** 2026-03-03 | **Jira:** RAISE-402

## Objective

Transform skill outputs from free-form Markdown to typed YAML artifacts with Pydantic schema validation, governance-rule semantic linting, knowledge graph ingestion, and generated human-readable docs.

## What was delivered

| Story | What | LOC (approx) | Tests |
|-------|------|:---:|:---:|
| S354.1 | Base artifact model + storage (`models.py`, `writer.py`, `reader.py`) | ~100 | 15 |
| S354.2 | `StoryDesignArtifact` schema + governance validators + type registry | ~120 | 17 |
| S354.3 | Graph ingestion (`load_artifacts()` in GraphBuilder) | ~30 | 5 |
| S354.4 | Doc generation (Markdown template + `renderer.py`) | ~80 | 10 |
| S354.5 | Pilot wiring (`output_type` in SkillMetadata, SKILL.md update) | ~10 | 2 |
| S354.6 | `rai artifact validate` CLI command | ~70 | 7 |
| **Total** | | **~410** | **73** (epic-scoped) |

## Done Criteria — verification

| Criterion | Status |
|-----------|--------|
| `rai-story-design` produces valid `.raise/artifacts/s{N}.{M}-design.yaml` | done (SKILL.md instructs YAML output) |
| Pydantic validates structure, `@model_validator` catches semantic issues | done (empty rationale, AC count bounds) |
| `rai graph build` ingests artifacts as nodes with ref edges | done (`load_artifacts()`) |
| Markdown generated from YAML without information loss | done (template rendering) |
| `raise.output_type` declared in SKILL.md and consumed by system | done (`SkillMetadata.output_type`) |

## What went well

- **Walking skeleton strategy** worked perfectly — each story built on the previous, no rework needed
- **TDD throughout** — caught 4 test regressions in S354.2 when registry changed dispatch behavior, fixed immediately
- **Markdown templates with `str.format()`** (user suggestion) — simpler than Jinja, human-readable templates
- **Parallel stories** S354.3/S354.4 had zero merge conflicts as predicted (different modules)
- **Design decisions held** — all 6 research decisions (D1-D6) and 4 architecture decisions (AD1-AD4) survived implementation unchanged

## What could improve

- **Worktree branch confusion** at epic start — the worktree was on e353's branch, caused file recreation. Ishikawa analysis done, fix deferred.
- **Jira status mapping** case-sensitivity (`Done` vs `done`) caused transition errors — should normalize in adapter
- **No end-to-end integration test** — we test components individually but don't have a test that runs the full skill → YAML → validate → render → graph cycle

## Decisions made

| ID | Decision | Survived? |
|----|----------|:---------:|
| D1 | YAML dense, docs generated | yes |
| D2 | One artifact per skill execution | yes |
| D3 | Incremental migration on demand | yes |
| D4 | Direct graph ingestion | yes |
| D5 | Additive schema evolution | yes |
| D6 | Pilot rollout | yes |
| AD1 | New `src/rai_cli/artifacts/` module | yes |
| AD2 | Pydantic validators as governance rules | yes |
| AD3 | `raise.output_type` in SKILL.md frontmatter | yes |
| AD4 | Replace (not transition) for pilot skill | yes |

## Patterns captured

- CLI commands that validate-and-report follow `gate.py`'s marker + exit code pattern
- `RAI_PROJECT_ROOT` env var enables CLI testability without monkeypatching
- Markdown templates with `str.format()` + `_remove_empty_sections()` is sufficient for artifact doc gen

## Parking lot (future work)

- Governance documents (ADRs, constitution, etc.) migration from Markdown parsing to YAML artifacts — reduces fragility
- E2E integration test for full artifact lifecycle
- `--format table` for `rai artifact validate`
- Remove legacy `stories/` copy once downstream skills migrate to `.raise/artifacts/`
