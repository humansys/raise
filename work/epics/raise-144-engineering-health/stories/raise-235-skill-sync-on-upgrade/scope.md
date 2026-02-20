## Feature Scope: RAISE-235

**Summary:** `rai init` updates existing skills when a newer rai-cli version is detected, using a SHA256 manifest as authoritative skill registry.

**In Scope:**
- Skill manifest `.raise/manifests/skills.json` — SHA256 per-file, version, origin (`framework`/`org`)
- dpkg three-hash detection: auto-update untouched files, keep customized, prompt on conflict
- Interactive conflict resolution (diff/keep/overwrite/backup) for TTY
- CLI flags: `--dry-run`, `--force`, `--skip`
- Non-TTY defaults to `--skip` (CI-safe)
- Updated `SkillScaffoldResult` reporting: installed/updated/conflicted/skipped/unmanaged
- Legacy handling: first init on existing project without manifest
- Manifest serves as authoritative registry of RaiSE-managed skills for memgraph

**Out of Scope:**
- `org` origin support (manifest field exists but no distribution mechanism yet)
- Dedicated `rai skill sync` subcommand (future, if needed)
- Skill extension hooks (parking lot SES-224)
- 3-way merge with `git merge-file` (Phase 2 if needed)
- Sub-file detection (frontmatter vs body) (Phase 2)
- Migration scripts between skill versions (YAGNI for now)

**Done Criteria:**
- [ ] `.raise/manifests/skills.json` written on every `rai init`
- [ ] Three-hash detection correctly classifies: current/auto-update/keep/conflict
- [ ] Auto-update works for untouched skills
- [ ] Customized skills are not silently overwritten
- [ ] Interactive prompt works for conflicts (TTY)
- [ ] `--dry-run` shows table of changes without mutating
- [ ] `--force` overwrites all, `--skip` keeps all
- [ ] Non-TTY defaults to skip
- [ ] `SkillScaffoldResult` reports all categories
- [ ] Legacy project (no manifest) handled gracefully
- [ ] Tests pass, types pass, lint passes
- [ ] Retrospective complete
