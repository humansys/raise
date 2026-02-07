# RES-PYPI-WIN-001: PyPI Publishing & Windows Compatibility

> Research for F&F pre-launch distribution strategy.

**Date:** 2026-02-07
**Session:** SES-081
**Trigger:** F&F release (Feb 9) — need to distribute raise-cli to testers
**Status:** Complete

---

## Research Questions

1. How does PyPI work? Philosophy, costs, requirements, process.
2. How do professional Python tools handle multiplatform support?
3. What % of developers use Windows / WSL / Claude Code on Windows?
4. Is raise-cli Windows-compatible?

---

## Findings

### 1. PyPI Publishing

**Key facts:**
- Free, run by Python Software Foundation (non-profit)
- 2FA mandatory since Jan 2024 (TOTP or security key)
- Passwords no longer accepted — API tokens or Trusted Publishers only
- Version numbers are permanent (can't re-upload same version)
- Pre-release versions (`2.0.0a1`) invisible to `pip install` by default — users need `--pre`
- Name `raise-cli` is **available** (verified 2026-02-07)
- TestPyPI exists for dry runs (separate account/system)

**Publishing with uv:**
```bash
uv build
uv publish --token pypi-YOUR_TOKEN
```

**sdist security:** Default hatch config leaks entire repo. Fixed with explicit include:
```toml
[tool.hatch.build.targets.sdist]
include = ["/src/raise_cli/", "/LICENSE", "/README.md", "/pyproject.toml"]
```

**Sources:**
- [PyPI Documentation](https://pypi.org/)
- [PyPI 2025 Year in Review](https://blog.pypi.org/posts/2025-12-31-pypi-2025-in-review/)
- [uv Publishing Guide](https://docs.astral.sh/uv/guides/package/)
- [Python Packaging User Guide](https://packaging.python.org/tutorials/packaging-projects/)

---

### 2. Multiplatform Support in Python Tools

**Industry standard: `platformdirs`** (383M downloads/month, 3,300+ dependents)

| Tool | Platform Library | Approach |
|------|-----------------|----------|
| Black | `platformdirs` | platformdirs + env var override |
| Poetry | `platformdirs` | platformdirs + env var override (roaming) |
| pre-commit | None (manual XDG) | XDG everywhere, consistency over convention |
| pipx | `platformdirs` (Linux only) | Reverted on Win/Mac due to edge cases |
| ruff/uv | `etcetera` (Rust) | Rust equivalent of platformdirs |

**Universal 3-tier resolution pattern:**
```
1. Environment variable override   (highest priority)
2. Platform-specific directory      (platformdirs)
3. Hardcoded fallback              (lowest priority)
```

**raise-cli's current approach:** Manual XDG (matches pre-commit). Works on all platforms — creates `~/.config/raise/` on Windows (non-standard but functional).

**Recommendation:** Add `platformdirs` post-F&F for proper Windows paths (`%APPDATA%\raise`). Current approach is fine for F&F.

**Cautionary tale (pipx):** macOS `Application Support` has spaces (breaks shebangs). Windows `AppData` has sandbox issues. For config/cache/data, platformdirs is safe.

**Sources:**
- [platformdirs on PyPI](https://pypi.org/project/platformdirs/)
- [Poetry Configuration](https://python-poetry.org/docs/configuration/)
- [uv Storage](https://docs.astral.sh/uv/reference/storage/)
- [pipx platformdirs reversion](https://github.com/pypa/pipx/discussions/1247)
- [pre-commit platformdirs rejection](https://github.com/pre-commit/pre-commit/issues/1475)

---

### 3. Developer Platform Statistics

**Stack Overflow Developer Survey 2025 (49K respondents):**

| OS | Professional Use |
|----|-----------------|
| Windows | 49.5% |
| macOS | 32.9% |
| Ubuntu | 27.7% |
| WSL | 16.8% |
| Linux (non-WSL) | 16.7% |

- ~30-34% of Windows developers use WSL
- WSL adoption plateaued at ~16-17% since 2022

**Claude Code on Windows:**
- Anthropic publishes no platform breakdown
- ~20% of GitHub issues (~4,689 of 23K) mention Windows — significant adoption with friction
- Native Windows support added July 8, 2025 (v1.0.51) — only 7 months old
- Native install now recommended over WSL in official docs
- Requires Git for Windows (Git Bash)

**Sources:**
- [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/technology)
- [Claude Code Setup Docs](https://code.claude.com/docs/en/setup)
- [Claude Code GitHub Issues](https://github.com/anthropics/claude-code/issues)

---

### 4. raise-cli Windows Compatibility Audit

**Result: Fully compatible** (after path encoding fix)

| Area | Status | Details |
|------|--------|---------|
| Path construction | No issues | 100% pathlib, zero hardcoded separators |
| Subprocess calls | No issues | 1 call, list args, no `shell=True` |
| External tools | No issues | git, ripgrep, ast-grep have Windows binaries |
| Unix tool deps | None | No grep, sed, awk, find, cat, wc |
| Skills (SKILL.md) | No issues | Hooks run in Git Bash (Claude Code guarantees) |
| Git operations | No issues | Standard cross-platform commands |
| MEMORY.md path | **Fixed** | Was only replacing `/`, now handles `\` and `:` |

**One fix applied:**
- `config/paths.py:get_claude_memory_path()` — added backslash normalization and drive letter colon removal

**Known non-standard (acceptable for F&F):**
- XDG directories on Windows (`~/.config/raise/` instead of `%APPDATA%\raise`)
- `~/.rai/` path in skill documentation (works, but non-standard for Windows)

---

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Publish to PyPI as pre-release (`2.0.0a1`) | F&F users install via `pip install raise-cli --pre` |
| sdist restricted to `src/raise_cli/` only | Prevent private repo data leaking |
| Ship 18 skills (not 5) | F&F users need full lifecycle, not just discovery |
| Exclude skill-create and framework-sync | Internal/meta skills, not needed by F&F users |
| Fix Windows path encoding now | Emilio testing on Windows laptop |
| Defer platformdirs migration | Current XDG approach works, pre-commit precedent |
| Defer full Windows polish | Skills docs, XDG paths — post-F&F |

---

## Actions Taken

1. Fixed `pyproject.toml`: email, removed broken GitHub URLs, sdist include paths
2. Expanded `skills_base` from 5 to 18 skills with reference subdirectories
3. Updated `scaffold_skills()` to handle recursive file copying
4. Fixed `get_claude_memory_path()` for Windows backslashes and drive letters
5. Added Windows-specific tests for path encoding
6. All 1227 tests passing, 92.75% coverage

---

*Research ID: RES-PYPI-WIN-001*
*Evidence level: High (primary sources, official docs, survey data)*
