# Retrospective: F11.2 Graph Builder

## Summary
- **Feature:** F11.2 Graph Builder
- **Epic:** E11 Unified Context Architecture
- **Started:** 2026-02-03
- **Completed:** 2026-02-03
- **Estimated:** 90 min
- **Actual:** 80 min
- **Velocity:** 1.1x

## What Went Well

- **Pattern reuse:** E2/E8 extractors integrated smoothly with adapters
- **TDD discipline:** Tests caught the `iter_concepts` vs `get_all_concepts` issue immediately
- **Cross-domain relationships:** The explicit (1.0) + heuristic (0.5) weight pattern worked well
- **Integration results:** 151 nodes, 255 edges from 4 sources — exceeded expectations

## What Could Improve

- **Read API before calling:** The method naming mismatch cost a debug cycle
- **Test fixture patterns:** The YAML frontmatter newline issue was avoidable with documented patterns

## Heutagogical Checkpoint

### What did you learn?

1. **Test fixture YAML gotcha:** `dedent("""\n---`)` fails `^---` regex. Use `dedent("""\---`)`.
2. **API discovery:** Iterator methods (`iter_*`) vs collection methods (`get_all_*`) — check actual API.
3. **Keyword matching scales:** ≥2 shared keywords with 0.5 weight produces useful related_to edges.

### What would you change about the process?

1. Read the module's public API before writing integration code
2. Document common test fixture patterns for reuse

### Are there improvements for the framework?

1. Added YAML frontmatter pattern to parking lot for future documentation
2. Consider `get_all_*` aliases for CLI use cases (added to parking lot)

### What are you more capable of now?

1. Building unified graphs from heterogeneous sources (loader → convert → infer pattern)
2. Cross-domain relationship inference with weighted edges
3. NetworkX integration with Pydantic models

## Improvements Applied

- [x] Added test fixture pattern to `dev/parking-lot.md`
- [x] Internalized: Read API before integration

## Action Items

- [ ] Consider adding `get_all_concepts()` / `get_all_relationships()` as aliases (low priority)

---

*Retrospective completed: 2026-02-03*
*Feature contributes to M2: Graph Builds milestone*
