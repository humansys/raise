## Feature Scope: F128.4 — Init --ide Flag + E2E Tests

**Epic:** RAISE-128 IDE Integration
**Size:** S
**Depends on:** F128.3 ✓

### In Scope

- Wire `--ide` CLI flag in `cli/commands/init.py` (coupling point #6)
- Pass IDE selection through to scaffolding functions that already accept `IdeConfig`
- E2E tests: `rai init --ide antigravity` produces working `.agent/` structure
- E2E tests: `rai init` (default) still produces `.claude/` structure (backward compat)
- Validate all scaffolding outputs for both IDE paths

### Out of Scope

- New IDE configs beyond Claude + Antigravity (future epic)
- Runtime IDE detection (RAISE-127)
- Migration of existing projects (`rai migrate --ide`)
- Changes to `IdeConfig` model (done in F128.1)
- Changes to scaffolding functions (done in F128.2 + F128.3)

### Done Criteria

- [ ] `rai init --ide antigravity` produces `.agent/` with skills, config, workflows
- [ ] `rai init` (no flag) produces `.claude/` structure identically to pre-epic behavior
- [ ] CLI help shows `--ide` option with valid choices
- [ ] Unit/integration tests cover both IDE paths
- [ ] All quality gates pass (ruff, pyright, bandit, pytest >90%)
- [ ] M3 milestone complete
