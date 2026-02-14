---
story_id: S18.3
title: Release Engineering
type: infrastructure
complexity: moderate
components: [pre-commit, github-actions, gitlab-ci, pypi, dependabot]
research: S18.4 security-quality-tooling synthesis
---

# S18.3: Release Engineering — Design

## Problem

rai-cli has no CI/CD pipeline, no pre-commit hooks, and no automated release flow. The current publish process is manual (`uv build && twine upload`). For a project that teaches DevSecOps discipline, the repo should embody it from day one.

## Value

Unblocks launch (M2: Launch Ready). Every push gets tested, every release is attested, and the public repo demonstrates the quality bar RaiSE advocates. Also unblocks raise-gtm S7.6 (Soft Launch).

## Scope Adjustment (post-S18.5)

S18.5 already delivered:
- GitHub repo (`humansys/raise`) — private, ready for public flip
- Sync script (`scripts/sync-github.sh`) — filtered orphan-commit mirror
- GitHub remote configured, initial content pushed
- PR template, labels, engineering team

**This story focuses on what S18.5 didn't cover:** pre-commit hooks, CI pipelines, release automation, and the publish flow.

## Approach

Three layers per S18.4 research recommendations:

### L1: Pre-commit Hooks (local dev)

| Hook | Stage | Purpose |
|------|-------|---------|
| pre-commit-hooks (6) | pre-commit | trailing-whitespace, end-of-file-fixer, check-yaml, check-toml, check-merge-conflict, check-added-large-files |
| ruff (check + format) | pre-commit | Lint + format |
| detect-secrets | pre-commit | Secret scanning with baseline |
| bandit | pre-commit | Security audit (medium severity, high confidence) |
| pyright | pre-push | Type checking (too slow for pre-commit) |

Target: pre-commit <4s, pre-push <15s.

**Files:** `.pre-commit-config.yaml`, `.secrets.baseline`

### L2: CI Pipelines

**GitHub Actions** (on humansys/raise):
- `ci.yml` — test + lint + type check on push/PR
- `codeql.yml` — CodeQL security-extended on push to main + weekly

**GitLab CI** (on raise-commons):
- `.gitlab-ci.yml` — SAST + dependency scanning + secret detection (3 template includes)

**Dependabot** (on humansys/raise):
- `.github/dependabot.yml` — weekly pip + github-actions updates

**Files:** `.github/workflows/ci.yml`, `.github/workflows/codeql.yml`, `.gitlab-ci.yml`, `.github/dependabot.yml`

### L3: Release Pipeline

**GitHub Actions:**
- `release.yml` — Trusted Publishers workflow, triggered by git tag `v*`
- Uses `pypa/gh-action-pypi-publish` with PEP 740 attestations (automatic)
- No token stored — OIDC Trusted Publisher configured on PyPI

**Manual steps (this story):**
- Verify TestPyPI publish works
- Configure Trusted Publisher on PyPI for `humansys/raise`
- Create release tag `v2.0.0-alpha.7`
- Flip repo to public

**Files:** `.github/workflows/release.yml`

### Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | detect-secrets over gitleaks | Lower false positive rate, pure Python, baseline file. Per S18.4 RQ1. |
| D2 | CodeQL on GitHub, not SonarCloud | 88% accuracy vs 82%, free for public repos, one-click setup. Per S18.4 RQ3. |
| D3 | GitLab CI for scanning, GitHub Actions for release | Source of truth (GitLab) runs security, public mirror (GitHub) runs release. |
| D4 | Trusted Publishers (OIDC) over stored API tokens | No secrets to manage, PEP 740 attestations automatic. Per S18.4 RQ5. |
| D5 | Skip zizmor, SBOM, SLSA for now | Post-launch scope per S18.3 original scope. |
| D6 | Repo goes public during this story | Branch protection unlocked, CodeQL enabled, launch readiness. |

## Acceptance Criteria

**MUST:**
- `.pre-commit-config.yaml` runs <4s (pre-commit stage)
- GitHub Actions CI passes on push (test + lint + type check)
- `pip install rai-cli` works from PyPI on clean environment
- GitHub repo flipped to public
- Release tag `v2.0.0-alpha.7` created

**SHOULD:**
- CodeQL enabled on GitHub mirror
- GitLab CI scanning active (SAST + deps + secrets)
- Dependabot configured for weekly updates
- Trusted Publisher configured on PyPI

**MUST NOT:**
- Store PyPI tokens in GitHub secrets (use Trusted Publishers)
- Break existing test suite or coverage threshold
