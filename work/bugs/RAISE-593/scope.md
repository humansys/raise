WHAT:      rai backlog -a jira gives cryptic error when jira.yaml missing — no guided setup
WHEN:      Any rai backlog command with -a jira in project without .raise/jira.yaml
WHERE:     Adapter instantiation — raw "config not found" error with file path
EXPECTED:  Actionable message or guided setup flow
Done when: Missing config produces clear guidance, not raw file-not-found

TRIAGE:
  Bug Type:    UX
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Missing

STATUS: Valid — error message is still cryptic, no guided setup exists.
