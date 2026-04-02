# Plan: RAISE-1160

## Task 1: Regression test (RED)
- Test: call process_session_close() with session_id="S-F-260401-0900"
- Assert result.session_id == "S-F-260401-0900"
- Assert NO write to personal/sessions/index.jsonl
- Verify: uv run pytest tests/session/test_close.py -x
- Commit: "test(RAISE-1160): regression test — process_session_close uses caller session_id"

## Task 2: Fix process_session_close (GREEN)
- When session_id provided: set result.session_id = session_id, skip append_session()
- When session_id is None: fall back to append_session() (legacy compat)
- Verify: uv run pytest tests/session/test_close.py -x
- Commit: "fix(RAISE-1160): use caller session_id, skip legacy append_session"

## Task 3: Verify full gate pass
- Run all 4 gates: test, lint, format, types
- Commit: only if refactor needed
