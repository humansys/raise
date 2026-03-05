# Story Scope: RAISE-243 rai-skill-create

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Branch:** `story/raise-243/rai-skill-create`
> **Size:** M

---

## In Scope

- SKILL.md for `rai-skill-create` in `.claude/skills/rai-skill-create/`
- Conversational flow: name → check-name → scaffold → fill content → validate
- Reads reference skills by domain for pattern matching
- Uses existing CLI tools (no code changes to `src/`)
- ShuHaRi adaptable (detail level adjusts to experience)

## Out of Scope

- CLI code changes (scaffold.py, validator.py, etc.) → existing infra sufficient
- Automatic distribution to `skills_base/` → separate concern
- Agent-specific adaptations → deferred
- Skill dependency resolution → premature

## Done Criteria

- [ ] `rai-skill-create` SKILL.md exists and passes `rai skill validate`
- [ ] Skill guides user through name validation, scaffolding, content creation
- [ ] Skill reads reference skills to inform generated content
- [ ] Manual test: run the skill to create a test skill successfully
- [ ] Story retrospective complete
