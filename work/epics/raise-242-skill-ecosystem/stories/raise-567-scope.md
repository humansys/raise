# Story Scope: RAISE-567 rai-bugfix retrospective improvement

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Branch:** `story/raise-567/bugfix-retrospective`
> **Size:** XS

---

## In Scope

- Add heutagogical checkpoint (4 questions) to rai-bugfix Step 5 (Review)
- Add `rai pattern reinforce` for behavioral patterns to Step 5
- Change `rai pattern add` in Step 5 to use `--scope project`
- Update `retro.md` template structure in Step 5 to include checkpoint + patterns sections
- Update Quality Checklist to include pattern reinforce gate

## Out of Scope

- Changes to any other step (1–4, 6)
- Adding calibration telemetry (`rai signal emit-calibration`) — bugs don't have estimates
- Changes to other skills
- CLI changes

## Done Criteria

- [ ] Step 5 includes heutagogical checkpoint (4 questions, same as rai-story-review Step 2)
- [ ] Step 5 uses `rai pattern add ... --scope project --from RAISE-{N}`
- [ ] Step 5 includes `rai pattern reinforce` with vote table
- [ ] `retro.md` structure documented with checkpoint + patterns sections
- [ ] Quality Checklist updated: "NEVER skip pattern reinforce"
- [ ] `rai skill validate .claude/skills/rai-bugfix/SKILL.md` passes
- [ ] Story retrospective complete
