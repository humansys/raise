# Agentic Tool Design: Best Practices for AI-Consumed APIs

> Research report for rai-server public API design
> Date: 2026-02-25 | Depth: Quick scan (12 sources)
> Decision: CRUD-level endpoints vs domain-level operations for agent consumers

---

## Executive Summary

The evidence strongly converges on a single thesis: **tools designed for AI agents should be domain-oriented operations, not CRUD endpoints**. Every major model provider (Anthropic, OpenAI), industry framework (LangChain, MCP), and practitioner source agrees that agent-consumed APIs must prioritize intent, semantic clarity, and composability over low-level data manipulation.

The key design shift is ontological: tools are not functions — they are **contracts between deterministic systems and non-deterministic agents** (Anthropic S1). This reframes every design decision.

**Recommendation for rai-server:** Expose 8-15 domain-level operations (not 30+ CRUD endpoints) organized around what agents *want to accomplish* with a knowledge graph, not the underlying data model.

---

## Triangulated Claims

Each claim below is supported by 3+ independent sources.

### Claim 1: Domain operations outperform CRUD for agent consumers

**Evidence (5 sources: S1, S3, S4, S5, S8):**

- "Agentic APIs prioritize actionable intent over CRUD operations" (S5)
- "Maintain dual API tiers: machine-oriented (high-level business operations) separate from human-oriented CRUD" (S4)
- "Functions always called in sequence should be combined into one" (S3 — OpenAI)
- "Design tools for agents, not the way you'd write functions/APIs for developers" (S1 — Anthropic)
- ~85% of enterprise prompts require 3+ tools; combining sequential operations reduces total calls (S8)

**Synthesis:** Agents reason about *goals*, not data mutations. A `remember_decision(context, decision, rationale)` operation is cognitively cheaper for an agent than `POST /nodes` + `POST /edges` + `POST /properties`. The model spends fewer tokens understanding, planning, and executing the operation.

**Confidence:** Very High

### Claim 2: Tool descriptions are the primary interface — naming and documentation matter more than schema

**Evidence (5 sources: S1, S3, S7, S10, S12):**

- "Tool definitions become part of context on every LLM call — they consume tokens" (S12)
- "Docstring is critical — it's how agents decide when to use your tool" (S7)
- "Good naming and descriptions with user-intent mapping help performance" (S12)
- "Describe tools as you would to a new hire — make implicit context explicit" (S1)
- "Can someone correctly use the function given only what you provided to the model?" — the intern test (S3)

**Synthesis:** The tool description IS the API documentation for agents. It must answer: What does this do? When should I use it? What do I need to provide? What will I get back? This is fundamentally different from REST API docs — agents cannot browse examples, scroll through pages, or ask follow-up questions about the docs.

**Confidence:** Very High

### Claim 3: Flat parameters with unambiguous names beat nested structures

**Evidence (3 sources: S1, S3, S7):**

- "Make arguments flat rather than deeply nested — flat is easier for the model to reason about" (S3)
- "Input parameters should be unambiguously named: `user_id` not `user`" (S1)
- "Always include type hints for parameters and return values" (S7)
- "Use enums and object structure to make invalid states unrepresentable" (S3)

**Synthesis:** Every layer of nesting is a reasoning step the model must perform. Flat parameter lists with self-documenting names (`source_node_type`, `relationship_label`) reduce the cognitive load on the model. Enums constrain the solution space, reducing hallucinated values.

**Confidence:** Very High

### Claim 4: Tool outputs should be high-signal, agent-actionable — not raw database rows

**Evidence (3 sources: S1, S7, S2):**

- "Return only high-signal information; eschew low-level technical identifiers (uuid, mime_type)" (S1)
- "Tools should return informative error messages so agent can decide: retry, different tool, or ask for clarification" (S7)
- "Prioritize transparency by explicitly showing the agent's planning steps" (S2)

**Synthesis:** Tool responses should contain what the agent needs for its *next decision*, not a complete database dump. For a knowledge graph query, return `{concept: "API Design", related: ["REST", "GraphQL"], confidence: 0.85}` rather than `{id: "uuid-...", created_at: "...", node_type_id: 3, ...}`. Error messages should be prescriptive: "No nodes match 'API desing' — did you mean 'API Design'?" rather than "404 Not Found".

**Confidence:** High

### Claim 5: Simplicity wins — fewer, well-designed tools outperform many fine-grained ones

**Evidence (4 sources: S2, S3, S5, S6):**

- "Most successful implementations use simple, composable patterns" (S2)
- "Functions always called in sequence should be combined" (S3)
- "Tool definitions consume tokens on every call — be concise" (S6)
- "Find the simplest solution possible; increase complexity only when needed" (S2)

**Counterevidence (S8):** "~85% of enterprise prompts require 3+ tools; optimal tool count depends on use case." This suggests the answer is not "fewer is always better" but rather "each tool should be *worth* its token cost."

**Synthesis:** The sweet spot is **8-15 well-designed domain operations** that each accomplish a meaningful unit of agent work. Not 3 (too coarse, loses flexibility) and not 40 (too much selection overhead). Each tool should pass two tests: (1) does it represent a coherent agent intent? (2) would splitting it into smaller tools force the agent to make decisions it shouldn't need to make?

**Confidence:** High

### Claim 6: Namespacing and semantic grouping help agents navigate tool sets

**Evidence (3 sources: S1, S5, S9):**

- "Namespacing tools by service and resource helps agents select the right tools" (S1)
- "Action registries let agents browse capabilities across domains" (S5)
- "Tool naming convention: snake_case, imperative verb prefix (get_*, list_*, create_*)" (S9)

**Synthesis:** For rai-server, a consistent naming scheme like `graph_query`, `graph_remember`, `graph_connect`, `pattern_recall` creates a navigable semantic space. The verb communicates intent; the noun communicates domain.

**Confidence:** High

---

## Contrary Evidence and Tensions

### Tension 1: CRUD familiarity vs domain abstraction
Standard REST/CRUD is well-understood by human developers building integrations. Domain operations require more upfront design and documentation. **Resolution:** Offer both tiers (S4's recommendation). The MCP/agent tier exposes domain operations; a traditional REST tier can serve human developers and programmatic integrations. For rai-server's primary use case (agent consumers), domain operations take priority.

### Tension 2: Tool count — fewer vs expressive
S2 says simplify; S8 says enterprise needs demand many tools. **Resolution:** The evidence suggests the metric is not tool count but *decision burden per task*. 12 well-designed tools that each handle a complete intent are better than 6 tools that require complex parameter combinations OR 30 tools that require selection reasoning.

### Tension 3: Flat parameters vs complex domain operations
Complex domain operations often need structured inputs (e.g., a node with properties and relationships). S3 says keep it flat. **Resolution:** Use flat top-level parameters for the primary intent, with optional structured sub-parameters for advanced use. Example: `graph_remember(concept="API Design", context="E275 research", details={"source": "Anthropic", "confidence": 0.9})`.

---

## Design Principles for rai-server

Based on the triangulated evidence, these principles should guide the API surface:

### P1: Intent-First Operations
Design tools around what agents want to *accomplish*, not what data they want to *mutate*.

| Instead of | Design |
|------------|--------|
| `POST /nodes` + `POST /edges` | `graph_remember(concept, context, relationships)` |
| `GET /nodes?type=pattern` | `pattern_recall(query, scope, limit)` |
| `PUT /nodes/{id}` | `graph_update_concept(concept, changes)` |
| `DELETE /nodes/{id}` + `DELETE /edges?source={id}` | `graph_forget(concept, cascade)` |

### P2: Self-Documenting Parameters
Every parameter name should pass the intern test without reading docs.

```
# Bad
def query(q: str, t: str, n: int) -> dict: ...

# Good
def graph_query(
    search_text: str,        # What to search for
    node_type: NodeType,     # Enum: concept, pattern, decision, ...
    max_results: int = 10    # How many results to return
) -> QueryResult: ...
```

### P3: Agent-Actionable Responses
Return what the agent needs for its next decision.

```python
# Bad — raw database row
{"id": "uuid-...", "node_type_id": 3, "created_at": "2026-...", "meta": "{\"score\": 0.85}"}

# Good — agent-actionable
{"concept": "API Design", "type": "pattern", "relevance": 0.85,
 "related_concepts": ["REST", "GraphQL", "MCP"], "suggested_actions": ["explore REST relationship"]}
```

### P4: Prescriptive Error Messages
Errors should tell the agent what to do, not just what went wrong.

```python
# Bad
{"error": "404", "message": "Not found"}

# Good
{"error": "concept_not_found",
 "message": "No concept matching 'API desing' found",
 "suggestions": ["API Design (confidence: 0.95)", "API Gateway (confidence: 0.72)"],
 "hint": "Try graph_query with a broader search_text"}
```

### P5: Semantic Namespacing
Group tools by domain with consistent verb-noun patterns.

```
graph_query        — Search the knowledge graph
graph_remember     — Store a new concept or relationship
graph_connect      — Create a relationship between concepts
graph_forget       — Remove a concept (with cascade option)
graph_context      — Get full context around a concept

pattern_recall     — Find relevant patterns
pattern_reinforce  — Strengthen a pattern with new evidence

session_log        — Record a session event
session_recall     — Retrieve session history
```

### P6: Progressive Disclosure
Simple use = simple parameters. Advanced use = optional structured parameters.

```python
# Simple: agent just wants to remember something
graph_remember(concept="TDD always", context="E275 coding standards")

# Advanced: agent needs full control
graph_remember(
    concept="TDD always",
    context="E275 coding standards",
    node_type="principle",
    relationships=[{"target": "testing", "type": "belongs_to"}],
    properties={"confidence": 0.95, "source": "team convention"}
)
```

---

## Recommended Tool Surface for rai-server

Based on the evidence, rai-server should expose **12-15 domain operations** organized into 3-4 semantic groups:

### Group 1: Graph Operations (core)
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `graph_query` | Search the knowledge graph by text, type, or relationship | `search_text`, `node_type?`, `max_results?` |
| `graph_remember` | Store a concept, decision, or pattern | `concept`, `context`, `node_type?`, `relationships?` |
| `graph_connect` | Create or strengthen a relationship | `source_concept`, `target_concept`, `relationship_type` |
| `graph_context` | Get full context around a concept (neighbors, paths) | `concept`, `depth?`, `include_types?` |
| `graph_forget` | Remove a concept and optionally its relationships | `concept`, `cascade?` |

### Group 2: Pattern Operations
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `pattern_recall` | Find patterns relevant to current task | `query`, `scope?`, `min_confidence?` |
| `pattern_reinforce` | Strengthen a pattern with new evidence | `pattern_id`, `evidence`, `context?` |
| `pattern_create` | Capture a new reusable pattern | `content`, `context_keywords`, `source?` |

### Group 3: Session Operations
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `session_start` | Begin a work session, load relevant context | `session_type`, `goal`, `project?` |
| `session_log` | Record an event during a session | `event_type`, `content`, `metadata?` |
| `session_close` | Close session, capture learnings | `summary`, `patterns_discovered?` |

### Group 4: Project Operations
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `project_status` | Get current project state and active work | `project_id` |
| `project_search` | Search across projects | `query`, `scope?` |

---

## Key Takeaways

1. **The ontological shift is real.** Agent-consumed APIs are a fundamentally different artifact than developer-consumed APIs. The evidence is unanimous on this point.

2. **Domain operations, not CRUD.** Every source from Anthropic to OpenAI to MuleSoft converges on intent-driven operations. CRUD is a leaking implementation detail.

3. **Descriptions are the interface.** Invest more time in tool descriptions than in schema design. The description is what the agent actually reads.

4. **Flat, self-documenting, constrained.** Flat parameters, enum types, unambiguous names. Make invalid states unrepresentable.

5. **High-signal outputs.** Return what the agent needs next, not everything the database has. Include actionable suggestions in errors.

6. **12-15 tools is the sweet spot** for a domain-specific service like rai-server. Enough to be expressive, few enough to avoid selection overhead.

---

## Sources

Full evidence catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)

Key references:
- [Anthropic: Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI: Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [MuleSoft: Rethinking API Design for Agentic AI](https://blogs.mulesoft.com/automation/api-design-for-agentic-ai/)
- [AgenticAPI.com](https://agenticapi.com/)
- [Anthropic: Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
- [LangChain Tools Guide 2025](https://latenode.com/blog/ai-frameworks-technical-infrastructure/langchain-setup-tools-agents-memory/langchain-tools-complete-guide-creating-using-custom-llm-tools-code-examples-2025)
- [Scale AI: Enterprise Tool Use Benchmark](https://scale.com/leaderboard/tool_use_enterprise)
- [MCP Specification: Tools](https://modelcontextprotocol.io/specification/2025-03-26/server/tools)
- [Paragon: Optimizing Tool Calling](https://www.useparagon.com/learn/rag-best-practices-optimizing-tool-calling/)
- [ZBrain: Knowledge Graphs for Agentic AI](https://zbrain.ai/knowledge-graphs-for-agentic-ai/)
- [Martin Fowler: Function calling using LLMs](https://martinfowler.com/articles/function-call-LLM.html)
