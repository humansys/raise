# Evidence Catalog: Agentic Tool Design Best Practices

> Research date: 2026-02-25
> Scope: Quick scan (12 sources)
> Decision context: rai-server public API design (CRUD vs domain operations)

---

## Evidence Level Scale

| Level | Meaning | Criteria |
|-------|---------|----------|
| **Very High** | Primary source, peer-reviewed or authoritative vendor docs | Direct from model provider or peer-reviewed research |
| **High** | Authoritative practitioner content | Established engineering blogs, official guides |
| **Medium** | Quality secondary analysis | Well-reasoned synthesis from credible authors |
| **Low** | Anecdotal or single-source | Blog posts, tutorials without triangulation |

---

## Source Catalog

### S1: Anthropic — "Writing effective tools for AI agents"
- **URL:** https://www.anthropic.com/engineering/writing-tools-for-agents
- **Type:** Primary vendor guidance
- **Evidence Level:** Very High
- **Date:** 2025
- **Key Findings:**
  - Tools are a new kind of software reflecting a contract between deterministic systems and non-deterministic agents
  - Design tools for agents, not the way you'd write functions/APIs for developers
  - Input parameters should be unambiguously named (e.g., `user_id` not `user`)
  - Use namespacing to group related tools (e.g., `asana_projects_search`, `asana_users_search`)
  - Tool outputs should return only high-signal information; eschew low-level technical identifiers (uuid, mime_type)
  - Describe tools as you would to a new hire — make implicit context explicit
  - Use eval-driven iteration: feed operational records into Claude for automated tool improvement

### S2: Anthropic — "Building effective agents"
- **URL:** https://www.anthropic.com/research/building-effective-agents
- **Type:** Primary vendor research
- **Evidence Level:** Very High
- **Date:** 2024-12
- **Key Findings:**
  - Most successful implementations use simple, composable patterns rather than complex frameworks
  - Maintain simplicity; prioritize transparency; carefully craft your agent-computer interface (ACI)
  - Find the simplest solution possible; only increase complexity when needed
  - Extra abstraction layers obscure prompts/responses and make debugging harder
  - Agentic systems trade latency and cost for better task performance

### S3: OpenAI — Function Calling Guide
- **URL:** https://platform.openai.com/docs/guides/function-calling
- **Type:** Primary vendor documentation
- **Evidence Level:** Very High
- **Date:** 2025 (updated)
- **Key Findings:**
  - Apply the "intern test": can someone correctly use the function given only what you provided to the model?
  - Functions always called in sequence should be combined into one
  - Make arguments flat rather than deeply nested — flat is easier for the model to reason about
  - Offload burden from the model; don't make it fill arguments you already know
  - Fewer than ~100 tools and ~20 args per tool is considered in-distribution
  - Use enums and object structure to make invalid states unrepresentable
  - Always enable strict mode for reliable schema adherence

### S4: MuleSoft — "Rethinking API Design for Agentic AI"
- **URL:** https://blogs.mulesoft.com/automation/api-design-for-agentic-ai/
- **Type:** Industry practitioner (Salesforce/MuleSoft)
- **Evidence Level:** High
- **Key Findings:**
  - Maintain dual API tiers: machine-oriented (high-level business operations) + human-oriented (traditional CRUD)
  - Do NOT overload agents with low-level CRUD endpoints
  - APIs must deliver semantic context and enable autonomous agent reasoning
  - Traditional microservice-based APIs are no longer sufficient for agentic consumers

### S5: AgenticAPI.com — "Agentic API: The new way to API"
- **URL:** https://agenticapi.com/
- **Type:** Industry specification/framework
- **Evidence Level:** Medium
- **Key Findings:**
  - Agentic APIs prioritize actionable intent over CRUD operations
  - Domain-specific verb libraries (e.g., RECONCILE for finance) replace generic CRUD
  - Action registries let agents browse capabilities across domains
  - Verb categories: Compute, Acquire, Orchestrate
  - Chaining empowers agents to orchestrate multi-step workflows in a single flow

### S6: Anthropic — "Advanced Tool Use" and "Tool Search Tool"
- **URL:** https://www.anthropic.com/engineering/advanced-tool-use
- **Type:** Primary vendor engineering
- **Evidence Level:** Very High
- **Date:** 2025
- **Key Findings:**
  - Tool Search Tool: agents search thousands of tools without consuming context window
  - Programmatic Tool Calling: invoke tools in code execution environment
  - Tool Use Examples: universal standard for demonstrating effective tool usage
  - Tool definitions consume tokens on every LLM call — be concise but descriptive

### S7: LangChain — Tool Design Patterns 2025
- **URL:** https://latenode.com/blog/ai-frameworks-technical-infrastructure/langchain-setup-tools-agents-memory/langchain-tools-complete-guide-creating-using-custom-llm-tools-code-examples-2025
- **Type:** Framework documentation
- **Evidence Level:** High
- **Key Findings:**
  - Use verb-noun patterns: `search_database`, `calculate_price`, `fetch_user_data`
  - Docstring is critical — it's how agents decide when to use your tool
  - Include in descriptions: what it does, when to use it, parameter descriptions, return format, example use cases
  - Always include type hints for parameters and return values
  - Tools should return informative error messages so agent can decide: retry, different tool, or ask for clarification

### S8: Scale AI — Enterprise Agentic Tool Use Benchmark (SEAL)
- **URL:** https://scale.com/leaderboard/tool_use_enterprise
- **Type:** Benchmark/evaluation
- **Evidence Level:** High
- **Key Findings:**
  - ~85% of enterprise prompts require at least 3 tools to solve
  - ~20% require 7+ tool calls
  - Enterprise settings require composing larger numbers of expressive APIs correctly
  - Optimal tool count depends on use case, not a universal "fewer is better"

### S9: MCP Specification — Tool Naming and Versioning
- **URL:** https://modelcontextprotocol.io/specification/2025-03-26/server/tools
- **Type:** Protocol specification
- **Evidence Level:** Very High
- **Key Findings:**
  - Tool naming convention: snake_case, imperative verb prefix (`get_*`, `list_*`, `create_*`)
  - 2025-11-25 spec update introduces tool name standardization
  - Version pinning via `tool_requirements`, not hardcoded versioned names
  - Semantic layer abstraction harmonizes definitions for consistent, business-friendly data

### S10: Paragon — "Optimizing Tool Calling"
- **URL:** https://www.useparagon.com/learn/rag-best-practices-optimizing-tool-calling/
- **Type:** Practitioner guide
- **Evidence Level:** Medium
- **Key Findings:**
  - Quality of tool descriptions directly impacts LLM's ability to choose and use tools correctly
  - Use action-oriented language: start descriptions with verbs conveying primary action
  - Incomplete or unclear specs cause wrong tool selection, incorrect arguments, or misunderstood output
  - Extra-detailed descriptions tested against regular descriptions — concise + examples wins

### S11: ZBrain / Graphiti — Knowledge Graphs for Agentic AI
- **URL:** https://zbrain.ai/knowledge-graphs-for-agentic-ai/ and https://github.com/getzep/graphiti
- **Type:** Industry analysis + open-source framework
- **Evidence Level:** Medium
- **Key Findings:**
  - Knowledge graphs provide structured memory, real-time fact retrieval, and rules for grounding AI
  - Multi-modal retrieval strategy: vector search + graph traversal + keyword search
  - Ontology provides semantic grounding: terms resolve to entity types, concepts map to records
  - Query becomes precise traversal through knowledge graph

### S12: Martin Fowler — "Function calling using LLMs"
- **URL:** https://martinfowler.com/articles/function-call-LLM.html
- **Type:** Authoritative practitioner analysis
- **Evidence Level:** High
- **Key Findings:**
  - Tool definitions become part of context on every LLM call — they consume tokens
  - Good naming and descriptions with user-intent mapping help performance
  - Even structured parameters are ingested as tokenized text by the model
  - Define clear function declarations with mandatory vs optional parameter distinction

---

## Evidence Level Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| Very High | 5 | 42% |
| High | 4 | 33% |
| Medium | 3 | 25% |
| Low | 0 | 0% |

**Assessment:** Strong evidence base. 75% of sources are High or Very High quality, with primary vendor documentation from both major model providers (Anthropic, OpenAI) plus protocol specifications (MCP).
