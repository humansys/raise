---
module: publish
bounded_context: tooling
layer: domain
status: active
maintainer: rai-cli-team
dependencies:
  - config
  - subprocess
constraints:
  - "MUST: All version strings are PEP 440 compliant"
  - "MUST: Changelog follows Keep a Changelog format"
  - "MUST: Quality gates run before any destructive operation"
  - "SHOULD: Use Rich for CLI output formatting"
code_imports:
  - re
  - subprocess
  - dataclasses
  - pathlib
  - datetime
  - typing
code_exports: []
code_components: 3
---

# Module: publish

## Purpose

Pre-publish quality gates and release orchestration for PyPI publishing. Validates version compliance, runs test/lint/security gates, manages CHANGELOG.md, and orchestrates git tag creation for GitHub Actions-based releases.

## Bounded Context

**Tooling** — Developer-facing CLI tools for project lifecycle management (testing, releasing, versioning).

## Architecture Layer

**Domain** — Pure business logic for version parsing, changelog manipulation, and quality gate execution. No external service dependencies beyond subprocess calls to local tools.

## Components

### version.py

PEP 440 version parsing, validation, and bumping.

**Key functions:**
- `is_pep440(version: str) -> bool` — Validate PEP 440 compliance
- `parse_version(version: str) -> VersionInfo` — Parse into structured components
- `bump_version(current: str, bump_type: BumpType) -> str` — Apply version bump
- `sync_version_files(new_version: str, *, pyproject_path: Path, init_path: Path) -> None` — Write version to multiple files

**Dependencies:** stdlib only (re, dataclasses, pathlib)

### changelog.py

Keep a Changelog format parsing and manipulation.

**Key functions:**
- `has_unreleased_entries(content: str) -> bool` — Check for entries under [Unreleased]
- `promote_unreleased(content: str, version: str, date: str) -> str` — Move unreleased entries to versioned section

**Dependencies:** stdlib only (re)

### check.py

Quality gate runner — executes 10 validation checks before publishing.

**Gates:**
1. Tests pass (pytest)
2. Type checks clean (pyright)
3. Lint clean (ruff)
4. Security scan (bandit)
5. Coverage threshold (pytest --cov)
6. Build succeeds (uv build)
7. Package validates (twine check)
8. CHANGELOG has unreleased entries
9. Version is PEP 440 compliant
10. Version sync (pyproject.toml == __init__.py)

**Key functions:**
- `run_checks(...) -> list[CheckResult]` — Execute all gates, return results

**Dependencies:** subprocess (for external commands), version.py, changelog.py

## Design Decisions

**Two-phase CLI pattern:**
- `rai publish check` — Read-only validation, safe to run anytime
- `rai publish release --dry-run` — Preview changes before execution
- `rai publish release` — Execute with HITL confirmation

**Why:** Destructive operations (git tag, push) require human confirmation. Separate validation phase allows pre-flight checks without risk.

**PEP 440 enforcement:**
- Rejects semver-style versions (`2.0.0-alpha.7`)
- Accepts PEP 440 pre-releases (`2.0.0a7`, `2.0.0b1`, `2.0.0rc1`)

**Why:** PyPI requires PEP 440. Enforcing at CLI level prevents upload failures.

## Data Flow

```
User → rai publish check
         ↓
  run_checks() → subprocess(pytest, pyright, ruff, bandit, uv build, twine)
         ↓
  CheckResult[] → Rich console output
         ↓
  Exit 0 (all pass) or 1 (any fail)

User → rai publish release --bump alpha
         ↓
  run_checks() [unless --skip-check]
         ↓
  bump_version("2.0.0a7", "alpha") → "2.0.0a8"
         ↓
  promote_unreleased(changelog, "2.0.0a8", today)
         ↓
  sync_version_files(pyproject, init)
         ↓
  git add + commit + tag
         ↓
  [HITL confirmation]
         ↓
  git push --follow-tags
         ↓
  GitHub Actions → PyPI Trusted Publishers → package published
```

## Testing Strategy

**Unit tests:** 57 tests covering version parsing, bump logic, changelog manipulation, quality gate execution (mocked subprocess).

**Integration tests:** Manual smoke tests for CLI commands (`--help`, `--dry-run`).

**No PyPI upload tests:** Actual publishing is handled by GitHub Actions. CLI only creates tags.

## Constraints

**MUST:**
- All version strings validated with `is_pep440()` before use
- CHANGELOG.md follows Keep a Changelog format (## [Unreleased], ## [X.Y.Z] - YYYY-MM-DD)
- Quality gates run before any destructive operation (unless `--skip-check` with explicit confirmation)

**SHOULD:**
- Use Rich library for CLI output formatting (✓/✗ icons, colored output)
- Subprocess commands timeout after 300s to prevent hangs

**MUST NOT:**
- Publish directly to PyPI (GitHub Actions handles this via Trusted Publishers)
- Allow non-PEP-440 versions to reach version files or git tags

## Related Modules

**Used by:**
- `cli/commands/publish.py` — Typer CLI commands that orchestrate publish workflows

**Uses:**
- `config` — For paths (if needed in future)
- `subprocess` — For external command execution (pytest, ruff, etc.)

## Migration Notes

**From:** No prior publish tooling — manual version bumps, manual CHANGELOG updates, manual git tags.

**To:** Automated quality gates + version bumping + changelog management + tag creation.

**Breaking changes:** None (new module, no prior API).

## Performance

**run_checks() timing:** ~10-30s depending on test suite size and coverage calculation.

**Bottleneck:** pytest with coverage is slowest gate (~8-12s for 1827 tests).

**Optimization opportunities:** None needed — quality gates are infrequent (pre-release only).

## Security

**Subprocess injection risk:** Mitigated by using `shell=True` with fixed command strings (no user input interpolation).

**Git tag deletion risk:** Tags are created but never deleted by CLI. Manual `git tag -d` required for rollback.

## Future Enhancements

- [ ] Add `rai publish changelog add` for interactive changelog entry creation
- [ ] Support `pyproject.toml`-only versioning (no `__init__.py` required)
- [ ] Add `--skip-gate` flag to skip individual gates (e.g., `--skip-gate security`)

## References

- **Research:** `work/research/RES-PUBLISH-001/` — PyPI publishing best practices
- **Design:** `work/hotfixes/hf-2-publish-skill/design.md`
- **ADR:** (none yet — consider ADR for two-phase CLI pattern)
