# RAISE-1277: Plan

## T1: Add `check_learning_chain` function + tests (RED→GREEN)
- Add `check_learning_chain(work_id, base_dir, chain_type)` to `memory/learning.py`
  - `chain_type` = "story" or "epic" (determines which skills to check)
  - Returns dataclass `ChainStatus(work_id, expected, found, missing)`
  - Story chain: design, plan, implement, review
  - Epic chain: design, plan, close
- Write tests in `tests/memory/test_learning.py`:
  - Complete chain returns all found, empty missing
  - Partial chain returns correct found/missing
  - Empty chain returns all missing
- Verify: `uv run pytest packages/raise-cli/tests/memory/test_learning.py -x`
- Commit: `feat(RAISE-1277): add check_learning_chain function for record completeness`

## T2: Add `LearningChainGate` + tests (RED→GREEN)
- Create `gates/builtin/learning.py` with `LearningChainGate`
  - `gate_id = "gate-learning-chain"`
  - `workflow_point = "before:story:review"`
  - Derives work_id from current branch (story/sN.M/... pattern)
  - Reports found/missing as details, passes if all expected records present
- Register in pyproject.toml entry points
- Write tests in `tests/gates/test_learning_gate.py`
- Verify: `uv run pytest packages/raise-cli/tests/gates/test_learning_gate.py -x`
- Commit: `feat(RAISE-1277): add LearningChainGate for record completeness enforcement`

## T3: Add `rai learn check` CLI command + tests (RED→GREEN)
- Add `check` subcommand to `cli/commands/learn.py`
  - `rai learn check <work_id> [--chain story|epic] [--project .]`
  - Prints chain status table, exit 0 if complete, exit 1 if missing
- Write tests in `tests/cli/test_learn.py`
- Verify: `uv run pytest packages/raise-cli/tests/cli/test_learn.py -x`
- Commit: `feat(RAISE-1277): add rai learn check CLI for chain completeness`
