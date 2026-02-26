# Research: API Ontology + MCP Patterns

| Field | Value |
|-------|-------|
| Date | 2026-02-25 |
| Depth | Quick scan |
| Sources | 12 |
| Status | Complete |
| Epic | E275 (Shared Memory Backend) |
| Triggered by | S275.3 planning — need to understand REST/MCP relationship before designing FastAPI routes |

## Research Question

**Primary**: What are the best practices for MCP server tool design? How should a REST API relate to an MCP server that wraps it?

**Secondary**:
1. What patterns do existing MCP servers follow for tool naming, descriptions, and parameter design?
2. How do production MCP servers handle the REST-to-MCP mapping?
3. What does Anthropic's official guidance say about MCP tool design?

## Key Finding (One Line)

A good REST API is NOT a good MCP server — design a shared service layer, let REST serve developers (fine-grained CRUD) and MCP serve agents (outcome-oriented semantic tools).

## Files

| File | Contents |
|------|----------|
| `mcp-patterns-report.md` | Full synthesis with 5 triangulated claims and actionable recommendations |
| `sources/evidence-catalog.md` | 12 sources with URLs, evidence levels, and key findings |

## Decision Captured

For S275.3 (FastAPI bootstrap): Build a clean service layer (`services/` module) that both REST routes and a future MCP server can consume. Do NOT couple REST design to MCP concerns. REST stays RESTful; MCP will be a separate composition layer added later.
