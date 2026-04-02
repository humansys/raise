WHAT:      Sonar S5754 — exception swallowed in _query_adapter without NOSONAR
WHEN:      Detected by SonarQube local analysis during v2.3.0 cycle
WHERE:     session/bundle.py:102 (except SystemExit block)
EXPECTED:  Suppression correctly annotated with justification
Done when: NOSONAR applied with rationale comment

TRIAGE:
  Bug Type:    Logic
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Missing
