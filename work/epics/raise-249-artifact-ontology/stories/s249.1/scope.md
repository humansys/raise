## Feature Scope: S249.1 — story-design v1.2

**Epic:** RAISE-249 (Artifact Ontology & Contract Chain)
**Size:** M
**Branch:** `story/s249.1/story-design-v1.2`

### In Scope

- Add Step 2.5 Gemba Walk to rai-story-design SKILL.md (read actual source, map current interfaces)
- Add Step 3.5 Target Interfaces to rai-story-design SKILL.md (function signatures, models, integration points)
- Reposition Gherkin AC: received from story.md (story-start), not generated in design
- Add depth heuristic by story size (XS=skip Gemba, S=skim, M+=full)
- Update story-design output contract to match Contract 4 from epic design.md
- Bump skill version to 1.2.0

### Out of Scope

- Changes to story-plan (that's S2)
- Changes to story-start User Story template (that's S5)
- Changes to epic-* skills (S3, S4)
- CLI code changes (zero code — skill content only)
- Template changes to `.raise/templates/` (deferred, templates follow skills)

### Done Criteria

- [ ] SKILL.md has Gemba Walk step with depth heuristic
- [ ] SKILL.md has Target Interfaces step (signatures, models, integration points)
- [ ] SKILL.md receives Gherkin AC from story.md instead of generating them
- [ ] Output section matches Contract 4 format from epic design.md
- [ ] Version bumped to 1.2.0
- [ ] Changelog entry added
- [ ] Self-test: write a mini-example artifact verifying story-plan could consume it
