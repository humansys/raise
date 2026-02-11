## Story Scope: S-NAMESPACE

**Size:** M (mechanical rename, many sync points)
**Research:** RES-NAMESPACE-001 (complete)
**Branch:** `story/S-NAMESPACE/skill-namespace-prefix` off `v2`

### Context

Pre-publish rename window (PAT-253). Add `rai-` prefix to all distributed skills
to prevent collision with user-created and third-party skills in `.claude/skills/`.

Convention follows the Agent Skills specification (`[a-z0-9-]` only) and aligns
with the Spec Kit ecosystem precedent (`speckit-specify`, `speckit-plan`, etc.).

### In Scope

- Rename 20 distributed skill directories in `src/rai_cli/skills_base/`
- Rename corresponding 20 skill directories in `.claude/skills/`
- Update SKILL.md frontmatter `name:` fields (40 files)
- Update `DISTRIBUTABLE_SKILLS` list in `src/rai_cli/skills_base/__init__.py`
- Update both `methodology.yaml` files (~50 references)
- Update cross-references in 14 SKILL.md files (Complement, Next, Previous links)
- Update 4 non-distributed skills in `.claude/skills/` (docs-update, framework-sync, skill-create, discover-complete)
- Update test files (~5 files, ~40 assertions)
- Update migration.py known_skills if present
- Regenerate MEMORY.md from updated methodology.yaml
- Rebuild graph to verify extraction

### Out of Scope

- Alias mechanism (ruled out — simple convention only)
- Plugin-based namespacing (not available for project-level skills)
- Changes to skill body content beyond cross-references
- CLAUDE.md / CLAUDE.local.md updates (these reference skills by slash-command)
- AGENTS.md support

### Done Criteria

- [ ] All 20+ skill directories renamed with `rai-` prefix in both locations
- [ ] All SKILL.md frontmatter `name:` fields match directory names
- [ ] DISTRIBUTABLE_SKILLS list updated
- [ ] Both methodology.yaml files updated
- [ ] All cross-references between skills updated
- [ ] All tests pass (`pytest`)
- [ ] Type checks pass (`pyright`)
- [ ] Linting passes (`ruff check`)
- [ ] Graph builds successfully (`rai memory build`)
- [ ] MEMORY.md regenerated
- [ ] Retrospective complete
