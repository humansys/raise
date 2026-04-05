# RAISE-1174: Scope

WHAT:      `rai docs search "plain text" -t confluence` fails with unhelpful CQL parse error
WHEN:      Plain text query passed to Confluence search (no CQL operators)
WHERE:     packages/raise-cli/src/raise_cli/adapters/confluence_client.py:search()
EXPECTED:  Plain text auto-wrapped in CQL `siteSearch ~ "..."` transparently
Done when: Plain text queries work, CQL passthrough preserved, regression tests exist

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
