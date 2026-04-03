# Plan: RAISE-700

## Tasks (TDD order)

### T1: Add regression test for batch_keep propagation
Write a test that creates two conflicting skills and asserts batch_keep
prevents the second prompt from appearing. This is the only behavior not
covered by existing tests.
Verify: uv run pytest tests/onboarding/test_skills.py -k batch_keep -v
Commit: test(RAISE-700): regression test for batch_keep propagation in conflict

### T2: Extract _apply_skill_write()
Common write+copy_tree+manifest_update pattern, called from install,
auto_update, conflict, and overlay handlers.
Verify: uv run pytest tests/onboarding/test_skills.py
Commit: refactor(RAISE-700): extract _apply_skill_write helper

### T3: Extract _handle_new_skill()
Handles the "skill doesn't exist" install path. Removes 3 levels of nesting
from scaffold_skills loop body.
Verify: uv run pytest tests/onboarding/test_skills.py
Commit: refactor(RAISE-700): extract _handle_new_skill helper

### T4: Extract _handle_auto_update() and _resolve_conflict()
AUTO_UPDATE handler: skip_updates vs dry_run vs actual update.
CONFLICT handler: force/batch_overwrite → skip/batch_keep → dry_run →
                  interactive (_resolve_conflict_interactive).
Returns (batch_keep, batch_overwrite) tuple.
Verify: uv run pytest tests/onboarding/test_skills.py
Commit: refactor(RAISE-700): extract _handle_auto_update and _resolve_conflict

### T5: Extract _apply_skill_set_overlay()
Moves the skill-set overlay block out of scaffold_skills.
Verify: uv run pytest tests/onboarding/ -v
Commit: refactor(RAISE-700): extract _apply_skill_set_overlay helper

### T6: Refactor scaffold_skills + remove noqa
After all extractions, scaffold_skills should be a lean dispatcher.
Remove # noqa: C901 comment. Run full gate suite.
Verify: uv run pytest && uv run ruff check src/ tests/ && uv run ruff format --check src/ tests/ && uv run pyright
Commit: fix(RAISE-700): reduce scaffold_skills cognitive complexity 75→≤15

### T7: Post-fix Sonar scan
Run the Sonar scan to confirm S3776 is gone from skills.py:176.
