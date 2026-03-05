# MCP Server Tool Design Patterns: Synthesis Report

> Research date: 2026-02-25
> Sources: 12 (see `sources/evidence-catalog.md`)
> Decision context: rai-server FastAPI backend + future MCP server exposure

---

## Executive Summary

The strongest finding across sources is: **a good REST API is not a good MCP server**. The REST API and MCP tool layer serve fundamentally different consumers (human developers vs. LLM agents) and should be designed with different principles. However, they can share the same service/domain layer underneath.

**Recommendation for rai-server**: Design the REST API with clean domain boundaries (which naturally supports future MCP mapping), but do NOT try to make REST endpoints MCP-compatible from day 1. Instead, build a shared service layer that both the FastAPI routes and a future MCP server can consume.

---

## Triangulated Claims

### Claim 1: MCP tools should be outcome-oriented, not endpoint-oriented

**Confidence: Very High** (6 sources: S2, S3, S4, S5, S10, S12)

The most consistent finding across the literature. REST APIs are resource-centric (CRUD on entities), while MCP tools should be task-centric (what the user/agent wants to accomplish).

| Pattern | REST API | MCP Tool |
|---------|----------|----------|
| Order tracking | `GET /users/{id}`, `GET /orders?user_id=`, `GET /shipments?order_id=` | `track_order(email)` — calls all three, returns unified result |
| User management | `GET /users/{id}`, `PUT /users/{id}/name`, `PUT /users/{id}/email` | `manage_user_profile(user_id, name?, email?)` — orchestrates updates |
| Knowledge graph query | `GET /nodes?type=module`, `GET /edges?from=X`, `GET /nodes/{id}` | `explore_codebase(question)` — semantic search + graph traversal |

**Implication for rai-server**: The REST API should expose fine-grained CRUD endpoints. The MCP layer (later) should compose these into semantic operations like `query_knowledge_graph`, `get_project_context`, `find_related_patterns`.

### Claim 2: Too many tools degrade LLM performance

**Confidence: Very High** (5 sources: S5, S7, S10, S11, S12)

Hard data backs this claim:
- Cursor caps at 40 MCP tools
- GitHub Copilot caps at 128
- Every tool definition consumes context window tokens
- Performance (accuracy + latency) degrades with more tools

**Mitigation patterns**:
1. **Toolsets** (GitHub pattern, S7): Group tools by domain, enable/disable groups via config
2. **Progressive disclosure** (Klavis pattern, S5): discover_categories -> get_actions -> get_details -> execute
3. **Persona-based filtering** (S10): Different tool subsets for different agent roles

**Implication for rai-server**: Plan for ~10-20 MCP tools maximum, grouped into toolsets. The REST API can have 50+ endpoints without issue.

### Claim 3: Resources for read-only context, Tools for actions

**Confidence: Very High** (3 sources: S1, S6, S12)

The MCP spec explicitly distinguishes:
- **Resources**: Application-controlled, contextual data (files, schemas, configs). The host decides when to include them.
- **Tools**: Model-controlled, executable functions. The LLM decides when to invoke them (with human approval).

| Use Case | Primitive | Example |
|----------|-----------|---------|
| Project metadata | Resource | `rai://project/{key}/metadata` |
| Node type definitions | Resource | `rai://schema/node-types` |
| Search the knowledge graph | Tool | `search_knowledge_graph(query)` |
| Add a pattern | Tool | `add_pattern(content, context)` |
| Get session context | Resource | `rai://session/{id}/context` |

**Implication for rai-server**: Read-only data that provides background context (schemas, project info) should be MCP Resources. Operations the agent invokes should be MCP Tools.

### Claim 4: Snake_case naming with domain prefix is the standard

**Confidence: High** (4 sources: S6, S7, S8, S9)

Concrete evidence:
- 90%+ of production MCP servers use snake_case (S9)
- GitHub uses: `list_repos`, `create_issue`, `search_code` (S7)
- Atlassian uses: `jira_get_issue`, `confluence_search`, `jira_create_issue` (S8)
- Pattern: `{domain}_{verb}_{noun}` or `{verb}_{noun}` within a single-domain server

**Spec constraints** (S6):
- Names: 1-64 characters
- Allowed chars: alphanumeric, `_`, `-`, `.`, `/`
- Case-sensitive

**Implication for rai-server**: Use `search_graph`, `get_node`, `add_pattern`, `get_session_context`. If multi-domain, prefix with `rai_`.

### Claim 5: Design the service layer to serve both REST and MCP

**Confidence: High** (3 sources: S2, S3, S4)

The recommended architecture:

```
┌─────────────────┐     ┌─────────────────┐
│  FastAPI Routes  │     │   MCP Server    │
│  (REST, CRUD)    │     │  (Semantic ops)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│           Service / Domain Layer         │
│  (Business logic, orchestration, auth)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│           Repository / Data Layer        │
│     (SQLAlchemy models, queries)         │
└─────────────────────────────────────────┘
```

Both the REST API and MCP server call the same service layer. The REST layer exposes fine-grained CRUD. The MCP layer composes services into higher-level operations.

**Implication for rai-server**: Build a clean service layer in S275.3 (FastAPI bootstrap). This service layer becomes the shared substrate for both REST routes and future MCP tools.

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Better Alternative |
|-------------|-------------|-------------------|
| 1:1 REST-to-MCP mapping | Overwhelms LLMs, wastes context window | Compose multiple REST calls into semantic tools |
| Auto-generating from OpenAPI | Produces too many low-level tools | Curate tools manually around outcomes |
| No output schemas | LLM can't predict response shape | Define outputSchema for structured responses |
| Throwing exceptions on error | Agent can't self-correct | Return descriptive error strings |
| Exposing all tools always | Context window waste | Use toolsets/progressive disclosure |
| Generic tool names | Model confusion across servers | Use domain-prefixed snake_case names |

---

## Concrete Recommendations for rai-server (E275)

### S275.3 (FastAPI Bootstrap) — Do Now
1. **Service layer pattern**: Create a `services/` module separate from `routes/`. Routes call services, services call repositories.
2. **Clean domain boundaries**: Separate graph, pattern, session, and project concerns at the service level.
3. **REST API design**: Standard CRUD endpoints, RESTful naming. This is for human developers and programmatic clients.
4. **Response models**: Use Pydantic models for all responses. These will later inform MCP outputSchemas.

### Future MCP Server — Design Decisions to Bank
1. **~15 semantic tools** grouped into 3-4 toolsets (graph, patterns, sessions, project)
2. **MCP Resources** for: project metadata, node type schemas, session context
3. **MCP Tools** for: graph search, pattern operations, session management
4. **Naming**: `search_graph`, `get_node_context`, `add_pattern`, `get_session_bundle`
5. **Progressive disclosure**: Start with a `discover_capabilities` tool if tool count grows
6. **Error handling**: Return structured error strings, never throw

### What NOT to Do
- Don't add MCP dependencies to rai-server yet
- Don't shape REST endpoints to match MCP tool signatures
- Don't try to auto-generate MCP tools from OpenAPI spec
- Don't design REST paths around "what an LLM would call"

---

## Key Insight

The REST API and MCP server are two different UIs for the same backend — one for developers, one for agents. Design the shared service layer well, and the MCP layer becomes a straightforward composition layer on top of it. The risk is NOT in the REST design — it's in coupling the REST design to MCP concerns prematurely.

---

## Sources

See `sources/evidence-catalog.md` for full evidence catalog with URLs, evidence levels, and key findings.

Key sources by weight:
1. [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25) — Official spec (Very High)
2. [Philipp Schmid: MCP Best Practices](https://www.philschmid.de/mcp-best-practices) — "Good REST API != Good MCP Server" (Very High)
3. [GitHub MCP Server](https://github.com/github/github-mcp-server) — Reference implementation with toolsets (Very High)
4. [Klavis: Less is More](https://www.klavis.ai/blog/less-is-more-mcp-design-patterns-for-ai-agents) — Progressive disclosure pattern (High)
5. [Scalekit: Map API to MCP](https://www.scalekit.com/blog/map-api-into-mcp-tool-definitions) — Domain-based grouping (High)
6. [Atlassian MCP](https://github.com/sooperset/mcp-atlassian) — Production 51-tool server with namespacing (High)
