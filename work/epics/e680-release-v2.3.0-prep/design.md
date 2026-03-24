---
epic_id: "E680"
title: "Release v2.3.0 Prep — Design"
created: "2026-03-23"
---

# E680: Design — Release v2.3.0 Prep

## Gemba: What Went Wrong in Previous Releases

Releases v2.2.0 through v2.2.3 were ad-hoc:
- No epic documentation published to Confluence
- CHANGELOG updated minimally or retroactively
- No formal security verification gate
- No smoke test beyond "tests pass"
- No release announcement or communication
- Documentation debt accumulated across 12+ epics (flagged in RAISE-433)

v2.3.0 is the first release to follow the 7-dimension checklist from research.

## 7-Dimension Release Framework

Based on `work/research/release-prep-best-practices/release-prep-report.md` (13 sources):

### Phase 1: Pre-Release (S680.1 → S680.5)

| Dimension | Story | Deliverable |
|-----------|-------|-------------|
| 1. Scope audit | DONE | 36 tickets tagged, Jira ↔ git reconciled |
| 2. Changelog | S680.2 | CHANGELOG.md v2.3.0 entry (Keep a Changelog) |
| 3. Documentation | S680.1 + S680.3 | 3 Confluence pages + `/docs` updates |
| 4. Security | S680.4 | `pip-audit`, verify 0 open CVEs |
| 5. Verification | S680.4 + S680.5 | Full test suite + gates + smoke tests |

### Phase 2: Release (S680.6)

| Dimension | Deliverable |
|-----------|-------------|
| 6. Release mechanics | `/rai-publish --bump minor` → PyPI |

### Phase 3: Post-Release (S680.6)

| Dimension | Deliverable |
|-----------|-------------|
| 7. Communication | GitHub release notes + Confluence page |

## Story Details

### S680.1: Epic Documentation (M)

Run `/rai-epic-docs` for each completed epic:

| Epic | Key artifacts | Complexity |
|------|--------------|:----------:|
| E478 Pro/Community | 3 stories, pro/community package split | S |
| E494 ACLI Adapter | 7 stories, new adapter architecture | M |
| E654 Session Identity | 4 stories, new session model | M |

Each produces: worked example, extension guide, data flow, invariants, failure modes.
Publish to Confluence space RaiSE1.

### S680.2: Changelog & Release Notes (S)

**CHANGELOG.md format (Keep a Changelog):**

```markdown
## [2.3.0] - 2026-03-30

### Added
- ACLI Jira adapter with multi-instance support (E494)
- Session identity model — deterministic IDs per dev+repo (E654)
- CLI extension mechanism via entry points (RAISE-594)
- ISO 27001 audit report generator — control mapping + git evidence (E479 partial)
- `rai doctor` ACLI availability check (RAISE-614)

### Changed
- MCP Jira adapter replaced by ACLI adapter (E494) — breaking for users who extended McpJiraAdapter
- Session data moved from personal/ to git-tracked shared directory (E654)
- Pattern add default scope changed from personal to project (RAISE-608)

### Fixed
- [12 bugfixes listed individually]

### Security
- authlib 1.6.8→1.6.9 — 3 CVEs (RAISE-574)
- PyJWT ≥2.12.0 — crit header bypass (RAISE-575)
- astro/cloudflare/undici — 9 Snyk CVEs in site/ (RAISE-576)
```

**GitHub release notes:** Summary + highlights + known issues + contributor recognition.

### S680.3: User & Dev Docs (S)

Update `/docs` for:
1. **ACLI adapter migration** — users on McpJiraAdapter need to know it's replaced
2. **Session identity** — new session ID format, shared session index
3. **CLI extensions** — how to register commands via entry points
4. **Breaking changes** — MCP adapter removal, session path changes

### S680.4: Quality Gates & Security (S)

```bash
uv run pytest                    # full test suite
uv run pyright                   # type checking
uv run ruff check .              # linting
uv run rai gate check --all      # framework gates
uv run rai skill validate        # skill structure validation
uv run pip-audit                 # dependency CVE scan
uv run rai graph build           # knowledge graph integrity
```

### S680.5: Smoke Test & Verification (S)

1. **Session roundtrip:** `rai session start --project .` → work → `rai session close` (from main repo, not worktree)
2. **ACLI integration:** `rai backlog search "RAISE-680" -a jira` — verify adapter works
3. **Clean install test:** `uv pip install raise-cli` in clean venv, run `rai --help`

### S680.6: Release Publish & Announce (XS)

1. `/rai-publish --bump minor`
2. Verify PyPI listing
3. GitHub release with notes
4. Confluence release page (optional, SHOULD)

## Known Issues (to document in release notes)

| Ticket | Issue | Status |
|--------|-------|--------|
| RAISE-539 | `rai mcp install` env parsing KEY=VALUE | Assigned to Fernando |
| RAISE-634 | Docs site broken links | Assigned to Fernando |
| RAISE-213 | MCP Jira JSM permissions | Assigned to Fernando |

## Parking Lot

- `/rai-release-prep` skill design → retro output, deferred to post-release
- TestPyPI verification → skipped for v2.3.0 (CI is solid), consider for major releases
- Automated changelog generation from conventional commits → evaluate for v2.4.0+
