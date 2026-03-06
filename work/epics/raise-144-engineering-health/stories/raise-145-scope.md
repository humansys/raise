# RAISE-145: Scope

## Current State (Discovery)

The "Unified" prefix has **already been removed** from all Python source classes:

| Former Name | Current Name | Location |
|---|---|---|
| `UnifiedGraph` | `Graph` | `packages/rai-core/src/rai_core/graph/engine.py` |
| `UnifiedQueryStrategy` | `QueryStrategy` | `packages/rai-core/src/rai_core/graph/query.py` |
| `UnifiedQuery` | `Query` | `packages/rai-core/src/rai_core/graph/query.py` |
| `UnifiedQueryMetadata` | `QueryMetadata` | `packages/rai-core/src/rai_core/graph/query.py` |
| `UnifiedQueryResult` | `QueryResult` | `packages/rai-core/src/rai_core/graph/query.py` |
| `UnifiedQueryEngine` | `QueryEngine` | `packages/rai-core/src/rai_core/graph/query.py` |
| `UnifiedGraphBuilder` | `GraphBuilder` | `src/rai_cli/context/builder.py` |

### Remaining "Unified" references (not class names)

1. **Docstring ADR references** -- "ADR-019 Unified Context Graph Architecture" in `models.py`, `engine.py`, `query.py`, `builder.py`. These refer to the ADR title itself, not class names.
2. **Discovery artifacts** -- `work/discovery/components-validated.json` and `components-draft.yaml` contain stale `UnifiedX` class signatures. These will be corrected by re-running discovery.
3. **Test fixture strings** -- Various test files use "Unified" in test data strings (not class references).
4. **Epic design docs** -- Historical design docs in `work/epics/e11-unified-graph/` and `work/epics/e15-ontology-refinement/`.

## In Scope

- Verify no `Unified`-prefixed class names remain in Python source
- Update stale discovery artifacts (`components-validated.json`, `components-draft.yaml`) via re-scan
- Clean up docstring references if they refer to classes (keep ADR title references)

## Out of Scope

- Renaming the ADR title itself ("ADR-019 Unified Context Graph Architecture" stays)
- Editing historical epic design docs (those are point-in-time records)
- Changing test fixture strings that use "Unified" as test data (not class refs)

## Done Criteria

1. No Python source file contains a class definition with `Unified` prefix
2. Discovery artifacts reflect current class names
3. All tests pass (`uv run pytest`)
4. Type checks pass (`uv run pyright`)
5. Lint passes (`uv run ruff check`)
