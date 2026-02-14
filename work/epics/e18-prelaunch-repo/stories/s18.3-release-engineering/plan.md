# Implementation Plan: S18.3 — Release Engineering

## Overview
- **Story:** S18.3
- **Size:** M
- **Type:** Infrastructure (config files + gh CLI — no source code)
- **Created:** 2026-02-13
- **Research:** S18.4 security-quality-tooling synthesis

## Tasks

### Task 1: Pre-commit Configuration
- **Description:** Create `.pre-commit-config.yaml` with L1 stack from S18.4 research. Generate `.secrets.baseline` for detect-secrets. Add bandit config to `pyproject.toml`.
- **Files:**
  - `.pre-commit-config.yaml` (new)
  - `.secrets.baseline` (new, generated)
  - `pyproject.toml` (add `[tool.bandit]` section)
- **Hooks:**
  - pre-commit: pre-commit-hooks (6), ruff check+format, detect-secrets, bandit
  - pre-push: pyright
- **Verification:** `pre-commit install && pre-commit run --all-files` passes <4s
- **Size:** S
- **Dependencies:** None

### Task 2: GitHub Actions CI Workflow
- **Description:** Create CI workflow that runs tests, linting, and type checking on push and PR. Matrix for Python 3.12 (expand later).
- **Files:** `.github/workflows/ci.yml` (new)
- **Jobs:** test (pytest), lint (ruff check), typecheck (pyright)
- **Verification:** Workflow file validates with `actionlint` or manual review. Will run on next sync+push.
- **Size:** S
- **Dependencies:** None

### Task 3: CodeQL Workflow
- **Description:** Create CodeQL security analysis workflow for Python. Runs on push to main and weekly schedule. Uses security-extended query suite.
- **Files:** `.github/workflows/codeql.yml` (new)
- **Verification:** Workflow file structure reviewed. Activates when repo goes public.
- **Size:** XS
- **Dependencies:** None

### Task 4: GitLab CI Configuration
- **Description:** Create `.gitlab-ci.yml` with SAST, dependency scanning, and secret detection using GitLab template includes. Add test stage for pytest + ruff + pyright.
- **Files:** `.gitlab-ci.yml` (new)
- **Verification:** `cat .gitlab-ci.yml` — valid YAML with correct template paths. Pipeline runs on next push to GitLab.
- **Size:** S
- **Dependencies:** None

### Task 5: Dependabot Configuration
- **Description:** Create Dependabot config for weekly pip and github-actions dependency updates.
- **Files:** `.github/dependabot.yml` (new)
- **Verification:** Valid YAML structure. Activates on GitHub.
- **Size:** XS
- **Dependencies:** None

### Task 6: Release Workflow (Trusted Publishers)
- **Description:** Create GitHub Actions release workflow triggered by `v*` tags. Uses `pypa/gh-action-pypi-publish` with OIDC Trusted Publishers (no token). Includes PEP 740 attestations.
- **Files:** `.github/workflows/release.yml` (new)
- **Verification:** Workflow file reviewed. Requires HITL: Trusted Publisher must be configured on PyPI (manual step).
- **Size:** S
- **Dependencies:** None (but activation requires T7)

### Task 7: Sync, Flip Public, and Publish (HITL)
- **Description:** Final integration: sync filtered content to GitHub, flip repo to public, configure Trusted Publisher on PyPI, create release tag, verify end-to-end.
- **Steps:**
  1. Sync latest to GitHub (`./scripts/sync-github.sh v2 main`)
  2. **HITL:** Flip repo to public (`gh repo edit humansys/raise --visibility public`)
  3. **HITL:** Configure Trusted Publisher on pypi.org (owner: humansys, repo: raise, workflow: release.yml)
  4. Enable branch protection on main (now possible with public repo)
  5. Bump version to `2.0.0-alpha.7` in pyproject.toml
  6. Tag and push: `git tag v2.0.0-alpha.7 && git push github v2.0.0-alpha.7`
  7. Verify: release workflow triggers, package appears on PyPI, `pip install rai-cli` works
- **Verification:** `pip install rai-cli==2.0.0a7` on clean venv succeeds
- **Size:** M
- **Dependencies:** All previous tasks

## Execution Order

```
T1 (pre-commit) ──┐
T2 (CI workflow) ──┤
T3 (CodeQL) ───────┼──→ T7 (sync + publish — HITL)
T4 (GitLab CI) ────┤
T5 (Dependabot) ───┤
T6 (Release wf) ───┘
```

1. **T1–T6** — All independent, can execute sequentially in any order
2. **T7** — Final integration after all config files committed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Trusted Publisher OIDC config fails | Low | Medium | Fall back to API token temporarily; fix OIDC after |
| pre-commit hooks slow (>4s) | Low | Low | Profile and remove slowest hook |
| GitLab CI template syntax changes | Low | Low | Pin to stable templates; test on MR |
| Public flip exposes something unexpected | Low | High | Run sync-github.sh + review GitHub content before flipping |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| T1: Pre-commit | S | — | |
| T2: CI workflow | S | — | |
| T3: CodeQL | XS | — | |
| T4: GitLab CI | S | — | |
| T5: Dependabot | XS | — | |
| T6: Release workflow | S | — | |
| T7: Sync + publish | M | — | HITL required |
