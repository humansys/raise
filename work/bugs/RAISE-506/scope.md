# RAISE-506: Duplicate pattern references in session state

WHAT:      patterns_captured in LastSession lists same placeholder ID N times
           (e.g. ["PAT-SES-024", "PAT-SES-024", "PAT-SES-024"]) instead of
           the real pattern IDs returned by append_pattern().
WHEN:      Session close with multiple patterns captured.
WHERE:     src/raise_cli/session/close.py:253
EXPECTED:  patterns_captured contains actual unique pattern IDs (e.g. ["PAT-E-001", "PAT-E-002"]).
Done when: 1. patterns_captured uses real IDs from append_pattern results
           2. Regression test verifies unique real IDs in session state
