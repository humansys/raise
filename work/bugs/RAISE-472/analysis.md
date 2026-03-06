# RAISE-472 Analysis

## Método: 5 Whys (S — cadena causal única)

Problem → rai backlog get retorna vacío sin error cuando el servidor MCP falla

Why 1: _parse_issue_detail recibe McpToolResult(is_error=True, error_message="...") y
        retorna IssueDetail con todos los campos vacíos (result.data = {})

Why 2: Ningún método en McpJiraAdapter verifica result.is_error antes de invocar
        _parse_issue_detail, _parse_issue_ref, _parse_search_results, _parse_comments

Why 3: _parse_result() en bridge.py convierte isError=True correctamente a
        McpToolResult(is_error=True), pero los métodos upstream no leen ese flag —
        no hay convención documentada ni enforced de verificarlo

Why 4: isError es un campo estándar del protocolo MCP (Anthropic SDK CallToolResult)
        pero el contrato de "verificar is_error antes de parsear" nunca se estableció
        al diseñar los adaptadores

Root cause: Los adaptadores MCP (McpJiraAdapter, DeclarativeMcpAdapter) no honran
            el contrato del protocolo MCP — cuando el servidor señala isError=True,
            el error es silenciado en lugar de propagado.

## Evidencia

- bridge.py:191-218: _parse_result() distingue isError correctamente → McpToolResult
- mcp_jira.py:134-135: get_issue llama _parse_issue_detail sin verificar is_error
- mcp_jira.py:272-285: _parse_issue_detail usa result.data directamente (vacío si error)
- Diagnóstico directo: McpBridge con credenciales faltantes → isError=True,
  content="Jira client not available. Ensure server is configured correctly."
- isError: campo estándar en mcp.types.CallToolResult (Anthropic MCP Python SDK)

## Fix approach

En cada método async de McpJiraAdapter que llama bridge.call():
  result = await self._bridge.call(...)
  if result.is_error:
      raise McpBridgeError(result.error_message)
  return self._parse_*(result)

Aplica a: get_issue, create_issue, update_issue, transition_issue, add_comment,
          get_comments, search (link_to_parent y link_issues no parsean respuesta)

Mismo patrón en DeclarativeMcpAdapter.

El CLI ya maneja McpBridgeError en el catch de backlog.py → muestra error y exit 1.
