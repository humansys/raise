WHAT:      promote_unreleased fails when [Unreleased] is the last section (no prior releases)
WHEN:      First release of a project — changelog has only [Unreleased] with no versioned sections below
WHERE:     src/raise_cli/publish/changelog.py:47 — regex lookahead missing \Z alternative
EXPECTED:  promote_unreleased works regardless of whether versioned sections exist below
Done when: Regex handles both cases: next section exists, and \Z (end of string)

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
