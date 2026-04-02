# RAISE-1160: Dual Session ID System

WHAT:      Session close writes two records with different IDs — SES-NNN (legacy) and S-F-YYMMDD-HHMM (new) — for the same event
WHEN:      Every structured session close (--summary or --state-file)
WHERE:     close.py:process_session_close() calls append_session() → SES-NNN; session.py:close() calls write_session_entry() → S-F-*
EXPECTED:  One session ID (S-F-*), one index (sessions/{prefix}/index.jsonl), one record per session
Done when: process_session_close uses caller's session_id, stops writing to legacy index, session-state.yaml uses S-F-* ID
