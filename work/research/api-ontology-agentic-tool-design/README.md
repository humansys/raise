# Research: Agentic Tool Design — API Ontology for AI Consumers

## Metadata

| Field | Value |
|-------|-------|
| **Research ID** | R-E275-001 |
| **Date** | 2026-02-25 |
| **Researcher** | Rai (Claude Opus 4.6) |
| **Depth** | Quick scan (12 sources) |
| **Decision context** | rai-server public API design for E275 |
| **Status** | Complete |

## Research Question

What are the best practices for designing tools/endpoints that AI agents consume? What ontological principles should guide API surface design when the primary consumers are LLM-based agents?

## Files

| File | Purpose |
|------|---------|
| [agentic-tool-design-report.md](agentic-tool-design-report.md) | Full synthesis with triangulated claims, design principles, and recommended tool surface |
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | 12 sources with evidence levels, URLs, and key findings |

## Key Conclusion

Design domain-level intent operations (12-15 tools), not CRUD endpoints (30+). The evidence is unanimous across Anthropic, OpenAI, MuleSoft, MCP spec, and LangChain: agent-consumed APIs are a fundamentally different artifact than developer-consumed APIs.

## Triangulated Claims (3+ sources each)

1. Domain operations outperform CRUD for agent consumers (5 sources, Very High confidence)
2. Tool descriptions are the primary interface (5 sources, Very High confidence)
3. Flat parameters with unambiguous names beat nested structures (3 sources, Very High confidence)
4. Tool outputs should be high-signal and agent-actionable (3 sources, High confidence)
5. Fewer well-designed tools outperform many fine-grained ones (4 sources, High confidence)
6. Namespacing and semantic grouping aid tool selection (3 sources, High confidence)

## Evidence Quality

- Very High: 5 sources (42%)
- High: 4 sources (33%)
- Medium: 3 sources (25%)
- Low: 0 sources (0%)
