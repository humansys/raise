# RAISE-533: Log injection via user-controlled data in migration.py

WHAT:      `logger.warning("Invalid JSON in sessions index: %s", line[:50])` logs unsanitized user input
WHEN:      When parsing sessions/index.jsonl with invalid JSON lines
WHERE:     src/raise_cli/onboarding/migration.py:51
EXPECTED:  User-controlled data sanitized before logging (strip newlines, control chars)
Done when: Logged data cannot inject fake log entries via newlines or control characters
