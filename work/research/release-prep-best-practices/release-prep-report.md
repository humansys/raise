# Research Report: Release Preparation Best Practices

**Question:** What constitutes a "proper" release for a developer framework that claims reliability?
**Context:** RaiSE v2.3.0 — Python CLI framework, PyPI distribution, Jira/Confluence integrations
**Sources:** 13 (see evidence-catalog.md)
**Date:** 2026-03-23

---

## Executive Summary

A "proper" release for a reliability-focused framework covers **7 dimensions**, not just "bump version and publish." The gap between ad-hoc and professional releases is primarily in **documentation, verification, and communication** — the code is usually ready before the release is.

**Confidence: HIGH** — 11/13 sources converge on the same core dimensions.

---

## Claim 1: A release has 3 phases, not 1

**Sources:** S2, S8, S9, S10 (4 sources)
**Confidence:** HIGH

| Phase | Activities |
|-------|-----------|
| **Pre-release** | Scope audit, changelog, docs, migration guide, security scan, test suite |
| **Release** | Version bump, tag, build, TestPyPI, PyPI publish, GitHub release |
| **Post-release** | Smoke test, announcement, monitoring, hotfix readiness |

Most teams only do the middle phase. The pre and post phases are what differentiate a reliable release.

---

## Claim 2: Changelog is the minimum viable documentation

**Sources:** S3, S4, S5, S6, S8, S11 (6 sources)
**Confidence:** HIGH

Every source agrees: a proper changelog is **non-negotiable**. The standard format (Keep a Changelog / pyOpenSci):

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Deprecated
- Features that will be removed

### Removed
- Removed features (breaking)

### Fixed
- Bug fixes

### Security
- Vulnerability patches
```

**Key principles:**
- Written for humans, not machines
- Every version gets an entry
- Unreleased section at top, promoted at release
- Link versions to diffs/tags

---

## Claim 3: Breaking changes require migration guidance proportional to impact

**Sources:** S5, S6, S11 (3 sources)
**Confidence:** HIGH

Pydantic's approach is the gold standard:
1. **Deprecation warnings** before removal (at least 1 minor version)
2. **Migration guide** with before/after examples
3. **Automated migration tool** (for major versions)
4. **Retained old API** with DeprecationWarning during transition

For minor releases (like v2.3.0), the minimum is:
- Document what changed and why
- Provide before/after examples for any API changes
- Note if any behavior changed silently

---

## Claim 4: Security audit is a pre-release gate, not optional

**Sources:** S9, S10, S13 (3 sources)
**Confidence:** HIGH

Pre-release security includes:
- **Dependency audit** — known CVEs in deps (Snyk, pip-audit, safety)
- **Secrets scan** — no credentials in committed code
- **SAST** — static analysis for code vulnerabilities

RaiSE already does this (RAISE-295 security fixes in v2.3.0), but it should be a **gate**, not a separate epic.

---

## Claim 5: TestPyPI before PyPI

**Sources:** S2, S8 (2 sources)
**Confidence:** MEDIUM

Best practice is to publish to TestPyPI first and verify:
- Package installs correctly
- CLI entry points work
- Dependencies resolve

**Contrary evidence:** Many frameworks skip this for minor/patch releases, only doing it for major versions. Trade-off: speed vs. safety.

---

## Claim 6: A release announcement is part of the release, not an afterthought

**Sources:** S6, S9, S10 (3 sources)
**Confidence:** MEDIUM

Pydantic publishes blog-style release announcements for significant releases. Components:
- **Highlights** — 3-5 key changes
- **Contributor recognition**
- **Migration notes** (if breaking)
- **What's next** — roadmap tease

For a framework that claims reliability, the announcement builds trust. "We tested this, we documented this, here's what changed."

---

## Claim 7: Verification must cover the integration surface, not just unit tests

**Sources:** S9, S10, S13 (3 sources)
**Confidence:** HIGH

Beyond unit tests:
- **Smoke test** — core workflows end-to-end
- **Integration test** — external integrations (for RaiSE: Jira adapter, session roundtrip)
- **Regression test** — known bugs that were fixed stay fixed
- **Install test** — clean install from PyPI works

---

## Synthesis: The 7-Dimension Release Checklist

Based on convergence across sources, a "proper" release covers:

| # | Dimension | Patch | Minor | Major |
|---|-----------|:-----:|:-----:|:-----:|
| 1 | **Scope audit** — Jira vs git reconciliation | auto | auto | auto |
| 2 | **Changelog** — Keep a Changelog format | required | required | required |
| 3 | **Documentation** — epic docs, user/dev docs | skip | required | required + migration guide |
| 4 | **Security audit** — dep scan, SAST | verify clean | verify clean | full audit |
| 5 | **Test verification** — unit + integration + smoke | unit + smoke | full suite + integration | full + install test |
| 6 | **Release mechanics** — bump, tag, build, publish | PyPI direct | TestPyPI → PyPI | TestPyPI → PyPI |
| 7 | **Communication** — announcement, release notes | changelog only | release notes | blog post + migration guide |

---

## Contrary Evidence & Gaps

1. **TestPyPI is not universal** — many mature projects skip it for minor releases. Risk is low if CI is solid.
2. **Migration guides for minor releases** — most sources only mandate them for major versions. But if behavior changes, even minor releases benefit.
3. **No source covers "framework-specific" release prep** — things like skill validation, governance doc updates, graph rebuild are RaiSE-specific and not covered by generic checklists.

---

## Recommendation for RaiSE v2.3.0

**Confidence: HIGH**

Apply the 7-dimension checklist at the "Minor" level:

1. **Scope audit** — DONE (this session: Jira ↔ git reconciled, 36 tickets tagged)
2. **Changelog** — Write CHANGELOG.md in Keep a Changelog format
3. **Documentation** — `/rai-epic-docs` for E478, E494, E654 + update `/docs` for ACLI adapter and session identity
4. **Security** — Verify no open CVEs (RAISE-574/575/576 already fixed, verify clean)
5. **Verification** — Full test suite + session roundtrip + ACLI integration smoke test
6. **Release** — `/rai-publish` with bump minor (already uses GitHub Actions → PyPI)
7. **Communication** — Release notes in Confluence + GitHub release description

**RaiSE-specific additions (not in generic checklists):**
- Skill validation — `rai skill validate` across all skills
- Graph rebuild — `rai graph build` to verify knowledge graph integrity
- Gate check — `rai gate check --all` to verify all quality gates pass

---

## Sources

- [Microsoft Knack Release Checklist](https://github.com/microsoft/knack/blob/dev/docs/release-checklist.md)
- [Audrey Feldroy PyPI Release Checklist](https://gist.github.com/audreyfeldroy/5990987)
- [pyOpenSci CHANGELOG.md Guide](https://www.pyopensci.org/python-package-guide/documentation/repository-files/changelog-file.html)
- [Keep a Changelog](https://keepachangelog.com)
- [Pydantic Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [Pydantic v2.10 Release Announcement](https://pydantic.dev/articles/pydantic-v2-10-release)
- [Python Packaging — Versioning](https://packaging.python.org/en/latest/discussions/versioning/)
- [py-pkgs: Releasing and Versioning](https://py-pkgs.org/07-releasing-versioning.html)
- [PFLB Software Release Checklist](https://pflb.us/blog/successful-software-release-inclusive-checklist/)
- [Cortex Software Release Checklist](https://www.cortex.io/post/software-release-checklist)
- [Click/Pallets Releases](https://github.com/pallets/click/releases)
- [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/)
- [GetDX Production Readiness Checklist](https://getdx.com/blog/production-readiness-checklist/)
