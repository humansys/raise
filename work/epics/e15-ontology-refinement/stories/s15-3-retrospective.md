# Retrospective: S15.3 Constraint Edges

## Summary
- **Story:** S15.3 Constraint Edges
- **Size:** S (3 SP)
- **Design:** SES-094 (separate session — challenged hardcoded mapping, audited pipeline, revised to data-driven)
- **Implement:** ~18 min (3 tasks, single pass, all GREEN)
- **Velocity:** 3.3x (S story at ~18 min vs ~60 min baseline)

## What Went Well

- **Data-driven design paid off** — The decision to put scope mapping in guardrails.md frontmatter instead of hardcoding in builder made the implementation trivially clean. `_extract_constraints()` is 25 lines, no conditional logic about categories.
- **Design investment in SES-094** — Challenging the original hardcoded approach added ~20 min to design but eliminated an entire class of maintenance burden. PAT-183 (grounding over speed) validated again.
- **TDD single-pass** — All 15 new tests written RED, all went GREEN on first implementation pass. Zero rework.
- **Exact edge count match** — 195 constrained_by edges, exactly as predicted in design. This validates the scope calculation methodology.

## What Could Improve

- Nothing significant. The story flowed exactly as designed.

## Heutagogical Checkpoint

### What did you learn?
- **Poka-yoke through data design:** By making the builder "dumb" (reads metadata, doesn't interpret), the scope mapping is impossible to get wrong at the code level — errors can only happen in the governance data, which is human-readable and reviewable.
- **Frontmatter as the integration point:** guardrails.md is both human documentation and machine-readable data. The `_parse_frontmatter` / `_strip_frontmatter` pattern is reusable for the 4 remaining governance docs (constitution, prd, vision, glossary).

### What would you change about the process?
- Nothing. The design-first approach with challenge (SES-094) caught the hardcoded mapping anti-pattern before implementation.

### Are there improvements for the framework?
- The frontmatter parser pattern (`_parse_frontmatter`, `_strip_frontmatter`) should be extracted to a shared utility when the next governance doc gets frontmatter (parking lot item already exists).

### What are you more capable of now?
- Extending the ontology graph with new edge types and scope-aware edge generation is now a well-understood, repeatable pattern.

## Improvements Applied
- None needed — process worked well.

## Metrics

| Metric | Value |
|--------|-------|
| Files changed | 5 source + 2 test + 3 docs |
| New tests | 15 (9 parser + 6 builder) |
| Total tests | 1351 (all pass) |
| Coverage | 92.28% |
| Graph | 847 nodes, 6093 relationships |
| New edges | 195 constrained_by |
| Commits | 3 implementation + 3 docs |
