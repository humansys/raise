## Story Scope: S-RENAME

**In Scope:**
- Rename CLI command `raise` → `rai` across entire codebase
- Rename package `raise-cli` → `rai-cli` in pyproject.toml and distribution config
- Update all references in source code, tests, skills, docs, and config files
- Update entry points and script definitions
- Ensure all tests pass after rename

**Out of Scope:**
- PyPI publish (deferred to after S-RENAME)
- Skill namespace prefixing with `rai.` (S-NAMESPACE decision pending)
- Any functional changes — this is purely mechanical rename

**Done Criteria:**
- [ ] `raise` → `rai` command name updated everywhere
- [ ] `raise-cli` → `rai-cli` package name updated everywhere
- [ ] All tests pass
- [ ] Type checks pass (pyright)
- [ ] Linting passes (ruff)
- [ ] `rai --help` works
- [ ] Retrospective complete
