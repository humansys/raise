# Plan: RAISE-1007

## Tasks

### T1: Unskip regression tests (RED)
- Remove `@pytest.mark.skip` from 3 tests:
  - `tests/daemon/test_runtime.py:272` — `test_governance_builds_hooks_dict`
  - `tests/daemon/test_governance_integration.py:69` — `test_hooks_dict_has_correct_structure`
  - `tests/daemon/test_governance_integration.py:140` — `test_full_pipeline_options`
- Verify: tests fail (RED) because hooks still disabled
- Commit: `test(RAISE-1007): unskip governance hook tests — RED`

### T2: Bump SDK + remove hack (GREEN)
- Edit `packages/rai-agent/pyproject.toml`: `claude-agent-sdk==0.1.48` → `claude-agent-sdk>=0.1.52`
- Edit `packages/rai-agent/src/rai_agent/daemon/runtime.py:305`: remove `and False` + BUG comments
- Run `uv lock` to update lockfile
- Verify: 3 tests pass (GREEN), all gates pass
- Commit: `fix(RAISE-1007): bump claude-agent-sdk >=0.1.52, re-enable governance hooks`

### T3: Cleanup + verify (REFACTOR)
- Remove `# noqa: SIM223` from the if-line
- Run full gate check on rai-agent package
- Commit: `refactor(RAISE-1007): remove noqa suppression from governance guard`
