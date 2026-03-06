WHAT:      rai backlog get (y otros subcomandos) no muestra output ni error cuando el
           servidor MCP retorna isError=True. El usuario no puede distinguir si falló
           la autenticación, la red, o hay un bug.

WHEN:      Cualquier operación de backlog cuando el servidor MCP señala un error
           (credenciales incorrectas, issue inexistente, red caída, misconfiguration).

WHERE:     src/raise_cli/adapters/mcp_jira.py — todos los métodos async (get_issue,
           search, create_issue, update_issue, transition_issue, add_comment,
           get_comments, link_to_parent, link_issues, batch_transition)
           src/raise_cli/adapters/declarative/adapter.py — mismo patrón

EXPECTED:  El CLI muestra el mensaje de error del servidor MCP y retorna exit 1.
           Ejemplo: "Error: Jira client not available. Ensure JIRA_URL, JIRA_USERNAME,
           JIRA_API_TOKEN are set."

Done when: rai backlog get RAISE-144 con credenciales faltantes muestra el error MCP
           en stderr y retorna exit 1. Tests de regresión pasan. Todos los gates verdes.
