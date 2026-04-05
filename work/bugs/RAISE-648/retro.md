# Retrospective: RAISE-648

## Summary
- Root cause: `GraphBuilder.build()` raises ValueError on duplicate node IDs with no recovery — kills entire graph and all downstream consumers
- Fix approach: `strict` param (default False) → warn+skip duplicates, store warnings. `--strict` CLI flag for CI.
- Classification: Functional/S1-High/Design/Incorrect

## Process Improvement
**Prevention:** Infrastructure components (graph builder, indexers, aggregators) should never crash on data quality issues. Default to graceful degradation with observability (warnings, metrics). Reserve hard failures for `--strict` / CI mode.
**Pattern:** Functional + Design + Incorrect → crash-on-bad-data instead of degrade-on-bad-data in infrastructure component.

## Heutagogical Checkpoint
1. Learned: The ID generation uses only the numeric prefix of epic dirs (`e(\d+)`) — this is the upstream cause (RAISE-1204). The memory loader already handles duplicates gracefully via `_deduplicate_by_precedence`. The builder was the only place that crashed.
2. Process change: When reviewing data-processing code, ask "what happens with bad input?" — crash is rarely the right answer for infrastructure.
3. Framework improvement: The `builder.warnings` list pattern is reusable — any builder/processor that can degrade should collect warnings for the CLI layer to report.
4. Capability gained: Full understanding of the graph build pipeline: loaders → builder dedup → structural extraction → CLI reporting.

## Patterns
- Added: PAT-E-728 (graceful degradation on duplicate node IDs)
- Reinforced: none evaluated
