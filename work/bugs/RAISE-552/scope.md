# Bug Scope: RAISE-552

WHAT:      `rai backlog search "RAISE-539"` falla con JQL error en lugar de retornar resultados
WHEN:      Cuando el query no contiene operadores JQL — plain text, issue key, o palabra clave
WHERE:     packages/raise-pro/src/rai_pro/adapters/mcp_jira.py:233 (McpJiraAdapter.search)
EXPECTED:  Query plain (e.g. "RAISE-539" o "backlog search error") se convierte automáticamente
           a JQL válido antes de enviarse a Jira
Done when: `rai backlog search "RAISE-539"` retorna la issue correcta sin error
           `rai backlog search "issue = RAISE-539"` sigue funcionando (JQL explícito respetado)
           `rai backlog search "backlog error"` convierte a text ~ "backlog error" JQL

TRIAGE:
  Bug Type:    Functional
  Severity:    S2-Medium
  Origin:      Code
  Qualifier:   Missing
