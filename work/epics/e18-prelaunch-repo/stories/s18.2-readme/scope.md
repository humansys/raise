## Story Scope: S18.2 — README

**Size:** M
**Epic:** E18 (Pre-Launch Repo Readiness)
**GTM Ref:** S7.2
**Branch:** story/s18.2/readme

**In Scope:**
- Full README.md rewrite following FastAPI/Ruff pattern (D4: one-liner → code example → features)
- Quick start: `pip install rai-cli` → `rai init --detect` → `claude` → `/rai-session-start`
- Feature highlights (24 skills, multi-language discovery, knowledge graph, memory)
- Session transcript as visual (D8: text-based, Claude Code is terminal)
- Badges: PyPI version, Python versions, license
- What's included vs what's coming (open core positioning)
- Links to community files (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG)
- Link to blog post BP-01

**Out of Scope:**
- Full documentation site (post-launch)
- Demo video/GIF (nice-to-have, post-launch)
- pyproject.toml changes (S18.3)
- CI/CD badges (no CI yet)

**Done Criteria:**
- [ ] README follows FastAPI/Ruff pattern (one-liner → example → features)
- [ ] `pip install rai-cli` quick start is accurate
- [ ] Session transcript demonstrates real workflow
- [ ] Badges render correctly
- [ ] Links to community files work
- [ ] All existing tests still pass
- [ ] Retrospective complete

**Dependencies:** S18.1 ✓ (repo shape finalized)
