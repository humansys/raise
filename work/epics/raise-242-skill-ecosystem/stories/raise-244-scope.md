# Story Scope: RAISE-244 rai-bugfix

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Branch:** `epic/raise-242/skill-ecosystem` (S size — stays on epic branch)
> **Size:** S

---

## In Scope

- Run `rai-skill-create` to generate `rai-bugfix` skill in `.claude/skills/rai-bugfix/`
- `rai-bugfix` SKILL.md with systematic bug fixing workflow (reproduce → analyse → fix → test → commit → close)
- Validate result with `rai skill validate`
- Document any friction or gaps discovered in `rai-skill-create` during E2E run

## Out of Scope

- Changes to `rai-skill-create` (RAISE-243 is closed; only document findings)
- Automated test infrastructure for skills → separate concern
- Integrating `rai-bugfix` with external issue trackers → future story

## Done Criteria

- [ ] `rai-bugfix` SKILL.md exists at `.claude/skills/rai-bugfix/SKILL.md`
- [ ] `rai skill validate .claude/skills/rai-bugfix/SKILL.md` passes with no errors
- [ ] Skill content covers the full bug fix lifecycle (reproduce, analyse, fix, test, commit, close)
- [ ] `rai-skill-create` E2E worked without errors or workarounds (or friction documented as patterns)
- [ ] Story retrospective complete
