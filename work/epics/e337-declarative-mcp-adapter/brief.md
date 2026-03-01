# Epic Brief: E337 — Declarative MCP Adapter Framework

## Hypothesis

If we provide a declarative YAML-based adapter system for MCP servers, then integrating new external services (GitHub, Linear, GitLab) will require ~50-80 lines of YAML instead of ~400 LOC of Python, reducing integration time from days to hours and enabling non-framework developers to add integrations.

## Success Metrics

| Metric | Target |
|--------|--------|
| YAML config size | 50-80 lines per adapter |
| New adapter effort | < 1 hour for standard PM protocol |
| Expression evaluator size | ~100 LOC, zero external deps |
| Existing adapters unaffected | Jira, Confluence, Filesystem unchanged |
| Test coverage | Unit + integration for all new modules |

## Appetite

**Time box:** 1 week (7 stories: 4S + 1M + 2XS)
**Critical path:** S1 → S2 → S3 → S4 (expression → schema → adapter → registry)

## Rabbit Holes

- **Jinja2 scope creep:** Mini evaluator handles dot-access + 4 filters. If users need more, revisit — but not now.
- **Auto-discovery (Level 3):** BM25 tool search by intent is future work. Stay at Level 2 declarative.
- **Docs protocol complexity:** Only 5 methods vs 11 PM methods. Should be straightforward extension.
- **MCP server process management:** McpBridge already handles this. Don't re-invent.

## References

- Research: `dev/research/declarative-mcp-adapter-design.md`
- Existing bridge: `src/rai_cli/adapters/mcp_bridge.py`
- Existing registry: `src/rai_cli/adapters/registry.py`
- Protocols: `src/rai_cli/adapters/protocols.py`
