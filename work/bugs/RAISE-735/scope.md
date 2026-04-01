WHAT:      Stale 'raise' command references in CLI output, docstrings, and glossary
WHEN:      User sees 'raise' in CLI output when correct command is 'rai'
WHERE:     init.py, session.py, memory/__init__.py, glossary.md, 5 test files
EXPECTED:  All references use 'rai' consistently
Done when: No stale 'raise' command references in codebase

TRIAGE:
  Bug Type:    UX
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Incorrect

STATUS: Valid — PR #12 from elabx has the fix, pending review/merge.
