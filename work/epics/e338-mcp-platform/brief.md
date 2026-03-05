# Epic Brief: E338 — MCP Platform

## Hypothesis

Si desacoplamos el McpBridge de los adapters de dominio y lo exponemos como infraestructura genérica de RaiSE, entonces se reducirán los tokens consumidos por sesión al usar MCPs (bridge vs directo en IDE) para el equipo de desarrollo, medido por comparación de token usage en sesiones con MCP nativo vs MCP via bridge.

## Success Metrics

- Context7 registered and callable via `rai mcp call` E2E
- Zero tool schema tokens injected into agent context (vs ~200+ per MCP tool natively)
- Telemetry events emitted for every bridge call
- All existing adapter tests pass after bridge move

## Appetite

7 stories (2M + 5S). Three milestones: Walking Skeleton → CLI Complete → Full Platform.

## Rabbit Holes

- Do NOT add static tool filtering (include/exclude) — token savings are structural (AR-Q3)
- Do NOT add tool catalog cache — `list_tools()` is fast enough (AR-R1)
- Do NOT add `rai mcp stats` — needs event persistence (AR-R2)
- Do NOT auto-detect package type in install — explicit `--type` flag (AR-R3)

## References

- Problem Brief: `work/problem-briefs/mcp-bridge-independence-2026-03-01.md`
- ADR-042: `dev/decisions/adr-042-mcp-infrastructure-layer.md`
- Scope: `work/epics/e338-mcp-platform/scope.md`
- Design: `work/epics/e338-mcp-platform/design.md`
