# Epic Scope: RAISE-242 Skill Ecosystem

> **Status**: In Progress
> **Branch**: `epic/raise-242/skill-ecosystem`
> **Base**: `v2`
> **Jira**: [RAISE-242](https://humansys.atlassian.net/browse/RAISE-242)

---

## Objective

Build the meta-skill infrastructure: understand the existing skill ecosystem patterns, then create a skill that generates new skills following those patterns. Validate with a concrete client skill (rai-bugfix).

## Rationale

Skills are RaiSE's primary product capability expansion mechanism. Currently 25+ skills exist but creating new ones requires manual reading of patterns and copy-paste from existing skills. A skill creator standardizes this, reduces errors, and enables consistent quality across the ecosystem.

This epic is "skill of skills" — grounding in how existing skills work is prerequisite to building the creator.

---

## In Scope

- Analyze existing skill patterns (structure, SKILL.md conventions, lifecycle)
- Understand CLI infrastructure (scaffold, validate, check-name, schema)
- Build `rai-skill-create` — interactive skill that generates new skills
- Build `rai-bugfix` — first client skill, validates the creator works
- Skills live in `.claude/skills/` (project-specific, not publishable)

## Out of Scope

- Skill marketplace or distribution → deferred to future epic
- Modifications to `skills_base/` (distributable skills) → separate concern
- CLI scaffold command changes → use existing infrastructure as-is
- Skill versioning or dependency management → premature

---

## Stories

| # | JIRA | Story | Size | Depends On |
|---|------|-------|------|------------|
| 1 | [RAISE-243](https://humansys.atlassian.net/browse/RAISE-243) | `rai-skill-create` — skill creator skill | M | — |
| 2 | [RAISE-244](https://humansys.atlassian.net/browse/RAISE-244) | `rai-bugfix` — systematic bug fixing skill | S | RAISE-243 |

---

## Done When

- [ ] Skill ecosystem patterns documented and understood
- [ ] `rai-skill-create` generates valid skills from conversation
- [ ] `rai-bugfix` created using `rai-skill-create` and works correctly
- [ ] All tests pass, types clean, lint clean
- [ ] Epic retrospective complete
- [ ] Merged to `v2`

---

## Changelog

| Date | Author | Change |
|------|--------|--------|
| 2026-02-20 | Rai | Initial scope |
