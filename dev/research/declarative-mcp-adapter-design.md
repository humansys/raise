# Research: Declarative MCP Adapter Framework

> Date: 2026-03-01 | Session: SES-311 | Status: Design complete, pending epic formalization

## Problem

RaiSE integra servicios externos (Jira, Confluence) via MCP servers usando `McpBridge` + adapters Python dedicados. Cada adapter nuevo requiere ~400 LOC de Python (arg building, response parsing, config). Esto bloquea la integración de MCP servers como mcp-github, mcp-linear, mcp-gitlab — requiere trabajo de framework developer, no de usuario.

**Objetivo:** Permitir integrar cualquier MCP server escribiendo un YAML declarativo (~50-80 lineas) en lugar de codigo Python.

## Research Sources

| Source | Type | Key Insight |
|--------|------|-------------|
| [MCPorter](https://github.com/steipete/mcporter) | CLI generator (TS) | Zero-config discovery + schema extraction from MCP servers → CLI generation |
| [Microsoft MCP Gateway](https://github.com/microsoft/mcp-gateway) | Reverse proxy | Declarative REST API config, session-aware routing, K8s-native |
| [MCPProxy pattern](https://dev.to/algis/mcp-proxy-pattern-secure-retrieval-first-tool-routing-for-agents-247c) | Proxy middleware | Retrieval-first (BM25 top-5), quarantine-then-approve, 43% vs 13% accuracy |
| [mcpwhiz](https://mcpwhiz.com/) | OpenAPI → MCP | Auto-generate MCP server from Swagger/OpenAPI spec |
| [AWS API Gateway MCP](https://aws.amazon.com/about-aws/whats-new/2025/12/api-gateway-mcp-proxy-support/) | Cloud proxy | REST API → MCP-compatible endpoints |
| [Envoy AI Gateway](https://aigateway.envoyproxy.io/docs/capabilities/mcp/) | Edge proxy | MCP routing at infrastructure level |

### Three Patterns in Ecosystem

| Pattern | Representative | Approach | Config |
|---------|---------------|----------|--------|
| **CLI Generator** | MCPorter | Connect to MCP → extract schemas → generate standalone CLI | Auto-discovery + JSON |
| **Gateway/Proxy** | MS MCP Gateway, Envoy, AWS | Reverse proxy aggregating N servers, routes by tool name | REST API, K8s |
| **Retrieval-First** | MCPProxy | Aggregate servers, BM25 index, serve only top-N relevant tools | Quarantine + allow-list |

### Three Levels for RaiSE

| Level | Description | Complexity |
|-------|-------------|------------|
| **1 — Generic Bridge** | `rai mcp call <server> <tool> --args '{...}'` (already have McpBridge) | Done |
| **2 — Declarative Adapter** | YAML mapping protocol methods → MCP tools (THIS DESIGN) | Medium |
| **3 — Smart Discovery** | Auto-register + BM25 tool search by intent | High, future |

**Decision:** Level 2 first, Level 1 as escape hatch (already available), Level 3 as future enhancement.

---

## Architecture

```
.raise/adapters/github.yaml          <-- user writes this
        |
        v
DeclarativeMcpAdapter                <-- new generic class
  |-- reads YAML config
  |-- creates McpBridge (existing, no changes)
  |-- maps protocol methods -> MCP tool calls
  |-- parses responses -> Pydantic models (existing)
        |
        v
Registry discovery                   <-- extends registry.py
  |-- entry points (existing, priority)
  |-- .raise/adapters/*.yaml (new, fallback)
```

**Unchanged:** McpBridge, protocols.py, models.py, sync.py, existing adapters (Jira, Confluence, Filesystem).

---

## YAML Schema (example: GitHub)

```yaml
adapter:
  name: github
  protocol: pm                          # "pm" | "docs"
  description: "GitHub Issues via mcp-github"

server:
  command: uvx
  args: [mcp-github]
  env:
    - env: GITHUB_TOKEN
      flag: --token

methods:
  create_issue:
    tool: github_create_issue
    args:
      title: "{{ issue.summary }}"
      body: "{{ issue.description }}"
      repo: "{{ project_key }}"
    response:
      model: IssueRef
      fields:
        key: "{{ data.number | str }}"
        url: "{{ data.html_url }}"

  search:
    tool: github_search_issues
    args:
      query: "{{ query }}"
      per_page: "{{ limit }}"
    response:
      model: list[IssueSummary]
      items_path: data.items
      fields:
        key: "{{ item.number | str }}"
        summary: "{{ item.title }}"
        status: "{{ item.state }}"

  # Unsupported
  link_to_parent: null
  link_issues: null
```

## Expression Language (minimal, no Jinja2)

- `{{ param }}` -- method parameter
- `{{ issue.summary }}` -- dot access into objects/dicts
- `{{ data.field }}` -- response data access
- `{{ value | str }}` -- type coercion
- `{{ value | default('x') }}` -- fallback
- `{{ items | pluck('name') }}` -- extract field from list of dicts
- `{{ value | json }}` -- JSON serialize
- Literals without `{{ }}` -- passthrough

~100 LOC, no external dependencies.

---

## New Files

```
src/rai_cli/adapters/declarative/
  __init__.py              # Public API
  schema.py                # Pydantic models for YAML config (~80 LOC)
  expressions.py           # ExpressionEvaluator (~100 LOC)
  adapter.py               # DeclarativeMcpAdapter (~200 LOC)

tests/adapters/declarative/
  __init__.py
  test_schema.py
  test_expressions.py
  test_adapter.py
  fixtures/
    github.yaml            # Test fixture
    minimal.yaml
```

## Modified Files

- `src/rai_cli/adapters/registry.py` -- add `_discover_yaml_adapters()`, merge into `get_pm_adapters()` / `get_doc_targets()`

---

## Key Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | One generic class for PM and docs | `protocol` field in YAML determines which methods apply. Structural typing via `@runtime_checkable` validates. |
| D2 | Mini expression evaluator, not Jinja2 | Only need dot-access + 4 filters. 100 LOC vs complex dependency. |
| D3 | YAML in `.raise/adapters/` | Consistent with `.raise/jira.yaml`, `.raise/confluence.yaml`. |
| D4 | Entry points override YAML | Existing adapters (Jira, Confluence) unaffected. YAML for new integrations. |
| D5 | `null` = unsupported method -> `NotImplementedError` | Explicit and predictable. |
| D6 | `batch_transition` auto-loops if not declared | Only auto-derived method (loops over `transition_issue`). |
| D7 | No auto-discovery of tools | Level 2 declarative. Future scaffold could introspect schemas. |

---

## Story Decomposition

| # | Story | Size | Scope |
|---|-------|------|-------|
| S1 | Expression evaluator | S | `ExpressionEvaluator` + filters + unit tests |
| S2 | YAML schema models | S | `DeclarativeAdapterConfig` Pydantic models + validation tests |
| S3 | DeclarativeMcpAdapter (PM protocol) | M | Generic adapter class, all 11 PM methods, mocked bridge tests |
| S4 | YAML discovery in registry | S | `_discover_yaml_adapters()`, integration with existing discovery, tests |
| S5 | Docs protocol support | S | Extend for `AsyncDocumentationTarget`, 5 docs methods, tests |
| S6 | CLI validation command | XS | `rai adapter validate <file>` -- parse + validate YAML |
| S7 | Reference config + docs | XS | Working `github.yaml` or `linear.yaml` as example |

**Dependency chain:** S1 -> S2 -> S3 -> S4 (critical path). S5 after S3. S6, S7 independent after S3.

---

## Verification

1. **Unit tests:** Expression evaluator (dot access, filters, edge cases), schema validation (valid/invalid YAML), adapter (mocked bridge, all protocol methods)
2. **Integration test:** Load YAML fixture -> instantiate adapter -> verify protocol compliance via `isinstance()` check
3. **Registry test:** Place YAML in temp `.raise/adapters/` -> verify `get_pm_adapters()` discovers it
4. **Manual smoke test:** Write a real `github.yaml`, run `rai backlog search --adapter github "is:issue"` (requires mcp-github installed + GITHUB_TOKEN)

---

## Session Notes

- MCP Atlassian tools removed from Claude Code permissions (46 permissions cleaned from `.claude/settings.local.json`)
- `uv sync --extra mcp` needed to enable `rai backlog --adapter jira` (mcp is optional dependency)
- Fernando has NOT started RAISE-244 (rai-bugfix skill) — no branch, no commits
- This epic is a new epic (not under E325 or E144)
