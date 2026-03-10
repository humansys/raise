# Design: HF-2 Publish Skill

## What & Why

**Problem:** No formalized quality gate or publish workflow. Version strings are already drifted (`pyproject.toml` says `2.0.0-alpha.7`, `__init__.py` says `2.0.0-alpha.1`, neither is PEP 440 compliant). Publishing is manual and ad-hoc with no pre-flight checks.

**Value:** A reliable, repeatable release process that catches issues before they reach PyPI. Prevents broken releases, version drift, and missing changelog entries.

## Research

RES-PUBLISH-001 surveyed 20+ primary sources (pydantic, pytest, FastAPI, ruff, uv, pip, httpx, Poetry, hatch). See `work/research/RES-PUBLISH-001/`.

## Architectural Context

**Module:** `cli/commands/` — new `publish.py` command file
**Layer:** CLI (orchestration)
**Pattern:** Follows existing Typer command structure (`release_app`, `session_app`, etc.)
**New module:** `src/rai_cli/publish/` — publish logic (check gates, version bump)

## Approach

Two CLI commands + one Claude Code skill:

### `rai publish check`

Runs all quality gates locally. Reports pass/fail for each. Exits non-zero if any fail.

```bash
$ rai publish check

🔍 Pre-publish Quality Check
─────────────────────────────
✓ Tests pass (1770 passed, 10 skipped)
✓ Type checks clean (pyright: 0 errors)
✓ Lint clean (ruff: 0 issues)
✓ Security scan (bandit: 0 issues)
✓ Coverage threshold (92.74% >= 90%)
✓ Build succeeds (sdist + wheel)
✓ Package validates (twine check: OK)
✗ CHANGELOG.md has unreleased entries — FAIL: no CHANGELOG.md found
✗ Version PEP 440 compliant — FAIL: "2.0.0-alpha.7" is not valid

Result: 7/9 checks passed, 2 FAILED
```

**Gates (ordered):**

| # | Gate | Command | Required |
|---|------|---------|----------|
| 1 | Tests pass | `uv run pytest --tb=no -q` | MUST |
| 2 | Type checks | `uv run pyright src/` | MUST |
| 3 | Lint clean | `uv run ruff check src/` | MUST |
| 4 | Security scan | `uv run bandit -r src/ -q` | MUST |
| 5 | Coverage | `uv run pytest --cov --cov-fail-under=90 -q` | MUST |
| 6 | Build | `uv build` | MUST |
| 7 | Package valid | `uv run twine check dist/*` | MUST |
| 8 | CHANGELOG | Check `CHANGELOG.md` has `## [Unreleased]` entries | MUST |
| 9 | Version PEP 440 | Validate version string format | MUST |
| 10 | Version sync | `pyproject.toml` matches `__init__.py` | MUST |

### `rai publish release`

Orchestrates the full release:

```bash
$ rai publish release --bump minor

Pre-publish check... ✓ All 10 gates passed

Current version: 2.0.0a7
Bump type: minor
New version: 2.1.0

Steps:
  1. Update pyproject.toml: 2.0.0a7 → 2.1.0
  2. Update __init__.py: 2.0.0a7 → 2.1.0
  3. Update CHANGELOG.md: [Unreleased] → [2.1.0] - 2026-02-14
  4. Commit: "release: v2.1.0"
  5. Tag: v2.1.0
  6. Push commit + tag → triggers GitHub Actions release

Proceed? [y/N]: y

✓ Version bumped
✓ Changelog updated
✓ Committed: release: v2.1.0
✓ Tagged: v2.1.0
✓ Pushed to origin

Release v2.1.0 published. GitHub Actions will handle PyPI upload.
Verify at: https://github.com/humansys/raise/actions
```

**Arguments:**

| Arg | Type | Description |
|-----|------|-------------|
| `--bump` | `major\|minor\|patch\|alpha\|beta\|rc\|release` | Version bump type |
| `--version` | `str` | Explicit version (overrides --bump) |
| `--dry-run` | `bool` | Show what would happen without executing |
| `--skip-check` | `bool` | Skip quality gates (dangerous, requires confirmation) |
| `--project` | `Path` | Project root (default: `.`) |

**Version bump logic:**

| Current | `--bump` | Result |
|---------|----------|--------|
| `2.0.0a7` | `alpha` | `2.0.0a8` |
| `2.0.0a7` | `beta` | `2.0.0b1` |
| `2.0.0a7` | `rc` | `2.0.0rc1` |
| `2.0.0a7` | `release` | `2.0.0` |
| `2.0.0` | `patch` | `2.0.1` |
| `2.0.0` | `minor` | `2.1.0` |
| `2.0.0` | `major` | `3.0.0` |

### `/rai-publish` skill

Guides the human through publish workflow. Adds judgment:
- Reviews changes since last release (`git log`)
- Suggests version bump type
- HITL confirmation before push

## Components Affected

| Component | Change |
|-----------|--------|
| `src/rai_cli/publish/__init__.py` | **Create** — new module |
| `src/rai_cli/publish/check.py` | **Create** — quality gate runner |
| `src/rai_cli/publish/version.py` | **Create** — version parsing, bumping, PEP 440 validation |
| `src/rai_cli/publish/changelog.py` | **Create** — changelog parsing and updating |
| `src/rai_cli/cli/commands/publish.py` | **Create** — Typer CLI commands |
| `src/rai_cli/cli/main.py` | **Modify** — register `publish_app` |
| `CHANGELOG.md` | **Create** — initial changelog in Keep a Changelog format |
| `.claude/skills/rai-publish/SKILL.md` | **Create** — publish skill |
| `tests/publish/` | **Create** — tests for all new modules |

## Pre-requisite Fix: PEP 440 Version

Before publish can work, fix version strings:
- `pyproject.toml`: `2.0.0-alpha.7` → `2.0.0a7`
- `__init__.py`: `2.0.0-alpha.1` → `2.0.0a7` (sync to pyproject.toml)

## Acceptance Criteria

**MUST:**
1. `rai publish check` runs all 10 gates and reports pass/fail
2. `rai publish release` bumps version, updates changelog, commits, tags, pushes
3. Version sync between `pyproject.toml` and `__init__.py` is enforced
4. `--dry-run` shows plan without executing
5. Human confirmation required before push

**SHOULD:**
1. Rich formatted output with pass/fail indicators
2. `--skip-check` requires explicit "I know what I'm doing" confirmation
3. `/rai-publish` skill provides guided workflow

**MUST NOT:**
1. Publish directly to PyPI (GitHub Actions handles that via Trusted Publishers)
2. Modify existing `release` command (different concern — graph inspection)
3. Allow non-PEP-440 versions

## Testing Approach

- Unit tests for version parsing/bumping (pure logic, no side effects)
- Unit tests for changelog parsing/updating (file content manipulation)
- Integration tests for check gates using subprocess (verify commands run)
- CLI tests using Typer test runner for command registration

**DO NOT** test actual git push or PyPI upload — mock those boundaries.
