# RAISE-1300: Scope

WHAT:      `generate_jira_config()` merges workflow states and issue types from all selected projects into a single global blob, including states from shared workflow schemes that belong to unrelated projects
WHEN:      Config generation with multiple selected projects (e.g., RAISE, RGTM, VE)
WHERE:     packages/raise-cli/src/raise_cli/adapters/jira_config_gen.py — `_merge_workflows()`, `_merge_issue_types()`
EXPECTED:  Workflow states and issue types organized per project in the projects section, not merged globally
Done when: Generated config has per-project workflow states and issue types in the projects dict; global workflow/issue_types sections removed

TRIAGE:
  Bug Type:    Interface
  Severity:    S2-Medium
  Origin:      Design
  Qualifier:   Incorrect
