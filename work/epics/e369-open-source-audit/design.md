# E369: Open Source Readiness Audit — Design

## Approach

No architecture changes. This is a hygiene/polish epic — fix what a critical
reviewer would notice in 15 minutes of evaluation. All changes are cosmetic,
metadata, or CI configuration.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Coverage gap (29%) | Out of scope | Raising coverage is a separate epic. Document it honestly instead of hiding it |
| Old repo refs in work/ | Leave as-is | Historical artifacts, not published to PyPI |
| Trusted Publishers | Document as blocker | Requires manual PyPI config, not code |

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CI matrix change breaks something on 3.13 | Low | Medium | Run tests locally first |
| Secrets found in git history | Low | High | If found, assess if repo needs history rewrite |
| pip-audit finds critical vuln in dep | Medium | Medium | Upgrade dep or document accepted risk |

## Components Touched

- `README.md` — badge only
- `CONTRIBUTING.md` — package name fix
- `SECURITY.md` — version table
- `CHANGELOG.md` — URLs, formatting
- `pyproject.toml` — urls, deps, classifiers
- `.github/workflows/ci.yml` — Python matrix
