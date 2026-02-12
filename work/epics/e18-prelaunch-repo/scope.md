# Epic E18: Pre-Launch Repo Readiness — Scope

> **Status:** PENDING
> **Branch:** TBD (via `/rai-epic-start`)
> **Created:** 2026-02-12
> **Soft launch:** 2026-02-15 (Saturday)
> **Parent:** E7 Pre-Launch Open Core (raise-gtm) — Dev Rai track

---

## Objective

Prepare raise-commons for public release: security audit, community files, README for 30-second conversion, and release engineering (GitHub mirror + PyPI publish).

**Value proposition:** This is the repo track of the E7 pre-launch epic. Everything a developer sees when they find RaiSE — the repo, the README, the install experience — is built here. Repo quality > marketing volume.

**Success criteria:**
- No secrets in git history
- Community files complete (LICENSE consistent, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG)
- README converts a developer in 30 seconds (validated with F&F)
- `pip install rai-cli` works from PyPI on clean environment
- GitHub public mirror live

---

## Stories (3)

| ID | Story | Size | GTM Ref | Description |
|----|-------|:----:|---------|-------------|
| S18.1 | Repo Readiness | M | S7.1 | Security audit, license fix, NOTICE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG, issue templates, dep check |
| S18.2 | README | M | S7.2 | Open-core README — 30-second conversion, GIF/screenshot, quick start, badges |
| S18.3 | Release Engineering | M | S7.4 | pyproject.toml cleanup, GitHub mirror setup, TestPyPI → PyPI, release tag v2.0.0-alpha |

**Total:** 3 stories (all M), all in raise-commons

---

## In Scope

**MUST:**
- Security audit of git history (no leaked secrets)
- License consistency (Apache 2.0 everywhere)
- CONTRIBUTING.md updated for GitHub open core
- CODE_OF_CONDUCT.md (Contributor Covenant)
- CHANGELOG.md with v2.0.0-alpha release notes
- README.md that converts in 30 seconds
- Working PyPI install from clean environment
- GitHub public mirror of open core

**SHOULD:**
- 30-second GIF for README (real session demo)
- GitHub issue templates (bug, feature, first session)
- NOTICE file (Apache 2.0 best practice)
- Badges (PyPI version, Python versions, license, tests)

---

## Out of Scope

- Blog post (BP-01) → raise-gtm S7.3 (done)
- Launch content (LinkedIn, HN, Reddit) → raise-gtm S7.5
- Soft/community launch execution → raise-gtm S7.6/S7.7
- CI/CD pipeline → post-launch
- Full documentation site → post-launch
- Demo video → nice-to-have, not blocking

---

## Done Criteria

### Per Story
- [ ] Code/files implemented
- [ ] Quality checks pass (where applicable)
- [ ] Retrospective complete

### Epic Complete
- [ ] `pip install rai-cli` works from PyPI on clean environment
- [ ] README reviewed by F&F
- [ ] All community files present and consistent
- [ ] GitHub mirror live
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Dependencies

```
S18.1 (Repo Readiness)
  │
  ├──→ S18.2 (README) — soft dependency, can start once repo shape is clear
  │
  └──→ S18.3 (Release Engineering) — hard dependency on clean repo
            │
            └── soft dependency on S18.2 (README should be ready before publish)
```

**Cross-repo:**
- S18.3 completion unblocks raise-gtm S7.6 (Soft Launch)
- raise-gtm S7.3 (BP-01) already done — no inbound dependency

---

## Key Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Separate epic in raise-commons (E18) vs inline in GTM E7 | Each repo owns its own work artifacts. GTM E7 references via GTM Ref column. |
| 2 | Story IDs S18.x (not S7.x) | raise-commons numbering, cross-referenced to GTM S7.x |
| 3 | Plan from raise-gtm S7.1 reused | S7.1 plan already detailed and reviewed — adopt, don't redo |

---

## Coordination

**Dev Rai** (raise-commons): Owns S18.1, S18.2, S18.3
**Market Rai** (raise-gtm): Owns S7.3 (done), S7.5
**Emilio** coordinates: S7.6 (soft launch), S7.7 (community launch)

Handoff signal: Dev Rai updates raise-gtm E7 progress tracking when S18.x stories complete.

---

*Created: 2026-02-12*
*Source: E7 Pre-Launch Open Core (raise-gtm)*
