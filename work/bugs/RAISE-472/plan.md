# RAISE-472 Plan — MCP isError silently swallowed

## Tier: S | TDD order | Commit after each task

---

## Task 1 — Tests de regresión RED (McpJiraAdapter)

Agregar helper `_err()` y tests en `tests/adapters/test_mcp_jira.py` que verifican que
cada método lanza `McpBridgeError` cuando `result.is_error=True`.

Métodos a cubrir: get_issue, create_issue, update_issue, transition_issue,
add_comment, get_comments, search.

```python
def _err(msg: str) -> McpToolResult:
    return McpToolResult(is_error=True, error_message=msg)
```

Verificación:
  uv run pytest tests/adapters/test_mcp_jira.py -k "is_error" -v  # DEBE FALLAR (RED)

Commit: test(RAISE-472): regression tests RED — McpJiraAdapter.is_error propagation

---

## Task 2 — Tests de regresión RED (DeclarativeMcpAdapter)

Agregar tests en `tests/adapters/declarative/test_adapter.py` que verifican que
DeclarativeMcpAdapter lanza McpBridgeError cuando result.is_error=True en cualquier
llamada a bridge.call().

Verificación:
  uv run pytest tests/adapters/declarative/test_adapter.py -k "is_error" -v  # DEBE FALLAR

Commit: test(RAISE-472): regression tests RED — DeclarativeMcpAdapter.is_error propagation

---

## Task 3 — Fix McpJiraAdapter (GREEN)

En `src/raise_cli/adapters/mcp_jira.py`, agregar verificación de `result.is_error`
antes de cada `_parse_*()` en los métodos:
  get_issue, create_issue, update_issue, transition_issue,
  add_comment, get_comments, search

Patrón:
  result = await self._bridge.call(...)
  if result.is_error:
      raise McpBridgeError(result.error_message)
  return self._parse_*(result)

(link_to_parent y link_issues no parsean respuesta — no requieren cambio)

Verificación:
  uv run pytest tests/adapters/test_mcp_jira.py -v
  uv run pyright src/raise_cli/adapters/mcp_jira.py
  uv run ruff check src/raise_cli/adapters/mcp_jira.py

Commit: fix(RAISE-472): propagate MCP isError in McpJiraAdapter — raise McpBridgeError

---

## Task 4 — Fix DeclarativeMcpAdapter (GREEN)

En `src/raise_cli/adapters/declarative/adapter.py`, agregar verificación de
`result.is_error` en los métodos del adaptador declarativo.

Verificación:
  uv run pytest tests/adapters/declarative/test_adapter.py -v
  uv run pyright src/raise_cli/adapters/declarative/adapter.py
  uv run ruff check src/raise_cli/adapters/declarative/adapter.py

Commit: fix(RAISE-472): propagate MCP isError in DeclarativeMcpAdapter

---

## Task 5 — Gates completos + reproducción invertida

Verificar que todos los gates pasan y que el bug ya no reproduce.

  uv run pytest tests/ -x -q
  uv run pyright src/
  uv run ruff check src/ tests/
  export $(grep -v '^#' .env | xargs) && rai backlog get RAISE-144 -a jira  # debe mostrar output

Commit: (solo si hay ajustes menores de cleanup)
