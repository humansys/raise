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

## Planned Stories

1. **S369.1 — First Contact Audit** — README, quickstart, install experience, `rai --help`
2. **S369.2 — Trust Signals** — LICENSE, CONTRIBUTING, CI badge, CHANGELOG, test coverage visible
3. **S369.3 — Security & Deps** — vulnerability scan, secrets check, dep cleanup
4. **S369.4 — Walk the Talk** — error messages, PyPI metadata, repo reflects what it preaches

## Done Criteria

- Senior dev can understand, install, and try the tool in <15 min
- All critical/high security issues resolved
- Trust signals present and accurate (LICENSE, CONTRIBUTING, CI, CHANGELOG)
- Error messages are clear, not raw tracebacks
- `rai release check` passes
- Ready to bump 2.2.1 and publish to PyPI
