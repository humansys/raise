# Scope: RAISE-243 — rai-skill-create ADR-040 Compliance

> **Branch:** `story/raise-243/adr040-compliance`
> **Parent:** RAISE-242 Skill Ecosystem
> **Context:** E257/ADR-040 established the skill contract after RAISE-243 was originally closed.
>              rai-skill-create was not included in the E257 batch refactor.

---

## In Scope

- Refactor `.claude/skills/rai-skill-create/SKILL.md` to follow ADR-040:
  - 7 fixed sections in order (Purpose, ShuHaRi, Context, Steps, Output, Quality Checklist, References)
  - ≤150 lines total
  - ≤15 discrete rules
  - Replace prose conditionals with decision tables
  - Remove `## Notes` section — move essential content to References or inline
  - Add `## Quality Checklist` section (recency zone — last thing agent reads)
- Fix CLI commands to current ontology:
  - `rai memory build` → `rai graph build`
  - `rai memory query` → `rai graph query`
  - `rai memory context` → `rai graph context`
  - `rai memory add-pattern` → `rai pattern add`
  - `rai memory emit-work` → `rai signal emit-work`
- Preserve Step: index new skill in graph (`rai graph build` + verify with `rai graph query`)
- Validate result: `rai skill validate` passes

## Out of Scope

- Changes to `src/` — this is a pure SKILL.md refactor
- Adding new workflow steps or capabilities
- Changing the frontmatter schema

---

## Done When

- [ ] `rai-skill-create/SKILL.md` ≤150 lines
- [ ] 7 sections exactly (ADR-040 order)
- [ ] No old CLI commands (`rai memory *`)
- [ ] Quality Checklist section present and in recency position
- [ ] Memory indexing step preserved with `rai graph build`
- [ ] `rai skill validate .claude/skills/rai-skill-create/SKILL.md` passes
- [ ] Story committed and merged to epic branch
