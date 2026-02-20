## Feature Scope: RAISE-235

**Summary:** `rai init` updates existing skills when a newer rai-cli version is detected.

**In Scope:**
- Version-aware skill sync during `rai init` (compare bundled vs project skill versions)
- Track installed skill package version in `.raise/` metadata
- Update only changed skills (not blanket overwrite)
- Report updated/skipped/customized skills in `SkillScaffoldResult`
- Respect customized skills (warn + skip, not silent overwrite)

**Out of Scope:**
- Dedicated `rai skill sync` subcommand (future, if needed)
- `rai: framework/custom` frontmatter ownership semantics (ADR-038, parking lot)
- Skill extension hooks (parking lot SES-224)
- Backup/rollback of overwritten skills

**Done Criteria:**
- [ ] Running `rai init` after upgrading `rai-cli` updates stale skills
- [ ] Customized skills are not silently overwritten
- [ ] `SkillScaffoldResult` reports updated skills separately
- [ ] Tests cover upgrade scenario (old version → new version)
- [ ] Tests pass, types pass, lint passes
- [ ] Retrospective complete
