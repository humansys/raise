WHAT:      S6395 (redundant group) + S5850 (regex precedence) in adr.py and changelog.py
WHEN:      Detected post-RAISE-536/537 — first fix was incomplete
WHERE:     governance/parsers/adr.py:81, publish/changelog.py:18,47
EXPECTED:  Regex grouping unambiguous, no NOSONAR needed
Done when: Sonar clean on affected regexes

TRIAGE:
  Bug Type:    Logic
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Incorrect
