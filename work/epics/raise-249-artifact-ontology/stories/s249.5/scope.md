# Story Scope: S249.5 — story-start v1.1 (User Story Artifact)

> **Epic:** RAISE-249 (Artifact Ontology & Contract Chain)
> **Size:** S
> **Branch:** epic/raise-249/artifact-ontology (S-sized, no story branch)

---

## In Scope

- Add Step 5.5 to `rai-story-start/SKILL.md`: produce User Story artifact in Connextra + Gherkin + SbE format
- Artifact location: `work/epics/{epic-id}/stories/{story-id}/story.md`
- Artifact format: Contract 3 from epic `design.md` (YAML frontmatter + Connextra + Gherkin scenarios + SbE table)
- story-design receives Gherkin AC from story.md instead of generating them
- Depth heuristic: XS stories can use informal AC (skip Gherkin ceremony)
- Platform-agnostic examples (PAT-E-400): code examples in language-neutral or multi-language form
- Version bump to 1.3.0

## Out of Scope

- Changes to story-design (S1 already done — it already references story.md for AC)
- Changes to any other skill
- CLI code changes
- Template changes in `.raise/templates/`
- Executable Gherkin (we're not building a test runner)

## Done Criteria

- [ ] SKILL.md updated with Step 5.5 (User Story artifact generation)
- [ ] Contract 3 format documented in the step
- [ ] Depth heuristic for story size (XS=informal, S+=Gherkin)
- [ ] Version bumped to 1.3.0 in frontmatter
- [ ] Self-test: write a mini User Story artifact and verify story-design could consume it
- [ ] Retrospective complete
