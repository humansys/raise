# Story Scope: S249.3 — epic-start v1.1 (Epic Brief Artifact)

> **Epic:** RAISE-249 (Artifact Ontology & Contract Chain)
> **Size:** S
> **Branch:** epic/raise-249/artifact-ontology (S-sized, no story branch)

---

## In Scope

- Add Step 3.5 to `rai-epic-start/SKILL.md`: produce Epic Brief artifact in SAFe hypothesis + Shape Up format
- Artifact location: `work/epics/{epic-id}/brief.md`
- Artifact format: Contract 1 from epic `design.md` (YAML frontmatter + Hypothesis + Metrics + Appetite + Scope Boundaries)
- epic-design receives the brief as structured input instead of building from scratch
- Platform-agnostic (PAT-E-400)
- Version bump

## Out of Scope

- Changes to epic-design (S4 handles that)
- Changes to any other skill
- CLI code changes
- Template changes in `.raise/templates/`

## Done Criteria

- [ ] SKILL.md updated with Step 3.5 (Epic Brief artifact generation)
- [ ] Contract 1 format documented in the step
- [ ] Version bumped in frontmatter
- [ ] Self-test: write a mini Epic Brief artifact and verify epic-design could consume it
- [ ] Retrospective complete
