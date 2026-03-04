# Epic Brief: E354 — Typed Skill Artifacts

> **Date:** 2026-03-03
> **Owner:** Emilio Osorio
> **Jira:** [RAISE-402](https://humansys.atlassian.net/browse/RAISE-402)

---

## Hypothesis

If we transform skill outputs from free-form Markdown to typed YAML artifacts with schema validation, governance linting, and graph ingestion, then:
- Rai can consume structured data instead of parsing prose
- Governance rules become automatically verifiable
- Human docs become a generated derivative, not a maintained artifact
- The open-core path (repo YAML → Pro service aggregation) becomes natural

## Success Metrics

| Metric | Target |
|--------|--------|
| Pilot skill (story-design) produces valid typed artifact | End-to-end working |
| Pydantic validates all artifact fields | 100% schema coverage |
| Governance rules catch semantic issues | At least 3 rules active |
| Graph ingestion reads artifacts as nodes | story-design artifacts appear in graph |
| Human docs generated from YAML without loss | Diff test passes |

## Appetite

Medium — 4-6 stories. Pilot with `story-design`, then expand to lifecycle path.
Research phase complete (3 evidence catalogs, 6 decisions locked).

## Rabbit Holes

- Over-engineering the schema before the pilot validates the approach
- Building migration tooling for historical artifacts before proving the new model
- Premature Pro/Enterprise backend work — keep it open-core only for now
- Complex schema versioning — start with additive-only (D5)
