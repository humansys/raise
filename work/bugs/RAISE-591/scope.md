WHAT:      S7503 — async def can_publish has no await in mcp_confluence.py
WHEN:      Detected by SonarQube during v2.3.0 cycle
WHERE:     packages/raise-pro/src/rai_pro/adapters/mcp_confluence.py:115
EXPECTED:  NOSONAR with justification (async required by protocol)
Done when: Suppression annotated with rationale

TRIAGE:
  Bug Type:    Interface
  Severity:    S3-Low
  Origin:      Design
  Qualifier:   Incorrect
