# Evidence Catalog: MCP Server Tool Design Patterns

> Research date: 2026-02-25
> Depth: Quick scan (12 sources)
> Question: How should a REST API relate to an MCP server that wraps it?

---

## Sources

### S1 — Stainless: "From REST API to MCP Server"
- **URL**: https://www.stainless.com/mcp/from-rest-api-to-mcp-server
- **Type**: Industry guide (MCP tooling vendor)
- **Evidence Level**: High
- **Key Finding**: REST endpoints that retrieve data (GET) map to MCP resources; endpoints that modify state (POST/PUT/DELETE) map to MCP tools. 1:1 mapping is a starting point but not the destination.

### S2 — Scalekit: "How to Map REST APIs to MCP Tool Definitions"
- **URL**: https://www.scalekit.com/blog/map-api-into-mcp-tool-definitions
- **Type**: Technical guide
- **Evidence Level**: High
- **Key Finding**: Categorize API into logical domains first. Use consistent naming across tools. Group multiple REST calls into single high-level actions (e.g., `manage_user_profile` instead of separate get/update tools).

### S3 — Scalekit: "Should You Wrap MCP Around Your Existing API?"
- **URL**: https://www.scalekit.com/blog/wrap-mcp-around-existing-api
- **Type**: Architecture analysis
- **Evidence Level**: High
- **Key Finding**: MCP servers should be outcome-oriented, not endpoint-oriented. An MCP tool should represent a workflow, not a CRUD operation. Multiple REST calls can be orchestrated behind a single MCP tool.

### S4 — Philipp Schmid: "MCP is Not the Problem, It's Your Server"
- **URL**: https://www.philschmid.de/mcp-best-practices
- **Type**: Expert blog (HuggingFace, published 2026-01-21)
- **Evidence Level**: Very High
- **Key Finding**: "A good REST API is not a good MCP server." Design tools around outcomes, not endpoints. MCP is a UI for agents — curate the experience. Example: `track_order(email)` instead of three separate REST calls.

### S5 — Klavis AI: "Less is More: 4 Design Patterns for Building Better MCP Servers"
- **URL**: https://www.klavis.ai/blog/less-is-more-mcp-design-patterns-for-ai-agents
- **Type**: Architecture patterns (vendor blog)
- **Evidence Level**: High
- **Key Finding**: Progressive disclosure pattern — discover categories first, then actions, then schemas, then execute. Minimizes context window usage while maximizing capability. Directly addresses the "too many tools" problem.

### S6 — MCP Specification (2025-11-25)
- **URL**: https://modelcontextprotocol.io/specification/2025-11-25
- **Type**: Official specification
- **Evidence Level**: Very High
- **Key Finding**: Tools are model-controlled executable functions. Resources are application-controlled contextual data. Tool names 1-64 chars, case-sensitive, alphanumeric + `_-./`. OutputSchema is optional but enables type-safe structured responses. Annotations provide metadata about tool behavior.

### S7 — GitHub MCP Server (Official)
- **URL**: https://github.com/github/github-mcp-server
- **Type**: Reference implementation (first-party)
- **Evidence Level**: Very High
- **Key Finding**: Uses toolsets (repos, issues, pull_requests, actions, code_security) to enable/disable groups. Preserves old names as aliases when renaming. Snake_case naming. `--toolsets` flag for selective exposure.

### S8 — Atlassian MCP Servers (Community + Official)
- **URL**: https://github.com/sooperset/mcp-atlassian
- **Type**: Production implementation
- **Evidence Level**: High
- **Key Finding**: 51+ tools covering Jira + Confluence. Uses `jira_` and `confluence_` prefixes for namespacing. Domain-specific tool names like `jira_search`, `jira_get_issue`, `confluence_get_page`. Some implementations consolidate to 5 generic HTTP tools instead.

### S9 — MCP Tool Naming Conventions (ZazenCodes)
- **URL**: https://zazencodes.com/blog/mcp-server-naming-conventions
- **Type**: Community analysis
- **Evidence Level**: Medium
- **Key Finding**: 90%+ of MCP tools use snake_case. Common pattern: `{service}_{action}_{resource}` or `{domain}/{action}`. Namespaced names prevent tool hijacking in multi-server environments.

### S10 — "The MCP Tool Trap" (Jentic)
- **URL**: https://jentic.com/blog/the-mcp-tool-trap
- **Type**: Industry analysis
- **Evidence Level**: Medium-High
- **Key Finding**: Enterprise APIs expose hundreds of operations; dumping them all into MCP overwhelms LLMs. Cursor caps at 40 tools, GitHub Copilot at 128. Focus on persona-specific tool subsets.

### S11 — JetBrains: "Building LLM-Friendly MCP Tools"
- **URL**: https://blog.jetbrains.com/ruby/2026/02/rubymine-mcp-and-the-rails-toolset/
- **Type**: IDE vendor engineering blog (2026-02)
- **Evidence Level**: High
- **Key Finding**: Design for pagination, filtering, and error handling as first-class concerns. Return helpful strings on error (not exceptions) so agents can self-correct. Context window is the scarce resource.

### S12 — MCP Best Practices (modelcontextprotocol.info)
- **URL**: https://modelcontextprotocol.info/docs/best-practices/
- **Type**: Community documentation
- **Evidence Level**: High
- **Key Finding**: Each MCP server should have one clear, well-defined purpose. Security considerations include tool behavior descriptions being untrusted unless from trusted servers. Host must obtain explicit user consent before invoking tools.

---

## Evidence Level Key

| Level | Criteria |
|-------|----------|
| Very High | Official spec, first-party reference implementations, or domain experts with direct experience |
| High | Production implementations, vendor engineering blogs with concrete patterns |
| Medium-High | Industry analysis with data backing claims |
| Medium | Community analysis, pattern surveys |
| Low | Anecdotal, single-source claims |
