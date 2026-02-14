# Evidence Catalog: RES-PUBLISH-001

## Quality Gates

**Source**: Pydantic CI/CD Pipeline (DeepWiki)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Single ci.yml with `alls-green` gate pattern. 3 type checkers (mypy, Pyright, Pyrefly). 16+ downstream integration tests. Release job gates on tag + all checks passing.

**Source**: FastAPI Test Workflow (GitHub)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: 100% coverage threshold enforced (`--fail-under=100`). Tests on Python 3.10, 3.12-3.14. Multi-OS matrix. CodSpeed benchmarks.

**Source**: pytest CI Workflows (GitHub)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Uses `hynek/build-and-inspect-python-package` for package validation. Towncrier for changelog. `prepare-release-pr` automated workflow + core team approval gate.

**Source**: hynek/build-and-inspect-python-package (GitHub)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Runs `check-wheel-contents` + `twine check --strict`. Prints directory trees. Sets SOURCE_DATE_EPOCH for reproducible builds. Used by pytest, attrs, structlog.

**Source**: Poetry release.yml (GitHub)
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Zero test gates in release workflow. Just build + version regex check + publish. Relies entirely on branch protection.

## Publishing Mechanics

**Source**: astral-sh/trusted-publishing-examples (GitHub)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Complete reference workflow: checkout → uv install → build → smoke test both wheel and sdist → `uv publish`. Trusted Publishers via OIDC.

**Source**: PyPI Trusted Publishers Docs
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: 4 fields: repo owner, repo name, workflow filename, environment name (optional but recommended). OIDC tokens expire automatically vs long-lived API tokens.

**Source**: uv Documentation (astral.sh)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: `uv publish` supports `--token`, `--check-url` (skip existing), attestation support. `uv build` produces sdist + wheel in dist/.

## Changelog Management

**Source**: Keep a Changelog (keepachangelog.com)
- **Type**: Primary (standard)
- **Evidence Level**: Very High
- **Key Finding**: Categories: Added, Changed, Deprecated, Removed, Fixed, Security. SemVer. Unreleased section at top. The format standard most projects converge on.

**Source**: Towncrier (twisted/towncrier)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Fragment-based. One file per change named `{issue}.{type}.md`. Avoids merge conflicts. Used by pytest, pip, Twisted, attrs, BuildBot. "Not about automation — about avoiding merge conflicts."

**Source**: Scriv (nedbat/scriv)
- **Type**: Primary
- **Evidence Level**: High
- **Key Finding**: Fragment-based alternative. Filenames use date/time + branch (no issue number needed). `scriv github-release` publishes to GitHub Releases.

**Source**: "Conventional changelogs suck" (Sophia Willows)
- **Type**: Secondary (analysis)
- **Evidence Level**: Medium
- **Key Finding**: Auto-generated changelogs from commits conflate developer-facing and user-facing logs. Commit messages describe code changes, not user impact.

## Version Management

**Source**: Python Packaging User Guide — Single Source Version
- **Type**: Primary (standard)
- **Evidence Level**: Very High
- **Key Finding**: Static in pyproject.toml is simplest. Dynamic from __init__.py via importlib.metadata. setuptools-scm/hatch-vcs from git tags for fully automated.

**Source**: Hatch Versioning Docs
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: `hatch version minor`, `hatch version release`. Regex-based version file update. Path-based source. Integrated with hatchling build backend.

## Release Automation

**Source**: Python Packaging Guide — Publishing with GH Actions
- **Type**: Primary (standard)
- **Evidence Level**: Very High
- **Key Finding**: Official two-phase pattern: build in one job (no credentials), publish in isolated environment job. TestPyPI first, PyPI on tag. "Separate building from publishing."

**Source**: Ruff Release Process (DeepWiki)
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Manual workflow_dispatch. Dry-run mode. Editorialize CHANGELOG, bump PR, merge, manually trigger. 18+ platform targets.

**Source**: Brett Cannon — "What to do when you botch a release"
- **Type**: Primary (authority)
- **Evidence Level**: Very High
- **Key Finding**: Yank is primary rollback. Cannot delete or re-upload same filename. Build numbers can shadow broken wheels. PEP 592 + PEP 763.

## Rollback

**Source**: PyPI Yanking Docs
- **Type**: Primary
- **Evidence Level**: Very High
- **Key Finding**: Yanked releases hidden from pip resolution but still installable with exact pin. Always provide a yank reason. Files are NOT deleted.
