# Evidence Catalog: Release Preparation Best Practices

## Research Question
What constitutes a "proper" release preparation for a developer framework that claims reliability?

## Sources

### S1: Microsoft Knack Release Checklist
- **URL:** https://github.com/microsoft/knack/blob/dev/docs/release-checklist.md
- **Type:** Primary (production framework, Microsoft-maintained)
- **Evidence Level:** Very High
- **Key Finding:** Python CLI framework with formal release checklist: version bump in setup.py → PR → merge → tag on GitHub → publish to PyPI. Strict semver.
- **Relevance:** Direct analogue — Python CLI framework used by Azure CLI.

### S2: Audrey Feldroy PyPI Release Checklist
- **URL:** https://gist.github.com/audreyfeldroy/5990987
- **Type:** Secondary (community standard, widely referenced)
- **Evidence Level:** High
- **Key Finding:** Canonical checklist: update HISTORY.md → commit → bump version → run tests with tox → push → create GitHub release → verify PyPI listing displays correctly.
- **Relevance:** Establishes baseline for any Python package release.

### S3: pyOpenSci CHANGELOG.md Guide
- **URL:** https://www.pyopensci.org/python-package-guide/documentation/repository-files/changelog-file.html
- **Type:** Primary (community standard body)
- **Evidence Level:** Very High
- **Key Finding:** Changelog must include: version number (semver), release date, categorized changes (Added/Changed/Deprecated/Removed/Fixed/Security), contributor recognition. Unreleased section at top, promoted to versioned section at release.
- **Relevance:** Defines changelog standard for scientific Python — applicable to any Python package.

### S4: Keep a Changelog
- **URL:** https://keepachangelog.com
- **Type:** Primary (de facto standard)
- **Evidence Level:** Very High
- **Key Finding:** Categories: Added, Changed, Deprecated, Removed, Fixed, Security. Guiding principles: changelogs are for humans, every version should have an entry, same types of changes grouped, versions are linkable, latest version first.
- **Relevance:** Industry standard format. Already partially adopted by RaiSE.

### S5: Pydantic Migration Guide
- **URL:** https://docs.pydantic.dev/latest/migration/
- **Type:** Primary (major Python framework)
- **Evidence Level:** Very High
- **Key Finding:** Dedicated migration guide for major versions. Deprecation warnings before removal. Migration tool (automated). Retained old method names with DeprecationWarning. Comprehensive before/after examples.
- **Relevance:** Gold standard for breaking change communication in Python ecosystem.

### S6: Pydantic v2.10 Release Announcement
- **URL:** https://pydantic.dev/articles/pydantic-v2-10-release
- **Type:** Primary (release announcement pattern)
- **Evidence Level:** High
- **Key Finding:** Release announcement includes: summary of highlights, contributor count, new features with examples, deprecation notices, migration notes. Published as blog post.
- **Relevance:** Pattern for release communication beyond just changelog.

### S7: Python Packaging User Guide — Versioning
- **URL:** https://packaging.python.org/en/latest/discussions/versioning/
- **Type:** Primary (official Python packaging authority)
- **Evidence Level:** Very High
- **Key Finding:** Python uses PEP 440 versioning (compatible with but not identical to semver). Pre-release versions (alpha, beta, rc) supported. Version should be single source of truth in pyproject.toml.
- **Relevance:** Authoritative versioning standard for PyPI packages.

### S8: py-pkgs — Releasing and Versioning
- **URL:** https://py-pkgs.org/07-releasing-versioning.html
- **Type:** Secondary (educational, well-referenced)
- **Evidence Level:** High
- **Key Finding:** Release checklist: update changelog → bump version → build → test on TestPyPI → publish to PyPI → create GitHub release with tag → set up next dev version. Emphasizes testing on TestPyPI first.
- **Relevance:** Complete end-to-end release flow for Python packages.

### S9: PFLB Software Release Checklist
- **URL:** https://pflb.us/blog/successful-software-release-inclusive-checklist/
- **Type:** Secondary (industry guide)
- **Evidence Level:** Medium
- **Key Finding:** Pre-release categories: code quality (tests, linting, security scan), documentation (changelog, migration, API docs), environment (staging verification), communication (release notes, announcement). Post-release: monitoring, hotfix readiness.
- **Relevance:** Comprehensive categorization of release activities.

### S10: Cortex Software Release Checklist
- **URL:** https://www.cortex.io/post/software-release-checklist
- **Type:** Secondary (DevOps platform)
- **Evidence Level:** Medium
- **Key Finding:** Release readiness includes: feature complete verification, regression testing, security audit, documentation complete, rollback plan, stakeholder sign-off. Post-release: smoke tests, monitoring dashboards, incident response plan.
- **Relevance:** Enterprise perspective on release readiness.

### S11: Click/Pallets Release Pattern
- **URL:** https://github.com/pallets/click/releases
- **Type:** Primary (foundational Python CLI library)
- **Evidence Level:** Very High
- **Key Finding:** Each release has: version tag, changelog entry (categorized), Python version support matrix, deprecation notices with timeline. Dropped Python 3.7-3.9 in 8.2.0 with clear notice. Uses pyproject.toml + flit_core.
- **Relevance:** Direct analogue — the CLI library RaiSE's dependency (Typer) is built on.

### S12: python-semantic-release
- **URL:** https://python-semantic-release.readthedocs.io/en/latest/
- **Type:** Primary (automation tool)
- **Evidence Level:** High
- **Key Finding:** Automates: version bumping from commit messages, changelog generation, GitHub release creation, PyPI publishing. Supports conventional commits → semver mapping.
- **Relevance:** Shows what can be automated in a mature release pipeline.

### S13: GetDX Production Readiness Checklist
- **URL:** https://getdx.com/blog/production-readiness-checklist/
- **Type:** Secondary (DX-focused)
- **Evidence Level:** Medium
- **Key Finding:** Readiness dimensions: functionality (feature complete, edge cases), reliability (error handling, graceful degradation), observability (logging, metrics), security (dependency audit, secrets scan), documentation (runbooks, API docs).
- **Relevance:** "Reliability" framing aligns with RaiSE's positioning.
