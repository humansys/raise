# E369: Open Source Readiness Audit — Scope

## Objective

Make raise-commons credible to a senior dev evaluating it in 15 minutes.
"Reliable AI software engineering" must be evident from first contact through code.

## In Scope

- First contact experience: README, quickstart, install, CLI help
- Trust signals: LICENSE, CONTRIBUTING, CI badge, CHANGELOG, coverage
- Security & dependencies: vulnerability scan, secrets check, dep cleanup
- Walk the talk: error messages, PyPI metadata, repo reflects what it preaches

## Out of Scope

- Code refactoring beyond what blocks credibility
- New feature development
- CI/CD redesign (only fix blockers)
- Performance optimization
- Increasing coverage to >80% (separate epic — too large)

## Gemba Findings

### Already Good
- README: clear value prop, quickstart, structure
- All community files exist (LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CHANGELOG)
- GitHub templates (issues, PR), Dependabot, CodeQL
- CLI help clean and professional
- 3,687 tests

### Issues Found
1. CONTRIBUTING.md:10 — old package name `rai-cli` / `src/rai_cli/`
2. CHANGELOG.md:146-153 — compare URLs point to `humansys/raise` (wrong repo)
3. SECURITY.md:44 — version table says "2.0.0-alpha.x" (stale)
4. pyproject.toml — no `[project.urls]` (Homepage, Docs, Repo, Changelog)
5. pyproject.toml:42 — dead dep `tomli` for `python < 3.11` (requires >=3.12)
6. CHANGELOG.md — missing blank lines between version entries
7. Coverage 29% — low for "reliable" (note: not fixing in this epic)
8. CI only tests Python 3.12, not 3.13
9. README has no CI badge
10. README:38 says "3.14 not yet supported" — verify

## Stories

1. **S369.1 — Documentation Polish** (XS)
   Fix stale references across community docs.
   - CONTRIBUTING.md: `rai-cli` → `raise-cli`, `src/rai_cli/` → `src/raise_cli/`
   - SECURITY.md: update supported versions table
   - CHANGELOG.md: fix compare URLs to `humansys-ai/raise-commons`, fix formatting
   - README: add CI badge, verify Python 3.14 claim

2. **S369.2 — Package Metadata & Deps** (XS)
   Make PyPI listing professional and deps clean.
   - Add `[project.urls]` to pyproject.toml (Homepage, Docs, Repository, Changelog)
   - Remove dead `tomli` dependency
   - Add Python 3.13 classifier
   - Run pip-audit / safety check

3. **S369.3 — CI Hardening** (S)
   CI should test what we claim to support.
   - Add Python 3.13 to test matrix
   - Verify CI badge URL works
   - Review release.yml for Trusted Publishers readiness

4. **S369.4 — Secrets & Hygiene Scan** (S)
   Ensure nothing internal leaks in published package.
   - Run secrets scanner (trufflehog or gitleaks)
   - Check .gitignore completeness
   - Verify sdist/wheel doesn't include internal artifacts
   - Review for internal references (URLs, emails, paths)

## Dependencies

```
S369.1 ──┐
S369.2 ──┼── independent, can parallelize
S369.3 ──┘
S369.4 ──── after S369.1-2 (builds on cleaned state)
```

## Done Criteria

- Senior dev can understand, install, and try the tool in <15 min
- All community docs accurate (no stale names, URLs, versions)
- PyPI metadata complete with project URLs
- CI tests all supported Python versions
- No secrets or internal references in published artifacts
- `rai release check` passes
- Ready to bump 2.2.1 and publish to PyPI
