# Evidence Catalog: Rovo AI & Atlassian Integration

## Research ID: RES-ROVO-001

---

## Sources

### S1: Atlassian Rovo Product Page
- **URL**: https://www.atlassian.com/software/rovo
- **Type**: Primary (Official)
- **Evidence Level**: Very High
- **Key Finding**: Rovo = Find + Learn + Act paradigm; multi-model (Claude, GPT, Gemini, Llama); Teamwork Graph as semantic layer
- **Relevance**: Core architecture understanding

### S2: Rovo Dev Product Page
- **URL**: https://www.atlassian.com/software/rovo-dev
- **Type**: Primary (Official)
- **Evidence Level**: Very High
- **Key Finding**: 4 agents (Code Planner, Generator, Reviewer, Automation); CLI that reads Jira work items; #1 SWE-bench 2025
- **Relevance**: Direct competitor/integration point for RaiSE

### S3: Teamwork Graph Overview
- **URL**: https://developer.atlassian.com/platform/teamwork-graph/what-is-teamwork-graph/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: Unified data model; objects + relationships; 100+ connectors; cross-tool availability
- **Relevance**: Defines the entity model we need to map to

### S4: Teamwork Graph Object Types
- **URL**: https://developer.atlassian.com/platform/teamwork-graph/object-types/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: 15 indexed types (Work Item, Document, Project, etc.); standardized across tools
- **Relevance**: Direct mapping targets for E8 concepts

### S5: Teamwork Graph Relationships
- **URL**: https://developer.atlassian.com/platform/teamwork-graph/relationships/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: 4 relationship types (Canonical, Activity, Logical, Inferred); max 500 associations per object
- **Relevance**: Relationship model alignment

### S6: Atlassian Remote MCP Server
- **URL**: https://www.atlassian.com/blog/announcements/remote-mcp-server
- **Type**: Primary (Official Blog)
- **Evidence Level**: Very High
- **Key Finding**: OAuth 2.1 auth; read/write Jira+Confluence; Anthropic first partner; Cloudflare infrastructure
- **Relevance**: Primary integration mechanism for V3

### S7: Atlassian MCP Server GitHub
- **URL**: https://github.com/atlassian/atlassian-mcp-server
- **Type**: Primary (Official Repository)
- **Evidence Level**: Very High
- **Key Finding**: Endpoint `https://mcp.atlassian.com/v1/mcp`; supports Claude, ChatGPT, Gemini
- **Relevance**: Technical integration details

### S8: Forge/Connect Migration
- **URL**: https://developer.atlassian.com/platform/adopting-forge-from-connect/changelog/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: Connect deprecated Mar 31, 2026; Forge is future; requestGraph for GraphQL
- **Relevance**: Platform direction for custom apps

### S9: Jira REST API v3 - Issue Types
- **URL**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-types/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: Epic, Story, Task, Bug types; Epic Link as custom field; ADF for descriptions
- **Relevance**: Jira entity model details

### S10: Teamwork Graph API Reference
- **URL**: https://developer.atlassian.com/platform/teamwork-graph/api-reference/overview/
- **Type**: Primary (Official Developer Docs)
- **Evidence Level**: Very High
- **Key Finding**: Cypher + GraphQL two-layer query; EAP status
- **Relevance**: Query patterns for graph traversal

### S11: Valiantys AI Architecture Guide
- **URL**: https://www.valiantys.com/en/resources/making-sense-of-atlassians-ai-architecture-a-guide-for-it-leaders-and-builders
- **Type**: Secondary (Partner Analysis)
- **Evidence Level**: High
- **Key Finding**: Third-party analysis of Atlassian AI strategy and integration patterns
- **Relevance**: External validation of architecture understanding

### S12: Eesel AI Rovo Skills Guide
- **URL**: https://www.eesel.ai/blog/rovo-agent-skills
- **Type**: Secondary (Third-party Guide)
- **Evidence Level**: Medium
- **Key Finding**: 100+ out-of-box skills; Rovo Studio for custom agents; MCP skill integration
- **Relevance**: Skill/agent extensibility patterns

---

## Triangulated Claims

### Claim 1: Teamwork Graph is the canonical data layer
- **Confidence**: HIGH
- **Evidence**: S1, S3, S4, S5 (4 official sources)
- **Summary**: All Atlassian AI features (Search, Chat, Agents) access data through Teamwork Graph, not direct product APIs

### Claim 2: MCP is the primary external integration mechanism
- **Confidence**: HIGH
- **Evidence**: S1, S6, S7 (3 official sources)
- **Summary**: Remote MCP Server with OAuth 2.1 is the supported way to connect external AI tools; Anthropic is first partner

### Claim 3: Connect is being deprecated in favor of Forge
- **Confidence**: VERY HIGH
- **Evidence**: S8 (official changelog with dates)
- **Summary**: Connect deprecated Mar 31, 2026; Forge with manifest is the path forward for custom apps

### Claim 4: Rovo Dev competes in the AI coding space
- **Confidence**: HIGH
- **Evidence**: S2 (official product page)
- **Summary**: Rovo Dev CLI, Code Planner, Code Reviewer, etc. are direct features in this space

### Claim 5: Teamwork Graph API is in EAP (Early Access)
- **Confidence**: HIGH
- **Evidence**: S10 (official docs)
- **Summary**: Direct Graph API access requires EAP enrollment; subject to change

---

## Gaps & Unknowns

1. **Teamwork Graph EAP timeline** — When will it GA? Unknown.
2. **Custom object types** — Can third parties define new object types? Unclear from docs.
3. **Bidirectional sync patterns** — Best practices for external→Atlassian sync not documented.
4. **Rovo Dev extensibility** — Can custom skills be added to Rovo Dev agents? Unclear.
5. **Data residency** — How does MCP handle data residency requirements? Not addressed.

---

*Compiled: 2026-02-02*
*Sources: 12 (10 primary, 2 secondary)*
