# E369: Open Source Readiness Audit — Retrospective

## Summary

Audited and fixed 17+ issues across documentation, package metadata, CI,
security, and naming consistency to prepare raise-commons for open source
publication. Published raise-cli, raise-core, and raise-server v2.2.1 to PyPI.

## Metrics

| Metric | Value |
|--------|-------|
| Stories planned | 4 |
| Stories added | 1 (S369.5 — textual rename) |
| Stories completed | 5 |
| Total commits | ~55 |
| Tests | 3,671 passed, 16 skipped |
| Coverage | 91% |
| Issues found | 17 (planned) + 35 text refs + 3 URL corrections |
| Issues fixed | All |
| PyPI packages published | 3 (raise-cli, raise-core, raise-server) |

## Deliverables

1. All community docs accurate (README, CONTRIBUTING, SECURITY, CHANGELOG)
2. PyPI metadata complete with project URLs
3. CI tests Python 3.12 + 3.13
4. CI badge in README
5. No secrets or internal references in published code
6. Trusted Publishers documented (release.yml already compatible)
7. Textual rename rai-cli → raise-cli complete (35 refs)
8. GitHub URLs corrected to humansys/raise
9. v2.2.1 published to PyPI (all 3 packages)
10. Consolidated audit results document for dev team

## What Went Well

- **Framing the audit as "senior dev first contact"** gave clear evaluation
  criteria and kept scope focused on what actually matters
- **Gemba-first approach** — scanning the actual repo before planning stories
  caught real issues (stale URLs, dead deps) vs hypothetical ones
- **Story-run automation** — 4 stories through full lifecycle in one session
- **pip-audit clean** — zero vulnerabilities was a pleasant surprise
- **sdist/wheel audit** — building and inspecting the actual artifacts gave
  concrete confidence vs assumptions

## What Could Improve

- **GitHub URL was wrong throughout** — we corrected CHANGELOG URLs from
  humansys/raise to humansys-ai/raise-commons, then had to revert because
  the actual repo IS humansys/raise. Double-checking the remote before
  bulk-replacing would have saved a round trip
- **Coverage number was wrong** — reported 29% initially (included rai_pro
  in measurement scope), actual was 91%. Should have scoped the coverage
  command to the published package from the start
- **Pending publisher limitation** — PyPI only allows one pending publisher
  at a time, which we discovered mid-process. Researching this upfront
  would have saved time
- **S369.5 was unplanned** — the textual rename was out of scope for
  RAISE-463 by design, but was clearly needed for this audit. Should have
  been identified during epic design as a known gap to close

## Patterns

- **PAT-E-599:** Audit framing matters — "what would a senior dev check in
  15 minutes" produces better scope than "run security checklist". Human
  evaluation criteria > tool-driven checklists.
- **PAT-E-600:** Always verify remote URLs before bulk-replacing repo
  references. `git remote -v` is the source of truth, not docs or memory.
- **PAT-E-601:** PyPI pending publishers are limited to one at a time.
  For multi-package monorepos, use an account-scoped API token for first
  publish, then add Trusted Publishers per-project afterward.
- **PAT-E-602:** Scope coverage measurements to the published package
  (`--cov=src/raise_cli`), not the entire src/ tree which may include
  unpublished code with different coverage profiles.

## Parking Lot

- Dead `tomli` import fallback in `settings.py` (unreachable, harmless)
- Automated secrets scanner in CI (trufflehog/gitleaks)
- Add Trusted Publishers to each PyPI project now that they exist
- Deprecate old `rai-cli` package on PyPI (redirect to raise-cli)
- Coverage improvement epic (91% → 95%+)
