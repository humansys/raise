# RES-PUBLISH-001: Open Source Python Release Best Practices

## Research Question

What are the established best practices for quality-gated release workflows in open source Python CLI tools?

**Decision this informs:** Design of `rai publish check` and `rai publish release` commands (HF-2).

## Key Findings

### 1. Quality gates belong at merge time, not release time

**Confidence: HIGH** (triangulated: pydantic, pytest, FastAPI, Poetry all confirm)

No mature project re-runs the full test suite inside the release workflow. They rely on branch protection requiring CI to pass before merge to main. The release is triggered by tagging a commit that already passed CI.

**Implication for us:** `rai publish check` should verify the *current state* is release-ready (tests pass, types clean, lint clean, etc.), but the release workflow itself trusts the tagged commit. The check is a local developer tool, not a CI gate.

### 2. Build validation IS a release gate

**Confidence: HIGH** (triangulated: pytest, attrs, structlog use `hynek/build-and-inspect-python-package`)

Package validation (`twine check --strict` + `check-wheel-contents`) is the one quality gate that runs *at release time*, not just at merge time. This catches packaging-specific issues (bad metadata, missing files, broken README rendering).

**Implication for us:** `rai publish check` should include `uv build` + `twine check` as a gate.

### 3. Fragment-based changelogs beat auto-generated

**Confidence: HIGH** (triangulated: pytest, pip, Twisted, attrs use towncrier; pyOpenSci recommends Keep a Changelog format)

Towncrier (fragment-based, one file per change) produces better user-facing changelogs than Conventional Commits auto-generation. The key insight: "It's not about automation. It's about avoiding merge conflicts on the changelog." (Hynek Schlawack)

**Counterpoint:** For a small team (1-2 people), fragment management is overhead. A manually-maintained CHANGELOG.md in Keep a Changelog format is simpler and sufficient. Towncrier shines with 5+ contributors.

**Implication for us:** Start with manual CHANGELOG.md in Keep a Changelog format. Consider towncrier when contributor count grows.

### 4. Trusted Publishing is the standard

**Confidence: VERY HIGH** (50,000+ projects, 20%+ of PyPI uploads, official PyPA recommendation)

OIDC-based Trusted Publishing eliminates stored API tokens. We already have this configured in `.github/workflows/release.yml`.

**Implication for us:** No change needed — already implemented.

### 5. Human gates remain universal

**Confidence: VERY HIGH** (zero mature projects fully automate)

Every mature project has at least one human decision point:
- **Tag creation** (pydantic — cheapest gate)
- **Workflow dispatch** (ruff, uv — most explicit)
- **Environment approval** (httpx, pytest deploy)

**Implication for us:** `rai publish release` should require explicit confirmation before tagging and pushing.

### 6. Version management: static in pyproject.toml is simplest

**Confidence: HIGH** (we already use this pattern)

Dynamic versioning from git tags (setuptools-scm, hatch-vcs) adds complexity. Static version in pyproject.toml with a bump command is the simplest approach for small teams.

**Implication for us:** `rai publish release` bumps version in pyproject.toml, commits, tags, pushes. Simple.

### 7. Yanking is the rollback strategy

**Confidence: VERY HIGH** (PyPI policy, PEP 592, PEP 763)

Cannot delete or re-upload same filename on PyPI. Yank hides from resolution. Fastest recovery: yank + bump + release.

**Implication for us:** Document rollback procedure in the skill. Not automated.

## Recommendation

**Decision:** Two-command publish workflow with local quality gates.

**Confidence: HIGH**

### `rai publish check`
Runs locally before release. Validates:
1. Tests pass (`uv run pytest`)
2. Type checks clean (`uv run pyright src/`)
3. Lint clean (`uv run ruff check src/`)
4. Security scan (`uv run bandit -r src/`)
5. Coverage threshold met (`uv run pytest --cov --cov-fail-under=90`)
6. Build succeeds (`uv build`)
7. Package validates (`twine check dist/*`)
8. CHANGELOG.md has unreleased entries
9. README.md renders correctly (via twine check)
10. No secrets detected (`detect-secrets scan`)

### `rai publish release`
Orchestrates the release:
1. Run `rai publish check` (must pass)
2. Prompt for version bump type (major/minor/patch/pre-release)
3. Move CHANGELOG.md unreleased entries to versioned section
4. Update version in pyproject.toml
5. Commit version bump + changelog
6. Create git tag (`v{version}`)
7. Push commit + tag (triggers `.github/workflows/release.yml`)
8. Display post-release verification checklist

### `/rai-publish` skill
Guides the human through the process. Adds judgment layer:
- Reviews what changed since last release
- Suggests version bump type based on changes
- HITL confirmation before tag push

**Trade-offs accepted:**
- Manual CHANGELOG over towncrier (team too small for fragment workflow)
- Static version over dynamic (simplicity)
- No TestPyPI step in v1 (can add later)
- No smoke test post-publish in v1 (can add later)

## Sources

See `sources/evidence-catalog.md` for full evidence catalog with 20+ primary sources.

Key references:
- [Python Packaging Guide — Publishing with GH Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [astral-sh/trusted-publishing-examples](https://github.com/astral-sh/trusted-publishing-examples)
- [hynek/build-and-inspect-python-package](https://github.com/hynek/build-and-inspect-python-package)
- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- [Towncrier](https://towncrier.readthedocs.io/en/stable/)
- [pytest RELEASING.rst](https://github.com/pytest-dev/pytest/blob/main/RELEASING.rst)
- [Pydantic CI/CD Pipeline](https://deepwiki.com/pydantic/pydantic/7.2-cicd-pipeline)
- [Brett Cannon — What to do when you botch a release](https://snarky.ca/what-to-do-when-you-botch-a-release-on-pypi/)
