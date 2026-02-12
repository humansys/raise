# Implementation Plan: S18.1 — Repo Readiness

## Overview
- **Story:** S18.1 — Repo Readiness
- **Size:** M
- **Created:** 2026-02-12
- **Note:** Mostly file creation/updates — no source code changes, no TDD cycles.

## Tasks

### Task 1: Security Audit (gitleaks)
- **Description:** Run gitleaks on current working tree to verify no secrets. Since D2 (fresh start), we only need clean current state — history won't be pushed to GitHub.
- **Files:** None modified (scan only)
- **Verification:** `gitleaks detect --source . --no-git` exits clean (or document findings)
- **Size:** S
- **Dependencies:** None
- **Note:** If gitleaks not installed, install via `brew install gitleaks` or download binary.

### Task 2: Harden .gitignore
- **Description:** Add secret-pattern entries missing per research: `.env`, `.env.*`, `*.pem`, `*.key`, `.pypirc`, `credentials.json`, `*.sqlite`, `.netrc`
- **Files:** `.gitignore`
- **Verification:** All patterns present in .gitignore
- **Size:** XS
- **Dependencies:** None

### Task 3: Update CONTRIBUTING.md
- **Description:** Update for GitHub open-core context:
  - GitLab URLs → GitHub URLs (use placeholder `https://github.com/humansys-ai/raise-commons` until S18.3 confirms)
  - `GitLab Issue` → `Issue`
  - `Merge Request` → `Pull Request`
  - `raise --version` / `uv run raise` → `rai --version` / `uv run rai`
  - Remove direnv section (too detailed)
  - Add link to CODE_OF_CONDUCT.md
- **Files:** `CONTRIBUTING.md`
- **Verification:** No `gitlab` or `raise ` (with space) references remain; `grep -i gitlab CONTRIBUTING.md` returns nothing
- **Size:** S
- **Dependencies:** None

### Task 4: Create CODE_OF_CONDUCT.md
- **Description:** Contributor Covenant v2.1. Contact: emilio@humansys.ai
- **Files:** `CODE_OF_CONDUCT.md`
- **Verification:** File exists, contains "Contributor Covenant" and "2.1"
- **Size:** XS
- **Dependencies:** None

### Task 5: Create CHANGELOG.md
- **Description:** Keep a Changelog format with v2.0.0-alpha.6 entry covering initial public release.
- **Files:** `CHANGELOG.md`
- **Verification:** File exists, follows Keep a Changelog structure
- **Size:** XS
- **Dependencies:** None

### Task 6: Create SECURITY.md
- **Description:** Coordinated Vulnerability Disclosure policy. Contact: emilio@humansys.ai. 48h ack, 30-day fix target, safe harbor.
- **Files:** `SECURITY.md`
- **Verification:** File exists, contains disclosure process and contact
- **Size:** XS
- **Dependencies:** None

### Task 7: Create GitHub Issue Templates
- **Description:** YAML-format issue templates in `.github/ISSUE_TEMPLATE/`:
  - `bug-report.yml` — structured with version, OS, steps to reproduce
  - `feature-request.yml` — problem statement, proposed solution
  - `config.yml` — blank issue link + discussion link
- **Files:** `.github/ISSUE_TEMPLATE/bug-report.yml`, `.github/ISSUE_TEMPLATE/feature-request.yml`, `.github/ISSUE_TEMPLATE/config.yml`
- **Verification:** YAML is valid (`python -c "import yaml; yaml.safe_load(open('...'))"`)
- **Size:** S
- **Dependencies:** None

### Task 8: Dependency Vulnerability Check
- **Description:** Run `pip-audit` or `uv pip audit` to check for known vulnerabilities in dependencies.
- **Files:** None modified (scan only)
- **Verification:** No critical/high vulnerabilities, or documented exceptions
- **Size:** XS
- **Dependencies:** None

### Task 9: Verification & Commit
- **Description:** Run existing test suite to confirm no regressions. Commit all changes.
- **Files:** All modified/created files
- **Verification:** `pytest` passes, `ruff check .` passes
- **Size:** XS
- **Dependencies:** Tasks 1-8

## Execution Order

1. Task 1 — Security audit (do first, informs if more work needed)
2. Task 2 — .gitignore hardening (quick, protects future)
3. Tasks 3-7 — parallel (all independent file creation/updates)
4. Task 8 — Dep vulnerability check
5. Task 9 — Verification & commit

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| gitleaks finds secrets in current tree | Low | Medium | Remove from tree, add to .gitignore, won't affect GitHub (fresh start) |
| gitleaks not available on system | Low | Low | Install or use alternative (`detect-secrets`) |
| pip-audit finds critical vuln | Low | Medium | Assess if fixable now or document as known issue |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| 1. Security audit | S | -- | |
| 2. .gitignore | XS | -- | |
| 3. CONTRIBUTING.md | S | -- | |
| 4. CODE_OF_CONDUCT.md | XS | -- | |
| 5. CHANGELOG.md | XS | -- | |
| 6. SECURITY.md | XS | -- | |
| 7. Issue templates | S | -- | |
| 8. Dep vuln check | XS | -- | |
| 9. Verify & commit | XS | -- | |
