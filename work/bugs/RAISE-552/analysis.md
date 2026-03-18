# Bug Analysis: RAISE-552

## Root Cause (5 Whys — XS)

Problem → `rai backlog search "RAISE-539"` falla con JQL error
Why1 → `McpJiraAdapter.search()` envía el query raw como JQL a jira_search
Why2 → No existe lógica de detección/wrapping entre input del usuario y JQL
Why3 → El diseño asumió que el caller siempre provee JQL válido (AR5 — "format is adapter-specific")
Root cause → El adapter no normaliza el input; expone detalles de implementación JQL al usuario

## Fix Approach

Agregar función `_to_jql(query: str) -> str` en `McpJiraAdapter` con tres casos:
1. `^[A-Z]+-\d+$` → issue key → `issue = RAISE-539`
2. Query ya contiene operadores JQL (=, !=, AND, OR, IN, IS, ~, ORDER BY) → pasar as-is
3. Cualquier otro texto plano → `text ~ "query"`

Fix location: packages/raise-pro/src/rai_pro/adapters/mcp_jira.py
