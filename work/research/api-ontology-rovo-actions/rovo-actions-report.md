# Rovo Agent Action Design: Research Report

**Date**: 2026-02-25
**Sources**: 11 (6 Very High, 3 High, 2 Medium)
**Confidence**: High — triangulated from official docs, case studies, and practitioner reports

---

## 1. Core Architecture

Rovo agents are LLM-powered conversational interfaces embedded in Jira and Confluence. They execute tasks through **actions** (recently rebranded as **skills**) — discrete units of work defined in a Forge app's manifest.

The architecture has three layers:

```
User (chat) --> Rovo Agent (LLM + prompt) --> Action (manifest) --> Forge Function (code)
                                                                        |
                                                                   External API
```

**Key insight**: The action manifest is the AI-facing contract. The LLM reads the action's `name`, `description`, and `inputs` schema to decide when and how to invoke it. The Forge function is just the execution backend.

*Sources: S1, S2, S4, S5 (triangulated across 4 official docs)*

---

## 2. Action Manifest Schema

Every action requires these fields:

| Field | Type | Purpose |
|-------|------|---------|
| `key` | string | Unique ID (`^[a-zA-Z0-9_-]+$`) |
| `name` | string | Human-readable display name |
| `actionVerb` | enum | `GET`, `CREATE`, `UPDATE`, `DELETE`, `TRIGGER` |
| `description` | string | **LLM reads this to decide invocation** |
| `inputs` | object | Named parameters with type, title, required, description |
| `function` or `endpoint` | string | Backend handler reference |

### Input Types

Only four primitive types: `string`, `integer`, `number`, `boolean`. No arrays, no objects, no enums.

**Implication for RaiSE**: Our FastAPI endpoints must accept only flat, primitive parameters. Complex queries (e.g., multi-filter searches) need to be encoded as strings (JSON strings or comma-separated values) or split into multiple focused actions.

*Sources: S1 (canonical), S4, S7 (all Very High)*

---

## 3. Triangulated Claims

### Claim 1: Description quality determines invocation accuracy

The action `description` is the primary signal the LLM uses to decide whether to invoke an action. Poor descriptions lead to wrong or missed invocations.

- S1: "Agent uses [description] to determine when to invoke the action"
- S4: "When a user asks to log a message, this action logs the message" — description written as a conditional trigger
- S6: Opus Guard embeds response parsing instructions in prompts to compensate for description limitations
- S3: "Prompt quality is the #1 success factor"

**Pattern**: Write descriptions as conditional triggers: "When the user wants to [goal], this action [does what] by [how]."

### Claim 2: Data minimization is essential

Return only the fields the agent needs, not raw API responses. Excess data wastes tokens, confuses the LLM, and hits the 5 MB limit.

- S7: Jira analyst returns only `key` + `summary`, not full issue objects
- S1: 5 MB data limit per action invocation
- S5: "Cryptic field names hurt LLM comprehension — surface clear descriptions"
- S3: Universal fetch approach works but needs careful response shaping

**Pattern**: Design API responses with an LLM consumer in mind — flat, descriptive field names, only essential data, human-readable values.

### Claim 3: Fewer, focused actions outperform many broad ones

- S8: "Fewer than 5 skills per agent" recommended
- S6: Opus Guard uses exactly 4 actions (CRUD pattern)
- S7: Single `get-issues` action with optional filter parameter
- S3: Universal fetch approach is powerful but harder to prompt correctly

**Pattern**: Design actions around user intents, not API resources. One action per distinct user goal.

### Claim 4: Prompt engineering is the primary integration mechanism

The prompt tells the agent *when* and *how* to use actions. Without explicit prompt instructions, the agent may not invoke actions correctly — especially in Forge (vs. Studio).

- S2: Prompt structure = role + capabilities + action execution steps + output format
- S6: Three-layer prompt: Workflow > Jobs > Templates
- S3: "Prompt quality is the #1 success factor"
- S4: "The main way to change the behavior of your Agent is by modifying the prompt"
- S6: "Prompts effective in Studio often fail for Forge agents"

**Pattern**: The prompt is the orchestration layer. Actions are just tools — the prompt is the toolbelt.

### Claim 5: Actions are stateless — no memory between invocations

- S3: "No contextual memory between interactions — API response data doesn't persist across queries"
- S1: Each action invocation is independent
- S4: Context object provides current page/issue, nothing historical

**Implication for RaiSE**: Every action call must be self-contained. If an agent needs to correlate data across calls, the prompt must instruct multi-step workflows, and each step must return enough context for the next.

---

## 4. actionVerb Semantics

| Verb | Semantics | Automation | Use For |
|------|-----------|------------|---------|
| `GET` | Read-only retrieval | Works | Queries, searches, lookups |
| `CREATE` | Resource creation | Blocked | Creating entities |
| `UPDATE` | Resource modification | Blocked | Modifying entities |
| `DELETE` | Resource removal | Blocked | Removing entities |
| `TRIGGER` | Side-effect execution | Blocked | Notifications, logs, workflows |

**Critical constraint**: `CREATE`, `UPDATE`, `DELETE`, and `TRIGGER` actions are blocked in automation rules. Only `GET` works in automated contexts.

**Implication for RaiSE**: If we want automation-compatible actions, read endpoints must use `GET`. Write operations will always require interactive confirmation.

*Sources: S1 (canonical), S8*

---

## 5. External API Integration Patterns

### Pattern A: Direct Forge Function (Recommended for RaiSE)

```
Rovo Agent --> Action --> Forge Function --> fetch() --> FastAPI Server
```

The Forge function calls our FastAPI server using `@forge/api` fetch. The function shapes the request and response.

### Pattern B: Forge Remote

```
Rovo Agent --> Action --> Forge Remote Endpoint --> External Server
```

Uses `endpoint` instead of `function` in manifest. The remote server is registered in the manifest with auth configuration.

### Pattern C: Universal Fetch (Advanced)

Single action that accepts arbitrary endpoint + params. More flexible but harder to prompt correctly.

- S3 recommends this for rapid iteration
- S6 and S7 use focused actions (Pattern A) for production

### Pattern D: MCP Integration (Emerging)

- S10: Rovo now supports MCP servers for tool connection
- No custom code required for simple integrations
- Admins manage via gallery
- Less control than Forge, but faster setup

**Recommendation for RaiSE**: Start with Pattern A (focused Forge functions calling FastAPI). Consider MCP as a parallel distribution channel later.

*Sources: S1, S3, S5, S10 (triangulated)*

---

## 6. Security Constraints

1. **Never trust input values for authorization** — read `accountId` from `context`, not from user input (S1)
2. **Use `asUser()` for permission validation** — ensures the calling user has permission (S6)
3. **actionVerb must accurately reflect the operation** — security auditing relies on this (S1)
4. **User confirmation required for mutations** — agents always ask before executing CREATE/UPDATE/DELETE (S8)
5. **Data stays in Atlassian Cloud** — content data is not accessible to app vendors by default (S6)

---

## 7. Teamwork Graph

The Teamwork Graph is Atlassian's proprietary knowledge graph that tracks people, teams, projects, goals, and work artifacts across the Atlassian ecosystem. Key facts:

- **Not directly extensible** via public API — no custom node/edge types
- **Powers intent routing** — Rovo Chat uses it to understand context
- **100B+ work items and relationships** indexed
- **Backs personalization** — responses grounded in actual work data

**Implication for RaiSE**: We cannot inject into the Teamwork Graph. Our knowledge graph is a parallel data source, accessed through Forge actions. The Teamwork Graph provides ambient context (who is asking, what project, what page); our graph provides domain-specific knowledge.

*Sources: S10, S11*

---

## 8. Recommendations for RaiSE API Design

### 8.1 Endpoint Design Principles

1. **Flat parameters only** — no nested objects in action inputs. Use string-encoded filters if needed.
2. **Verb-aligned routes** — map FastAPI routes to actionVerb semantics (GET for queries, POST for creates, etc.)
3. **Minimal response payloads** — return only fields the LLM needs. Include human-readable labels, not just IDs.
4. **Self-contained responses** — each response must include enough context for the agent to act on without prior state.
5. **Descriptive field names** — `project_name` not `prj_nm`. The LLM reads these.

### 8.2 Action Design Patterns

```yaml
# Pattern: Knowledge graph query
- key: search-knowledge
  actionVerb: GET
  description: >
    When the user wants to find information about a topic, concept, or pattern
    in the team's knowledge base, this action searches the knowledge graph
    and returns matching nodes with their descriptions and relationships.
  inputs:
    query:
      title: Search Query
      type: string
      required: true
      description: "The topic, concept, or keyword to search for"
    limit:
      title: Result Limit
      type: integer
      required: false
      description: "Maximum number of results to return (default 10)"

# Pattern: Context retrieval
- key: get-module-context
  actionVerb: GET
  description: >
    When the user wants to understand a specific module, component, or code area,
    this action retrieves its description, dependencies, and related patterns
    from the knowledge graph.
  inputs:
    moduleId:
      title: Module Identifier
      type: string
      required: true
      description: "The module ID (e.g., 'mod-memory', 'mod-discovery')"

# Pattern: Pattern lookup
- key: get-patterns
  actionVerb: GET
  description: >
    When the user wants to see team patterns, lessons learned, or best practices,
    this action retrieves relevant patterns from the knowledge graph filtered
    by context keywords.
  inputs:
    context:
      title: Context Keywords
      type: string
      required: false
      description: "Comma-separated keywords to filter patterns (e.g., 'testing,tdd')"
```

### 8.3 FastAPI Endpoint Mapping

| Action | actionVerb | FastAPI Route | Method |
|--------|-----------|---------------|--------|
| search-knowledge | GET | `/api/v1/knowledge/search` | GET |
| get-module-context | GET | `/api/v1/modules/{module_id}` | GET |
| get-patterns | GET | `/api/v1/patterns` | GET |
| create-pattern | CREATE | `/api/v1/patterns` | POST |
| update-pattern | UPDATE | `/api/v1/patterns/{pattern_id}` | PUT |

### 8.4 Response Format Guidelines

```json
{
  "results": [
    {
      "id": "pat-e-444",
      "title": "Coverage gates create Goodhart dynamics",
      "type": "pattern",
      "context": ["testing", "ci", "coverage"],
      "summary": "Fixed coverage gates (e.g., --cov-fail-under=90) incentivize test muda...",
      "confidence": 0.85,
      "last_reinforced": "2026-02-20"
    }
  ],
  "total": 1,
  "query": "coverage testing"
}
```

Key response design choices:
- Flat structure (no nesting beyond one level)
- Human-readable field names
- Summary field for LLM consumption (not raw data)
- Metadata for agent decision-making (confidence, dates)

### 8.5 Prompt Template for RaiSE Agent

```
You are a knowledge assistant for the {team_name} engineering team.
You help developers find patterns, understand code architecture, and
access institutional knowledge stored in the team's knowledge graph.

---

## Available Actions

### Finding Information
- Use **search-knowledge** when the user asks about a topic, concept, or wants to find relevant information.
- Use **get-module-context** when the user asks about a specific module, component, or code area.
- Use **get-patterns** when the user wants team patterns, lessons learned, or best practices.

### Presenting Results
- Always present results in a clear, structured format
- Include pattern IDs for reference
- Highlight high-confidence patterns (> 0.8) as established practices
- Note low-confidence patterns as emerging observations
```

---

## 9. Open Questions

1. **MCP vs Forge**: Should we also expose our API as an MCP server for simpler setups? MCP is emerging but less mature.
2. **Pagination**: How to handle paginated results given the 5 MB limit and stateless nature? Pre-aggregate on the server.
3. **Multi-tenant isolation**: Forge context provides cloudId — our API must scope all queries by tenant.
4. **Caching**: Given stateless interactions and latency concerns, should the Forge function cache frequently-accessed data?

---

## 10. Summary

| Principle | Rationale |
|-----------|-----------|
| Write descriptions for LLMs, not humans | Description is the AI routing signal |
| Flat, primitive inputs only | Schema constraint: string, integer, number, boolean |
| Return minimal, descriptive data | 5 MB limit + LLM token economy |
| Fewer than 5 actions per agent | Official recommendation for focused agents |
| Self-contained responses | No memory between invocations |
| Verb-align with actionVerb | Affects automation compatibility and security auditing |
| Iterate prompts in Studio first | Faster feedback loop before Forge deployment |
| Validate permissions server-side | Never trust action inputs for auth |
