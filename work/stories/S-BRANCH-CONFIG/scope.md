## Story Scope: S-BRANCH-CONFIG

**Origin:** Bugfix — distributed skills hardcode `v2` as development branch, leaking raise-commons's branch model to all users.

**In Scope:**
- Add `branches.development` and `branches.main` to `.raise/manifest.yaml`
- Update `rai init` / onboarding to capture branch config
- Replace hardcoded `v2` in distributed skills with `{dev_branch}` placeholder + instruction to read from manifest
- Update skills: `rai-epic-start`, `rai-epic-close`, `rai-story-close`

**Out of Scope:**
- Dynamic variable substitution in skills (skills are markdown, Rai reads manifest)
- CLI commands that programmatically use branch names (no such commands exist yet)

**Done Criteria:**
- [ ] No hardcoded `v2` branch references in distributed skills
- [ ] manifest.yaml schema includes branch config
- [ ] Onboarding skills capture branch info
- [ ] Tests pass
- [ ] Retrospective complete
