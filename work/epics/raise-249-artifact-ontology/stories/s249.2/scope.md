# Story Scope: S249.2 — story-plan v1.1 (SDLD Task Blueprints)

> **Epic:** RAISE-249 (Artifact Ontology & Contract Chain)
> **Branch:** `story/s249.2/story-plan-v1.1`
> **Size:** M
> **Contract:** Produces Contract 5 (SDLD Task Blueprints) — consumed by story-implement

---

## In Scope

- Update `/rai-story-plan` SKILL.md to produce SDLD Task Blueprints
- RED/GREEN paired tasks: test task precedes implementation task (TDD)
- Actual function signatures from story-design's Target Interfaces (Contract 4)
- Test specs derived from Gherkin acceptance criteria
- File paths grounded in Gemba Walk findings
- Traceability table: AC → Task mapping
- Depth heuristic by story size (XS=lightweight, S=standard, M+=full blueprint)
- Platform-agnostic code examples from the start (PAT-E-400)

## Out of Scope

- Changes to story-implement (only consumes new format — verify compatibility)
- Changes to any other skill
- CLI code changes (pure skill content / markdown)
- Executable test generation from blueprints (future scope)
- Template engine or code scaffolding from blueprints

## Done Criteria

- [ ] SKILL.md updated with SDLD Task Blueprint format
- [ ] Version bumped to 1.1.0 in metadata
- [ ] RED/GREEN task pairing documented as mandatory pattern
- [ ] Self-test: produce a sample blueprint from S249.1's design output
- [ ] All code examples are multi-language (5+ languages)
- [ ] Traceability table format defined (AC → Tasks)
- [ ] Retrospective complete

---

## Key References

- **Input contract (Contract 4):** S249.1 design output — `work/epics/raise-249-artifact-ontology/stories/s249.1/self-test-contract4.md`
- **Current story-plan:** `.claude/skills/rai-story-plan/SKILL.md`
- **Epic design:** `work/epics/raise-249-artifact-ontology/design.md`

---

*Created: 2026-02-21*
