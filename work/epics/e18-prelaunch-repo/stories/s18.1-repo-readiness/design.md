# Design: S18.1 — Repo Readiness

> Lean spec — moderate breadth, simple depth. Mostly file creation/updates.

## What & Why

**Problem:** raise-commons has GitLab-oriented community files and missing security hygiene for public GitHub release.

**Value:** A clean, professional open-source repo that passes GitHub's community profile checks and contains no secrets.

## Current State

| File | Status | Action |
|------|--------|--------|
| LICENSE | Apache 2.0 ✓ | None |
| pyproject.toml license | Apache 2.0 ✓ | None |
| NOTICE | Exists ✓ | None |
| CONTRIBUTING.md | Exists, GitLab refs | **Update** — GitHub URLs, `rai` command, PR terminology |
| CODE_OF_CONDUCT.md | Missing | **Create** — Contributor Covenant v2.1 |
| CHANGELOG.md | Missing | **Create** — Keep a Changelog format |
| SECURITY.md | Missing | **Create** — CVD policy |
| .github/ISSUE_TEMPLATE/ | Missing | **Create** — bug-report.yml, feature-request.yml, config.yml |
| .gitignore | Incomplete | **Update** — add secret-pattern entries |

## Approach

### 1. Security Audit (gitleaks scan)

Run `gitleaks detect` on the full repo. Since D2 decided fresh start (squashed initial commit for GitHub), the audit is primarily to verify no secrets exist in the *current tree* — history won't be pushed.

**If secrets found:** Remove from current tree, add to .gitignore, document in SECURITY.md.

### 2. .gitignore Hardening

Add missing entries per research:
```
# Secrets & credentials
.env
.env.*
*.pem
*.key
.pypirc
credentials.json
*.sqlite
.netrc
```

### 3. CONTRIBUTING.md Update

Changes needed:
- `gitlab.com/humansys/raise-commons` → GitHub URL (TBD in S18.3)
- `GitLab Issue` → `Issue`
- `Merge Request` → `Pull Request`
- `raise --version` → `rai --version`
- `uv run raise` → `uv run rai`
- Remove direnv section (too detailed for contributor guide)
- Add link to CODE_OF_CONDUCT.md

### 4. CODE_OF_CONDUCT.md

Contributor Covenant v2.1 — standard adoption. Contact: emilio@humansys.ai

### 5. CHANGELOG.md

Keep a Changelog format. Initial entry:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-alpha.6] — 2026-02-12

### Added
- Initial public release of rai-cli
- 24 RaiSE skills for AI-assisted software engineering
- Codebase discovery with multi-language support (Python, TypeScript, JavaScript, PHP, Svelte)
- Knowledge graph for project context and memory
- Session lifecycle management with memory persistence
- Framework governance documents (constitution, guardrails, glossary)

### Note
- This is an alpha release. APIs and skill interfaces may change.
```

### 6. SECURITY.md

Email-based CVD policy:
- Report to: security@humansys.ai (or emilio@humansys.ai if no security@ yet)
- Response timeline: 48h acknowledgment, 30-day fix target
- Safe harbor statement

### 7. GitHub Issue Templates (YAML format)

Three templates in `.github/ISSUE_TEMPLATE/`:
- `bug-report.yml` — structured bug report
- `feature-request.yml` — feature/enhancement request
- `config.yml` — blank issue option + links

### 8. Dependency Vulnerability Check

Run `uv pip audit` or equivalent to check for known vulnerabilities.

## Acceptance Criteria

**MUST:**
- [ ] No secrets in current working tree (gitleaks clean)
- [ ] .gitignore includes secret-pattern entries
- [ ] CONTRIBUTING.md uses GitHub terminology (no GitLab refs)
- [ ] CODE_OF_CONDUCT.md present (Contributor Covenant v2.1)
- [ ] CHANGELOG.md present (Keep a Changelog format)
- [ ] SECURITY.md present with disclosure policy
- [ ] Issue templates valid YAML in `.github/ISSUE_TEMPLATE/`
- [ ] All existing tests still pass

**SHOULD:**
- [ ] No critical/high dependency vulnerabilities
- [ ] CONTRIBUTING.md references CODE_OF_CONDUCT.md

**MUST NOT:**
- [ ] Touch README.md (that's S18.2)
- [ ] Change pyproject.toml packaging config (that's S18.3)

---

*Design created: 2026-02-12*
*Next: `/rai-story-plan`*
