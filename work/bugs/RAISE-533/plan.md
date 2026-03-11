# RAISE-533: Fix Plan

### T1: Regression test RED
- Test that logging invalid JSON lines does NOT produce newlines in the log output
- Mock logger, feed a line with `\n` embedded, assert the logged string has no newlines

### T2: Sanitize logged data
- Replace newlines and control characters in user-controlled data before logging
- Also check line 41 (`logger.warning("Sessions index not found: %s", sessions_path)`) — path is internal, not user-controlled, so OK
