# RAISE-593: Plan

## Tasks

### T1: Regression test — FileNotFoundError shows guidance (RED)
- Test that `resolve_entrypoint` on FileNotFoundError prints guidance text (not raw path)
- Test that other exceptions still show generic message
- Verify: `uv run pytest packages/raise-cli/tests/cli/commands/test_resolve.py -x -k file_not_found` — FAILS
- Commit: `test(RAISE-593): regression test for config-not-found guidance`

### T2: Catch FileNotFoundError with actionable message (GREEN)
- In `resolve_entrypoint` (line 86-93): catch `FileNotFoundError` before `Exception`
- Message: config file missing + suggest `rai adapter-setup` or manual creation
- Keep generic handler for other exceptions
- Verify: `uv run pytest packages/raise-cli/tests/cli/commands/test_resolve.py -x` — PASSES
- Commit: `fix(RAISE-593): actionable guidance when adapter config file missing`
