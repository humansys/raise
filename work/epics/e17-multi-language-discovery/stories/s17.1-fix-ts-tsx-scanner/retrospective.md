# Retrospective: S17.1 — Fix TS/TSX Scanner

## Summary
- **Story:** S17.1
- **Epic:** E17 Multi-Language Discovery
- **Started:** 2026-02-09
- **Completed:** 2026-02-09
- **Estimated:** 60 minutes (M-sized)
- **Actual:** ~45 minutes

## What Went Well
- TDD cycle was clean — each task had focused tests that caught real issues
- The exclude-based hierarchy routing was the right call — simple change, future-proof
- Interactive design session with Emilio surfaced the `build_hierarchy()` silent data loss risk early
- All 150 discovery tests pass, ruff clean, pyright clean
- The brace expansion risk (identified in plan) was caught and handled with multi-pattern glob + dedup

## What Could Improve
- Initial design proposed regex for Svelte extraction — Emilio correctly asked "why aren't we using treesitter?" Shows bias toward simpler but less consistent approaches
- Graph memory queries during `/epic-design` didn't meaningfully inform design decisions — parked for research

## Heutagogical Checkpoint

### What did you learn?
- tree-sitter-typescript has separate `language_typescript()` and `language_tsx()` functions — TSX is a different grammar, not a superset mode
- Python's `Path.glob()` doesn't support brace expansion (`{ts,tsx}`) — need separate glob calls with dedup
- Exported const extraction requires walking 3 levels deep: `export_statement → lexical_declaration → variable_declarator`
- `build_hierarchy()` was silently dropping any symbol kind not in its include list — this is the kind of bug that goes unnoticed until a customer demo fails

### What would you change about the process?
- The design session was valuable for a story this size — interactive design caught the hierarchy routing risk that a solo design would have missed
- Task decomposition granularity was right for M-sized story (5 tasks)

### Are there improvements for the framework?
- Consider a "pipeline impact trace" as a standard step in story-design when adding new enum/literal values — trace every consumer of the type to identify silent drops

### What are you more capable of now?
- Better understanding of tree-sitter TypeScript/TSX grammar structure
- Pattern for multi-extension glob handling in Python
- Awareness of include-based vs exclude-based routing tradeoffs in type-dispatched pipelines

## Improvements Applied
- PAT-230: Exclude-based routing over include-based for type-dispatched pipelines (prevents silent data loss)
- PAT-231: Pipeline impact trace when expanding Literal types — trace every consumer to find silent drops

## Action Items
- [ ] Research: Graph memory effectiveness in design sessions (parked in parking lot)
- [x] WorkLifecycle `init` phase bug parked as urgent in parking lot
