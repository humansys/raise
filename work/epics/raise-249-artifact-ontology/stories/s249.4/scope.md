## Feature Scope: S249.4

**Story:** epic-design v1.2 — Separate scope.md / design.md artifacts
**Size:** S
**Branch:** epic/raise-249/artifact-ontology (S-sized, skip story branch)

**In Scope:**
- Update `rai-epic-design/SKILL.md` to produce TWO artifacts: `scope.md` (what/why) and `design.md` (how/interfaces)
- Add Contract 2 output format from epic design.md § Contract 2
- Version bump to 1.2.0
- Changelog entry

**Out of Scope:**
- Changing epic-plan (consumer of scope.md — orthogonal)
- CLI code changes
- Template changes in `.raise/templates/`

**Done Criteria:**
- [ ] SKILL.md produces scope.md (WHAT/WHY) and design.md (HOW/interfaces)
- [ ] Contract 2 format documented in skill output section
- [ ] Version 1.2.0 in metadata
- [ ] Self-test: verify epic-plan could consume scope.md, story-design could consume design.md
- [ ] Retrospective complete
