# Evidence Catalog: GitLab Duo Tool/Action Design

## Source Index

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S1 | [GitLab Duo Docs - MCP Overview](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/) | Official Docs | Very High | MCP provides standardized way for Duo features to connect to external data sources and tools |
| S2 | [GitLab MCP Clients Docs](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_clients/) | Official Docs | Very High | Duo Chat (Agentic) connects to external MCP servers; config via mcp.json; stdio/http/sse transports |
| S3 | [GitLab MCP Server Docs](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/) | Official Docs | Very High | GitLab exposes MCP server for Claude Desktop, Cursor, etc.; OAuth 2.0 auth |
| S4 | [GitLab MCP Server Tools](https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server_tools/) | Official Docs | Very High | Available tools: version, create_issue, get_issue, create_mr, get_mr, semantic_code_search, get_mr_commits, get_mr_diffs, get_mr_pipelines |
| S5 | [GitLab Duo Agent Platform Docs](https://docs.gitlab.com/user/duo_agent_platform/) | Official Docs | Very High | Three agent types: foundational, custom, external; AI Catalog for publishing |
| S6 | [External Agents Docs](https://docs.gitlab.com/user/duo_agent_platform/agents/external/) | Official Docs | Very High | External agents integrate third-party AI providers; YAML config; service accounts; composite identity |
| S7 | [Agent Tools Docs](https://docs.gitlab.com/user/duo_agent_platform/agents/tools/) | Official Docs | Very High | Built-in tools selectable via dropdown; includes create_issue and others |
| S8 | [MCP Integration Blog Post](https://about.gitlab.com/blog/duo-agent-platform-with-mcp/) | Official Blog | High | MCP client + server dual capability; connects to Jira, Slack, AWS; OAuth 2.0 Dynamic Client Registration |
| S9 | [Duo Agent Platform GA Announcement](https://about.gitlab.com/blog/gitlab-duo-agent-platform-is-generally-available/) | Official Blog | High | GA as of Jan 2026; AI Catalog for sharing agents; flows for multi-step workflows |
| S10 | [AI Architecture Docs](https://docs.gitlab.com/development/ai_architecture/) | Official Docs | Very High | AI Gateway in GCP; /api/v4/ai_assisted namespace; Cloudflare routing; abstraction layer |
| S11 | [GitLab Knowledge Graph Docs](https://docs.gitlab.com/user/project/repository/knowledge_graph/) | Official Docs | High | Structured queryable representation of code repos; powers AI agents; parses entities/relationships |
| S12 | [Exploring GitLab's MCP Client (Community)](https://www.viktorious.nl/2025/12/09/exploring-gitlabs-mcp-client-gitlab-knowledge-graph-and-jira-integration/) | Community Blog | Medium | Practical walkthrough of MCP client config with Knowledge Graph and Jira; confirms mcp.json patterns |

## Evidence Level Definitions

| Level | Meaning |
|-------|---------|
| Very High | Official documentation, primary source |
| High | Official blog posts, engineering handbook |
| Medium | Community posts with verifiable claims, third-party analysis |
| Low | Anecdotal, unverified, or outdated |

## Triangulation Matrix

| Claim | Sources | Confidence |
|-------|---------|------------|
| GitLab Duo supports MCP natively (client + server) | S1, S2, S3, S8, S12 | Very High |
| Three transport types: stdio, HTTP, SSE | S2, S8, S12 | Very High |
| Config via mcp.json with mcpServers key | S2, S8, S12 | Very High |
| OAuth 2.0 for MCP server auth | S3, S8, S10 | Very High |
| External agents use YAML config + service accounts | S5, S6, S9 | Very High |
| AI Gateway routes requests via GCP | S10, S9 | High |
| GitLab has its own Knowledge Graph for code repos | S11, S12 | High |
| Tool approval via approvedTools field | S2, S12 | High |
| GitLab 18.6+ required for MCP server | S3, S4 | High |
| VS Code extension 6.28.2+ required for MCP client | S2 | High (single source but official) |
