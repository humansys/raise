# Epic Retrospective: E337 — Declarative MCP Adapter Framework

## Summary

| Field | Value |
|-------|-------|
| Epic | E337 |
| Stories | 5/5 complete |
| Duration | 2 sessions (SES-312, SES-313) |
| New files | 16 source + 6 test modules |
| LOC added | ~2,600 (source + tests) |
| Tests | 117 (26 + 35 + 14 + 9 + 9 + existing) |
| Avg velocity | 1.56x |
| QR fixes | 5 total (2+2+1) |
| Patterns | 5 new (PAT-E-601 through PAT-E-605) |

## Story Results

| Story | Size | Velocity | Tests | QR Fixes |
|-------|------|----------|-------|----------|
| S337.1: Expression evaluator + schema | S | 1.5x | 26 | 0 |
| S337.2: DeclarativeMcpAdapter (PM) | M | 1.8x | 35 | 0 |
| S337.3: YAML discovery in resolver | S | 1.6x | 14 | 2 |
| S337.4: Docs protocol support | S | 1.3x | 9 | 1 |
| S337.5: Reference config + validation CLI | S | 1.6x | 9 | 2 |

## Architecture Delivered

```
src/rai_cli/adapters/declarative/
├── __init__.py          — Public API (7 exports)
├── adapter.py           — DeclarativeMcpAdapter (PM + Docs, AR-Q1)
├── discovery.py         — YAML scanner + factory closures (AR-C1)
├── expressions.py       — ExpressionEvaluator (dot-access, filters)
├── schema.py            — Pydantic config models (5 classes)
└── reference/
    └── github.yaml      — Reference config, all 11 PM methods

src/rai_cli/cli/commands/
├── _resolve.py          — YAML + EP merge, lazy imports (AR-C2)
└── adapters.py          — rai adapter {list,check,validate}
```

## Done Criteria

- [x] Any MCP server can be integrated via YAML config (validated by reference github.yaml)
- [x] `rai backlog --adapter <name>` works with YAML-defined adapter (via resolver integration)
- [x] `rai adapter validate` catches invalid configs with clear errors
- [x] Existing adapters (Jira, Confluence, Filesystem) unaffected (EP priority, lazy imports)
- [x] All new code has unit + integration tests (117 tests)
- [ ] ADR-041 accepted and referenced (referenced in code, ADR doc deferred)

## What Went Well

1. **Velocity consistency.** All 5 stories between 1.3x-1.8x — no blockers, no pivots.
2. **QR as safety net.** Quality reviews caught 5 issues the machines missed: eager imports defeating lazy strategy (PAT-E-602), duplicate name silencing (PAT-E-603), protocol-aware search type mismatch (PAT-E-604), stale docstrings (PAT-E-605).
3. **Architecture decisions paid off.** AR-Q1 (one class, both protocols) avoided duplication. AR-C1 (factory closures) solved no-arg instantiation cleanly. AR-R1 (no model field) eliminated a registry.
4. **Design → ontological naming.** The user's question "why is it adapters and not adapter?" improved CLI consistency across the board.

## What to Improve

1. **Bulk replace_all on short tokens is risky.** PAT-E-605 — hit JSON data keys in addition to CLI command names.
2. **ADR not written.** ADR-041 is referenced in code but the actual ADR doc doesn't exist yet. Low priority — code is the ground truth.

## Key Patterns Discovered

| ID | Pattern |
|----|---------|
| PAT-E-602 | Eager `__init__.py` re-export defeats lazy import strategy |
| PAT-E-603 | Duplicate-name collision handling — first-wins with warning |
| PAT-E-604 | Multi-protocol adapter with homonymous methods needs protocol discriminator |
| PAT-E-605 | Bulk replace_all on short tokens needs diff review |

## Risks Realized

| Risk from scope | Realized? | Impact |
|-----------------|-----------|--------|
| Expression evaluator insufficient | No | Filters covered all cases |
| MCP response format varies | No | items_path + fields handled nesting |
| Registry collision YAML vs EP | Tested | EP wins via dict merge order |
