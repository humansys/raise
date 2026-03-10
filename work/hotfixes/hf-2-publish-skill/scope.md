# Hotfix Scope: HF-2 Publish Skill

## Problem

No formalized release quality gate or publish workflow. Publishing to PyPI is manual and ad-hoc — version bump, build, upload done by hand with no systematic pre-flight checks. Risk of publishing broken or incomplete releases.

## In Scope

- `rai publish check` — quality gate command that runs all pre-publish validations
- `rai publish release` — version bump, changelog, tag, PyPI upload (only if check passes)
- `/rai-publish` skill — Claude Code skill for guided release workflow
- Quality gates: tests, types, lint, security, coverage, license compliance, changelog, docs

## Out of Scope

- GitHub Actions CI/CD automation (future — trusted publishers)
- Multi-platform test matrix
- Signed releases / SLSA provenance
- MkDocs deployment (separate parking lot item)
- Automated dependency updates (Dependabot/Renovate)
- Release candidates workflow

## Done Criteria

- [ ] `rai publish check` runs all quality gates and reports pass/fail
- [ ] `rai publish release` performs version bump, changelog update, git tag, PyPI upload
- [ ] Release blocked if any check fails
- [ ] `/rai-publish` skill guides the release workflow
- [ ] All existing tests pass
- [ ] New tests cover check and release flows
- [ ] Retrospective complete
