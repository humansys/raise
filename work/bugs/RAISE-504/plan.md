# RAISE-504: Plan

## T1: Remove `rai discover build` command and formatter

- Remove `build_command` function from `src/raise_cli/cli/commands/discover.py`
- Remove `format_build_result` from `src/raise_cli/output/formatters/discover.py`
- Remove any imports of removed functions
- Update tests in `tests/cli/commands/test_discover.py` if they test build
- Verify: `uv run pytest tests/ -x && uv run ruff check src/ && uv run pyright src/`
- Commit: `fix(RAISE-504): remove redundant rai discover build command`

## T2: Remove 4 deprecated discovery skills

- Delete `.claude/skills/rai-discover-start/`
- Delete `.claude/skills/rai-discover-scan/`
- Delete `.claude/skills/rai-discover-validate/`
- Delete `.claude/skills/rai-discover-document/`
- Delete `src/raise_cli/skills_base/rai-discover-start/`
- Delete `src/raise_cli/skills_base/rai-discover-scan/`
- Delete `src/raise_cli/skills_base/rai-discover-validate/`
- Delete `src/raise_cli/skills_base/rai-discover-document/`
- Verify: `uv run pytest tests/ -x && uv run ruff check src/ && uv run pyright src/`
- Commit: `fix(RAISE-504): remove 4 deprecated discovery skills`

## T3: Clean references

- Grep for remaining references to removed skills or unified.json in src/
- Update any docs, skills, or code that reference removed items
- Remove "Replaces:" line from `/rai-discover` SKILL.md (nothing to replace anymore)
- Verify: `uv run pytest tests/ -x && uv run ruff check src/ && uv run pyright src/`
- Commit: `fix(RAISE-504): clean references to removed discovery artifacts`
