# GitLab Duo Tool/Action Design: Research Report

**Date**: 2026-02-25
**Depth**: Quick Scan (12 sources)
**Confidence**: High

---

## 1. Executive Summary

GitLab Duo Agent Platform (GA since January 2026) provides native MCP support as both client and server. For RaiSE, the recommended integration path is to **build an MCP server** that GitLab Duo Chat (Agentic) can consume directly. This aligns with GitLab's architecture and is the same pattern used for Jira, Slack, and AWS integrations.

Three integration paths exist, in order of recommendation:
1. **MCP Server** (primary) -- RaiSE exposes tools via MCP; GitLab Duo connects as MCP client
2. **External Agent** (secondary) -- RaiSE runs as an autonomous agent triggered from GitLab
3. **Custom Agent + MCP** (tertiary) -- GitLab user creates a custom agent that connects to RaiSE's MCP server

---

## 2. GitLab Duo Architecture Overview

### 2.1 Core Components

GitLab Duo's AI architecture has three main layers [S10, S5, S9]:

```
User (IDE / Web UI)
    |
GitLab Rails Monolith
    |
AI Gateway (GCP Cloud Run)
    |
Model Providers (Anthropic, Google, etc.)
```

- **AI Gateway**: Standalone service deployed on GCP; provides unified model access for all GitLab instances (SaaS, self-managed, dedicated). Cloudflare + GCP load balancers route to nearest deployment.
- **API namespace**: `/api/v4/ai_assisted` for AI workloads, isolated from regular API for independent scaling.
- **Execution model**: Async via Sidekiq by default (non-latency-sensitive); direct calls for latency-sensitive actions.

### 2.2 Agent Platform Structure

The Duo Agent Platform supports three agent types [S5, S6, S9]:

| Type | Description | Use Case |
|------|-------------|----------|
| **Foundational** | Pre-built by GitLab (Duo Chat, Code Suggestions, etc.) | Default AI features |
| **Custom** | Created by org via AI Catalog; system prompt + tool selection | Org-specific assistants |
| **External** | Integrated with third-party AI providers via YAML config | Bringing external AI into GitLab |

**Flows** are multi-agent workflows composed of agents and deterministic steps [S9]:
- Developer flow (Issue to MR)
- Convert to GitLab CI/CD flow
- Fix CI/CD pipeline flow
- Code Review flow

Flows are configured via `.gitlab/duo/agent-config.yml` and support custom Docker images and setup scripts.

### 2.3 GitLab's Own Knowledge Graph

GitLab has a built-in Knowledge Graph [S11, S12] that:
- Parses local repositories into structured, queryable representations
- Captures entities: files, directories, classes, functions, and relationships
- Powers AI agents for increased accuracy
- Connects via MCP to query projects

**Implication for RaiSE**: Our knowledge graph is complementary -- it covers cross-platform context (Jira + GitLab + code), process patterns, and organizational memory. GitLab's KG is repo-scoped. We should position as "cross-platform process intelligence" not "code knowledge graph."

---

## 3. MCP Support in GitLab Duo

### 3.1 Dual MCP Capability

GitLab Duo supports MCP in both directions [S1, S2, S3, S8]:

| Direction | GitLab Role | Description |
|-----------|-------------|-------------|
| **Inbound** | MCP Client | Duo Chat connects to external MCP servers (e.g., Jira, RaiSE) |
| **Outbound** | MCP Server | External AI tools (Claude, Cursor) connect to GitLab |

### 3.2 GitLab as MCP Client (Our Primary Integration Path)

**This is how RaiSE would be consumed.** GitLab Duo Chat (Agentic) connects to external MCP servers [S2, S8, S12].

**Configuration format** (`mcp.json`):

```json
{
  "mcpServers": {
    "raise-knowledge-graph": {
      "type": "http",
      "url": "https://api.raiseframework.ai/mcp",
      "approvedTools": ["query_graph", "get_context", "search_patterns"]
    }
  }
}
```

**Config file locations**:
- Linux/macOS: `~/.gitlab/duo/mcp.json` (user-level)
- Windows: `C:\Users\<username>\AppData\Roaming\GitLab\duo\mcp.json`
- Workspace: `<workspace>/.gitlab/duo/mcp.json`
- The Language Server loads and merges user + workspace configs.

**Supported transports** [S2]:
- `stdio` -- local command-based servers
- `http` -- HTTP-based connections (Streamable HTTP)
- `sse` -- Server-Sent Events connections

**Tool approval** [S2, S12]:
- `"approvedTools": true` -- auto-approve all tools (current and future)
- `"approvedTools": ["tool1", "tool2"]` -- approve specific tools only

**Prerequisites**:
- VS Code/VSCodium with GitLab extension v6.28.2+
- Group setting: "Allow external MCP tools" must be enabled
- GitLab 18.6+ for MCP server features

### 3.3 GitLab MCP Server Tools (Reference Pattern)

GitLab's own MCP server exposes these tools [S4]. This is the design pattern to follow:

| Tool | Description | Added |
|------|-------------|-------|
| `version` | Returns MCP server version | Base |
| `create_issue` | Creates issue in GitLab project | Base |
| `get_issue` | Retrieves issue details | Base |
| `create_merge_request` | Creates MR in project | Base |
| `get_merge_request` | Retrieves MR details | Base |
| `semantic_code_search` | AI-powered code search | 18.7 |
| `get_merge_request_commits` | MR commit list | Later |
| `get_merge_request_diffs` | MR diffs | Later |
| `get_merge_request_pipelines` | MR pipeline status | Later |

**Pattern observations**:
- Tools are CRUD-oriented (get/create) with clear noun-verb naming
- Each tool maps to a single GitLab API operation
- Tools are additive across versions (never removed)
- Authentication via OAuth 2.0 Dynamic Client Registration
- Tools accept simple parameter sets (project ID, issue ID, etc.)

---

## 4. External Agent Integration Path

If RaiSE needs to run as an autonomous agent (not just expose tools), the External Agent path is relevant [S6].

**How it works**:
1. Create external agent in AI Catalog (UI or API)
2. Configure via YAML (model provider, tools, system prompt)
3. Create service account with project access
4. Create trigger (mention in issue, epic, or MR comment)
5. Agent runs with composite identity (user + service account permissions)

**Key constraints**:
- `injectGatewayToken: true` enables GitLab AI Gateway proxy
- Environment variables injected: `AI_FLOW_AI_GATEWAY_TOKEN`, `AI_FLOW_AI_GATEWAY_HEADERS`
- Agent runs in a container (custom Docker image supported)
- Triggered by @mention in GitLab UI

**When to use**: If RaiSE needs to proactively act on GitLab events (e.g., auto-analyze new issues, suggest patterns on MR review). For passive tool consumption, MCP is simpler.

---

## 5. Integration Recommendations for RaiSE

### 5.1 Primary: Build an MCP Server

**Why**: This is GitLab's standard pattern for external tool integration. It works with Duo Chat (Agentic), requires no GitLab-side agent deployment, and is the same protocol we'd use for Claude Desktop, Cursor, and other MCP clients.

**Recommended RaiSE MCP tools**:

| Tool | Description | Maps to |
|------|-------------|---------|
| `query_graph` | Query knowledge graph with natural language | Core graph search |
| `get_node_context` | Get full context for a graph node | Node detail |
| `search_patterns` | Search organizational patterns | Pattern library |
| `get_project_overview` | Get project structure and key concepts | Project summary |
| `list_related_concepts` | Find concepts related to a given entity | Graph traversal |

**Design principles** (derived from GitLab's own patterns):
1. **CRUD-oriented naming**: `get_*`, `create_*`, `search_*`, `list_*`
2. **Single-operation tools**: Each tool does one thing well
3. **Simple parameters**: Avoid nested objects; use IDs and simple strings
4. **Versioned additions**: Add tools over time, never remove
5. **Clear descriptions**: Each tool needs a description good enough for an LLM to select it

### 5.2 Transport Choice

**Recommendation: HTTP (Streamable HTTP)**

| Transport | Pros | Cons | Verdict |
|-----------|------|------|---------|
| stdio | Simple for local dev | Requires local install | Dev only |
| HTTP | Cloud-native, stateless, works with SaaS | Needs hosting | Production |
| SSE | Streaming support | More complex, older MCP pattern | Avoid |

HTTP aligns with our FastAPI server (S275.3) and works for both GitLab Duo and other MCP clients.

### 5.3 Authentication

GitLab Duo's MCP client will connect to our server. We need to support:
- **API key auth** (simplest, for initial integration)
- **OAuth 2.0** (future, for enterprise deployments)

GitLab's own MCP server uses OAuth 2.0 Dynamic Client Registration. We should plan for this but start with API keys.

### 5.4 Configuration Example

How a GitLab user would connect to RaiSE:

```json
{
  "mcpServers": {
    "raise": {
      "type": "http",
      "url": "https://api.raiseframework.ai/mcp",
      "headers": {
        "Authorization": "Bearer <raise-api-key>"
      },
      "approvedTools": true
    }
  }
}
```

### 5.5 Positioning vs GitLab Knowledge Graph

| Aspect | GitLab Knowledge Graph | RaiSE Knowledge Graph |
|--------|----------------------|----------------------|
| Scope | Single repo | Cross-platform (GitLab + Jira + code) |
| Focus | Code structure (files, classes, functions) | Process intelligence (patterns, decisions, context) |
| Persistence | Session/request-scoped | Persistent, evolving |
| Learning | Static analysis | Temporal patterns, decay, scoring |

**Messaging**: "RaiSE extends GitLab Duo with cross-platform organizational memory -- connecting your GitLab repos with Jira context, team patterns, and architectural decisions."

---

## 6. Comparison with Atlassian Rovo

| Dimension | GitLab Duo | Atlassian Rovo |
|-----------|-----------|----------------|
| Protocol | MCP (native) | Forge platform + REST APIs |
| Tool model | MCP tools (standard) | Rovo Agents with actions |
| Auth | OAuth 2.0 / API key | Atlassian Connect / Forge auth |
| Extension | MCP server + External Agent | Forge app + Rovo agent config |
| Maturity | GA (Jan 2026) | GA (late 2025) |

**Implication**: RaiSE's MCP server works directly for GitLab Duo. For Atlassian Rovo, we need a Forge wrapper around the same API. The core API (FastAPI + MCP) serves both, with platform-specific thin adapters.

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| MCP spec evolves breaking changes | Low | Medium | Pin to stable MCP version; abstract transport layer |
| GitLab changes MCP client config format | Low | Low | Config is user-side, not our concern |
| GitLab Knowledge Graph overlaps with RaiSE | Medium | Medium | Position as complementary; focus on cross-platform + process |
| Auth complexity for enterprise | Medium | Medium | Start API key, plan OAuth 2.0 roadmap |

---

## 8. Action Items for RaiSE

1. **S275.3 (FastAPI server)**: Include MCP endpoint support from the start. Use `mcp` Python library with Streamable HTTP transport.
2. **Tool design**: Define 4-6 initial MCP tools following GitLab's CRUD pattern (query, get, search, list).
3. **Auth**: Start with API key auth in headers; plan OAuth 2.0 for enterprise.
4. **Positioning doc**: Write 1-paragraph positioning vs GitLab Knowledge Graph for sales/partner conversations.
5. **Test with GitLab Duo**: Once MCP server is live, test with VS Code + GitLab extension to validate end-to-end flow.

---

## Sources

Full evidence catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)

Key sources:
- [S1] [GitLab Duo MCP Overview](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/)
- [S2] [GitLab MCP Clients](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_clients/)
- [S3] [GitLab MCP Server](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/)
- [S4] [GitLab MCP Server Tools](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server_tools/)
- [S5] [Duo Agent Platform](https://docs.gitlab.com/user/duo_agent_platform/)
- [S6] [External Agents](https://docs.gitlab.com/user/duo_agent_platform/agents/external/)
- [S8] [MCP Integration Blog](https://about.gitlab.com/blog/duo-agent-platform-with-mcp/)
- [S9] [Agent Platform GA Blog](https://about.gitlab.com/blog/gitlab-duo-agent-platform-is-generally-available/)
- [S10] [AI Architecture](https://docs.gitlab.com/development/ai_architecture/)
- [S11] [GitLab Knowledge Graph](https://docs.gitlab.com/user/project/repository/knowledge_graph/)
