# Retrospective: RAISE-161 — Windows Compatibility Verification

## Summary
- **Story:** RAISE-161
- **Size:** XS (actual effort closer to S due to compat pattern)
- **Commits:** 5 (1 scope + 4 implementation)
- **Files touched:** 29 (1 created, 28 modified)
- **Tests:** 2021 passed, 9 new (compat module)

## What Went Well

- **Audit-first approach** — Exploring agent found all issues upfront, including the critical `fcntl` crash that would have bricked the tool on Windows. No surprises during implementation.
- **compat.py pattern** — Human caught that point fixes would scatter platform logic. The "stand on shoulders of giants" question elevated an XS tactical fix into an architectural pattern. Cost was minimal (~20 lines of module code) but value compounds on every future file.
- **Mechanical changes went fast** — Once compat was in place, wiring 15 path sites and 35 encoding sites was pure find-and-replace. Full test suite green after each commit.
- **Zero regressions** — 2021 tests, 0 new pyright errors. Cross-cutting changes without breakage.

## What Could Improve

- **Encoding gap is a class of debt, not a one-time fix** — New code can still write `write_text(content)` without encoding. No poka-yoke prevents it. A ruff rule or custom lint would catch this at PR time.
- **Docstring examples not updated** — `rai_base/__init__.py:17` and `skills_base/__init__.py:28` still show bare `read_text()` in docstrings. Cosmetic but inconsistent.

## Heutagogical Checkpoint

### What did you learn?
- Cross-platform Python tools converge on a `compat.py` anti-corruption layer pattern. `pip`, `poetry`, `virtualenv` all do this. The pattern is: platform guards in one module, rest of codebase imports abstractions.
- `Traversable.read_text()` from `importlib.resources` accepts `encoding` parameter — same API as `Path.read_text()`.
- `pyright` understands `sys.platform == "win32"` guards for type narrowing, but not boolean constants like `IS_WINDOWS`. Use the literal check inside functions that need narrowing.

### What would you change about the process?
- The human's question about strategic patterns before planning was the highest-value moment. Without it, we would have shipped 50 scattered fixes instead of 1 pattern + 50 mechanical applications. Consider adding "architectural pattern check" as a step in story-design for cross-cutting stories.

### Are there improvements for the framework?
- **New guardrail candidate:** "Platform-specific code MUST go through `rai_cli/compat.py`."
- **New guardrail candidate:** "All `read_text()`/`write_text()` calls MUST specify `encoding='utf-8'`."
- Both are enforceable via ruff custom rules or grep in CI.

### What are you more capable of now?
- Windows compatibility assessment for Python CLIs — now have a mental checklist: fcntl, path serialization, encoding, file URIs, chmod, shell=True assumptions.

## Patterns to Persist

1. **Compat anti-corruption layer** — Centralize platform-specific code in one module. Rest of codebase imports abstractions, never checks sys.platform.
2. **pyright needs literal sys.platform checks** — Boolean constants don't narrow types; the literal comparison does.

## Deferred Items
- Ruff/lint rule for missing `encoding=` parameter
- Docstring example updates in `rai_base` and `skills_base`
- `publish/check.py` shell=True + glob (CI-only, Linux-only)
- Test fixture hardcoded paths (when Windows CI exists)
