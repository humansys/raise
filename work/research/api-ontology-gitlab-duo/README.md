# Research: GitLab Duo Tool/Action Design for RaiSE Integration

| Field | Value |
|-------|-------|
| Date | 2026-02-25 |
| Depth | Quick Scan (12 sources) |
| Decision | API surface design for RaiSE knowledge graph backend as GitLab Duo integration |
| Status | Complete |
| Confidence | High (official docs + blog posts + community evidence) |

## Research Question

**Primary**: What are the best practices for designing tools/actions for GitLab Duo? How does GitLab Duo consume external tools and what patterns should tool providers follow?

**Secondary**:
1. How does GitLab Duo's tool/action system work (architecture, constraints)?
2. What extension points exist for third-party tools in GitLab Duo?
3. Does GitLab Duo support MCP or does it have its own tool protocol?
4. What are GitLab's published best practices for AI tool integration?

## Key Findings (TL;DR)

1. **GitLab Duo natively supports MCP** -- both as client (consuming external MCP servers) and as server (exposing GitLab to external AI tools). This is the primary integration path for third-party tools.
2. **Three integration paths exist**: MCP server (RaiSE exposes tools), External Agent (RaiSE runs as agent), Custom Agent (GitLab user configures agent with RaiSE MCP).
3. **MCP is the recommended path** for RaiSE. Building an MCP server lets GitLab Duo Chat (Agentic) consume our knowledge graph tools directly.
4. **Transport support**: stdio, HTTP, and SSE transports are all supported.
5. **GitLab has its own Knowledge Graph** -- understanding its scope helps position RaiSE as complementary (cross-platform, process-aware) rather than competing.

## Files

| File | Purpose |
|------|---------|
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | All sources with evidence levels |
| [gitlab-duo-report.md](gitlab-duo-report.md) | Full synthesis with triangulated claims and recommendations |
