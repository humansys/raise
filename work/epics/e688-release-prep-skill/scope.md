---
epic_id: "E688"
jira_key: "RAISE-688"
title: "/rai-release-prep — Automated Release Preparation Skill"
status: "backlog"
created: "2026-03-24"
---

# E688: /rai-release-prep — Automated Release Preparation Skill

## Objective

Create a deterministic, repeatable release preparation skill that guides (or automates) the full release lifecycle from scope audit to PyPI publish, with built-in Pro/Community separation and type-aware depth scaling.

## Value

- **Reliability:** Every release follows the same verified process — no ad-hoc steps, no forgotten gates
- **Pro/Community safety:** Automated audit prevents Pro content from leaking into Community releases
- **Scalable:** Patch/minor/major releases get appropriate depth without over-engineering patches or under-preparing majors
- **Repeatable:** Any developer (human or AI) can execute a release by running a single skill

## Context — What E680 Taught Us

v2.3.0 (E680) was the first release to follow the 7-dimension checklist from research. Key learnings:

### What Worked
- 7-dimension framework from research was ~80% correct
- Story-per-dimension decomposition gave good traceability
- Smoke tests expanded to cover changelog entries (PAT-E-692) — high ROI
- sync-skills.py visibility filter correctly excluded internal skills
- sync-github.sh filtered Pro code from GitHub mirror

### What Was Missing
1. **Pro/Community content audit (Dimension 0)** — Caught 3 leaks progressively during v2.3.0:
   - Round 1: ACLI adapter entries in changelog/release notes
   - Round 2: Jira/MCP/backlog bugfixes in changelog
   - Round 3: ISO 27001 audit entry in changelog
   A formal audit at the START would have caught all 3 at once.

2. **GitHub mirror sync (Dimension 9)** — Not in original framework. Required steps:
   - sync-github.sh creates filtered orphan commit
   - Tag must be pushed to GitHub separately
   - GitHub Release notes created manually (auto-generated is too bare)

3. **Content boundary rules** — Never documented until we hit them:
   - Pro features: Jira adapters, ACLI, MCP servers, Confluence adapters, ISO 27001
   - Community features: Session, CLI extensions, patterns, discovery, skills, doctor
   - Ambiguous: backlog commands (Pro adapter), rai doctor ACLI check (Community command, Pro check)

### Operational Gotchas Discovered
- `sync-skills.py` can corrupt `__init__.py` (duplicate list bug)
- `rai release publish` needs interactive confirmation (`yes |` pipe for automation)
- `rai release check` has 2 expected failures (twine not installed, no unreleased entries) — non-blocking
- Local main branch can diverge from origin/main — sync-github.sh should use `origin/main` directly
- Jira fixVersion names are bare ("2.3.0" not "v2.3.0")
- GitLab MR description doesn't propagate to GitHub — no leak risk but awareness needed

## Research Input

- `work/research/release-prep-best-practices/release-prep-report.md` — 13 sources, 7 claims
- `work/epics/e680-release-v2.3.0-prep/stories/s680.6-e680-docs.md` — E680 epic docs with validated hypothesis
- E680 story retrospectives (s680.1 through s680.5)

## Validated Release Prep Matrix

From E680 hypothesis validation — this is the **proven** matrix:

| # | Dimension | Patch (2.x.Y) | Minor (2.X.0) | Major (X.0.0) |
|---|-----------|:---:|:---:|:---:|
| 0 | **Pro/Community audit** | verify clean | verify clean | verify clean |
| 1 | Scope audit (Jira ↔ git) | auto | auto | auto |
| 2 | Changelog (Keep a Changelog) | required | required | required |
| 3 | Epic docs (`/rai-epic-docs`) | skip | run per epic | run per epic |
| 4 | User/dev docs (`/docs`) | conditional | Community only | Community + migration guide |
| 5 | Security audit (dep scan) | verify clean | verify clean | full audit |
| 6 | Quality gates (test + lint + type) | unit + smoke | full suite + smoke | full + install test |
| 7 | Release mechanics | `rai release publish` | `rai release publish` | TestPyPI → PyPI |
| 8 | Communication | changelog only | changelog + GH release + Confluence | blog + migration guide |
| 9 | **GitHub mirror sync** | sync-github.sh | sync-github.sh | sync-github.sh |
| R1 | RaiSE: skill validate | skip | run | run |
| R2 | RaiSE: gate check --all | run | run | run |
| R3 | RaiSE: smoke test changelog | skip | run | run |

**Dimension 0 and 9 are NEW — discovered during E680.**

## Scope Boundaries

### In (MUST)
- `/rai-release-prep` orchestrator skill — runs dimensions 0-9 in sequence
- Type detection (patch/minor/major) from `--bump` argument
- Pro/Community content audit (Dimension 0) — grep-based verification
- Changelog generation assistance (not full auto — manual curation validated as better)
- Quality gates execution
- Smoke test execution (expanded: cover changelog entries)
- `rai release publish` integration
- `sync-github.sh` integration
- GitHub Release notes from template

### In (SHOULD)
- Sub-skills for complex dimensions (epic-docs, changelog, smoke-test)
- Dry-run mode showing all steps without executing
- Resume from last completed dimension (like story-run resumes from artifacts)

### Out of Scope
- Automated changelog generation from conventional commits (parking lot — evaluate for v2.4.0+)
- TestPyPI verification (only for major releases, defer until first major)
- Blog post generation (manual for now)
- Monorepo-aware release (separate concern, after monorepo migration)

## Stories (Draft)

| ID | Story | Description | Size |
|----|-------|-------------|:----:|
| S688.1 | Pro/Community audit skill | `/rai-release-audit` — grep-based verification that changelog, release notes, docs don't contain Pro content | S |
| S688.2 | Release prep orchestrator | `/rai-release-prep` — runs dimensions 0-9 based on release type, with delegation gates | M |
| S688.3 | Smoke test expansion | Enhance S680.5 approach — auto-derive verifications from changelog Added/Changed entries | S |
| S688.4 | GitHub mirror + release | Integrate sync-github.sh + tag push + GH release creation into skill | S |
| S688.5 | Dogfood on v2.3.1 or v2.4.0 | Run `/rai-release-prep` on next actual release | S |

## Dependencies

```
S688.1 ──→ S688.2 ──→ S688.5
S688.3 ──→ S688.2
S688.4 ──→ S688.2
```

## Done Criteria

- [ ] `/rai-release-prep --bump minor` runs full v2.3.0-equivalent process
- [ ] Pro/Community audit catches known leak patterns (Jira, ACLI, MCP, ISO 27001)
- [ ] Smoke tests auto-derive from changelog entries
- [ ] GitHub mirror sync integrated (not a manual step)
- [ ] Dogfooded on at least one real release
- [ ] Retrospective validates process improvement over E680

## Invariants (from E680)

These MUST be enforced by the skill:

1. **INV-1:** Community changelog MUST NOT reference Pro features
2. **INV-2:** sync-skills.py filters by `visibility: public`
3. **INV-3:** sync-github.sh excludes `packages/`, `.claude/`, `work/`, `scripts/`
4. **INV-4:** pyproject.toml is patched during sync (no workspace refs)
5. **INV-5:** All quality gates pass before release
6. **INV-6:** Smoke tests verify changelog entries, not just core workflows
7. **INV-7:** Tag pushed to GitHub (not just GitLab) to trigger PyPI

## Failure Modes to Prevent (from E680)

| FM | Issue | Prevention in skill |
|----|-------|-------------------|
| FM-1 | sync-skills.py corrupts __init__.py | Verify after sync, auto-fix if duplicate detected |
| FM-2 | Pro content in Community changelog | Dimension 0 audit with known Pro keyword list |
| FM-3 | Local main diverges | Always use `origin/main` in sync-github.sh |
| FM-4 | Interactive prompt blocks automation | Pipe `yes` or use `--yes` flag |
| FM-5 | Tag only on GitLab, not GitHub | Skill pushes to both remotes |
| FM-6 | Jira version name mismatch | Query actual version names before updating |
| FM-7 | ISO/audit entries slip through | Pro keyword list includes "ISO", "audit report", "compliance" |

## Pro Content Keywords (for audit)

```yaml
pro_keywords:
  features:
    - ACLI
    - AcliJira
    - McpJira
    - MCP.*adapter
    - Jira.*adapter
    - Confluence.*adapter
    - ISO 27001
    - audit report
    - compliance
  commands:
    - backlog.*search
    - backlog.*command
    - JQL
  packages:
    - raise-pro
    - raise-server
    - rai_pro
```
