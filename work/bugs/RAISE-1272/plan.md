# RAISE-1272: Plan

## Tasks

### T1: Regression test — artifact titles matched over containers (RED)
- Test that suggest_routing skips "ADR-041: Skill Runtime Orchestration" and matches "Architecture" instead
- Test that titles like "RAISE-123: Some Bug" are skipped
- Test that legitimate container titles still match
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_config_gen.py -x -k "artifact"` — FAILS
- Commit: `test(RAISE-1272): regression test for artifact-title filtering in suggest_routing`

### T2: Filter artifact-like titles in suggest_routing (GREEN)
- Add `_is_artifact_title(title)` helper: returns True if title matches `WORD-NNN:` pattern (e.g., "ADR-041:", "RAISE-123:")
- In suggest_routing, skip children where `_is_artifact_title(child.title)` is True
- Verify: `uv run pytest packages/raise-cli/tests/adapters/test_confluence_config_gen.py -x` — PASSES
- Commit: `fix(RAISE-1272): skip artifact-like titles in suggest_routing`
