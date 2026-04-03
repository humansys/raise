WHAT:      4 SonarQube bugs — 2x S3923 (identical if-blocks), 2x S5850 (regex precedence)
WHEN:      Detected by SonarQube local analysis during v2.3.0 cycle
WHERE:     scanner.py:1561, python.py:91, adr.py:81, changelog.py:18
EXPECTED:  Zero BUG-type Sonar issues
Done when: All 4 issues resolved, Sonar clean

TRIAGE:
  Bug Type:    Logic
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Incorrect

NOTE: Umbrella ticket — sub-bugs RAISE-534 (S3923 scanner), RAISE-535 (S3923 python.py),
RAISE-536 (S5850 changelog), RAISE-537 (S5850 adr.py) each have full artifacts.
