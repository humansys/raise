WHAT:      session start does not load next_session_prompt from previous session close
WHEN:      rai session start --context after a session with next_session_prompt saved
WHERE:     session bundle loading
EXPECTED:  next_session_prompt appears in context bundle output
Done when: session start displays previous session's next_session_prompt

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing

STATUS: Invalid — verified working 2026-04-01. next_session_prompt loaded correctly at session start.
         Likely fixed by RAISE-214 (f57b89ca) or RAISE-163 (3118345f).
