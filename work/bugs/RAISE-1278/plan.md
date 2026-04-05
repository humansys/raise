# RAISE-1278: Plan

## T1: Regression test — lowercase work_id creates uppercase path
- Write test that `write_record` with `work_id="s1051.6"` creates dir `S1051.6/`
- Write test that `read_record(work_id="s1051.6")` finds record written as `S1051.6`
- Verify: `uv run pytest packages/raise-cli/tests/memory/test_learning.py -x`
- Commit: `test(RAISE-1278): regression test for work_id casing normalization`

## T2: Fix — normalize work_id in LearningRecord model and read_record
- Add `field_validator("work_id")` to `LearningRecord` that calls `.upper()`
- Normalize `work_id` to uppercase in `read_record()` before path construction
- Verify: `uv run pytest packages/raise-cli/tests/memory/test_learning.py -x`
- Commit: `fix(RAISE-1278): normalize work_id to uppercase in learning record I/O`

## T3: Migrate existing lowercase directories
- Rename lowercase dirs to uppercase, merge if both exist (keep richer record)
- Delete empty/skeleton duplicates
- Verify: `find .raise/rai/learnings/ -type d | grep -E '/[a-z]' | grep -v rai-`
- Commit: `chore(RAISE-1278): migrate lowercase learning record dirs to uppercase`
