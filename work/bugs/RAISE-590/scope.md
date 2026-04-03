WHAT:      S3923 — identical if/else blocks in scanner.py and python.py
WHEN:      Detected by SonarQube during v2.3.0 cycle
WHERE:     discovery/scanner.py:1561, context/analyzers/python.py:91
EXPECTED:  No dead conditional logic
Done when: Identical branches collapsed or differentiated

TRIAGE:
  Bug Type:    Logic
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Extraneous
