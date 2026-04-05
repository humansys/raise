# RAISE-1272: Scope

WHAT:      suggest_routing() matches individual artifact pages (e.g., "ADR-041: Skill Runtime...") instead of container pages ("Architecture") because "adr" substring matches both
WHEN:      Running /rai-adapter-setup on a Confluence space where individual ADR pages are at the top level
WHERE:     packages/raise-cli/src/raise_cli/adapters/confluence_config_gen.py:111 — `if keyword in title_lower`
EXPECTED:  Should match container/category pages, not individual artifact pages
Done when: suggest_routing prefers container pages and skips artifact-like titles (containing ':' or ticket IDs)

TRIAGE:
  Bug Type:    Logic
  Severity:    S3-Low
  Origin:      Code
  Qualifier:   Incorrect
