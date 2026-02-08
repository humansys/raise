# Progress: S15.3 Constraint Edges

## Status
- **Started:** 2026-02-08
- **Current Task:** 3 of 3
- **Status:** Complete

## Completed Tasks

### Task 1: Guardrails frontmatter + parser scope propagation
- **Duration:** ~8 min
- **Notes:** Added YAML frontmatter to guardrails.md, 3 new helper functions (_parse_frontmatter, _strip_frontmatter, _extract_prefix), updated extract_guardrails() to propagate constraint_scope. 9 new tests, all GREEN. Pyright clean.

### Task 2: Schema + builder constraint edges
- **Duration:** ~7 min
- **Notes:** Added constrained_by to EdgeType. Added _extract_constraints() to builder — reads scope from guardrail metadata, creates edges. Updated build() to call after structural nodes. 6 new tests, all GREEN.

### Task 3: Integration test — rebuild graph, verify edges
- **Duration:** ~3 min
- **Notes:** Graph rebuilt: 847 nodes, 6093 edges, 195 constrained_by edges (exactly as designed). Two-hop traversal verified: mod-memory → bc-ontology → 21 guardrails. Override scopes correct: bc-ontology has MUST-ARCH, bc-governance does not.

## Blockers
- None

## Discoveries
- pyright strict mode not available via CLI flag in this env — use pyright without --strict (pyproject.toml config handles strictness)
