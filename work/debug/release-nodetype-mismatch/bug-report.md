# BUG: Graph Schema Evolution Causes Hard Crash on Session Start

**Severity:** Critical (blocks all CLI operations that load the graph)
**Detected:** 2026-02-15
**Root Cause:** Schema evolution without versioning + strict Literal validation at serialization boundary
**Status:** Immediate fix applied (CLI upgrade). Structural countermeasures pending.

---

## Problem

`rai session start --context` crashes with `ValidationError` when the graph `index.json` contains node types not recognized by the installed CLI version.

```
ValidationError: 1 validation error for ConceptNode
type
  Input should be 'pattern', 'calibration', ... or 'layer'
  [type=literal_error, input_value='release', input_type=str]
```

**Impact:** Complete session blockage. No session start, no context loading, no memory queries. The CLI becomes unusable until the version mismatch is resolved.

**Trigger:** Graph was built using source code at HEAD (which includes `"release"` in `NodeType`), but the installed CLI was at v2.0.0a1 (which does not).

---

## Ishikawa Analysis (Root Cause Diagram)

```
                         ┌─── METHOD
                         │    [M1] No schema version in index.json
                         │    [M2] No compatibility check at graph load time
                         │    [M3] No migration/degradation strategy for
                         │         unknown node types
                         │    [M4] Strict Literal type in Pydantic rejects
                         │         any unknown value with hard crash
                         │
                         ├─── MATERIAL (Data/Dependencies)
                         │    [D1] Graph built with source v2 HEAD
                         │         (has "release" in NodeType)
                         │    [D2] CLI installed from PyPI v2.0.0a1
                         │         (does NOT have "release")
GRAPH LOAD CRASH ◄───────┤    [D3] Dual execution path: `python -m`
                         │         (source) vs `uv tool` (installed)
                         │    [D4] `rai memory build` picks up whichever
                         │         Python path is active
                         │
                         ├─── MEASUREMENT (Testing)
                         │    [T1] No cross-version roundtrip test
                         │         (build with v_N, load with v_N-1)
                         │    [T2] No test for "load graph with unknown
                         │         node type"
                         │    [T3] Build and load tested independently
                         │         but never as integrated pipeline
                         │    [T4] No contract test between graph
                         │         producer and consumer
                         │
                         ├─── MANPOWER (Process)
                         │    [P1] Ontology change done across 3 commits
                         │         in 2 modules — graph consumer not
                         │         verified against installed version
                         │    [P2] No checklist for "adding a new
                         │         NodeType" that includes consumer
                         │         compatibility verification
                         │
                         └─── MILIEU (Environment)
                              [E1] Dev machine has source at HEAD
                                   but tool installed at old version
                              [E2] No CI gate that verifies installed
                                   CLI can load a graph built by source
```

### Contributing Factors Ranked by Impact

| Factor | Impact | Preventability |
|--------|--------|----------------|
| **[M4] Strict Literal + no fallback** | **Critical** — converts data issue into hard crash | High — change validation strategy |
| **[T1] No cross-version test** | **High** — would have caught this immediately | High — add one test |
| **[M1] No schema version** | **Medium** — would enable graceful detection | Medium — add field + logic |
| **[D3] Dual execution path** | **Medium** — creates the version skew scenario | Low — inherent to dev workflow |
| **[P2] No NodeType change checklist** | **Low** — process gap, not code gap | Medium — add to guardrails |

---

## 5 Whys Chain

```
1. WHY does session start crash?
   → ConceptNode validation rejects type="release" because it's not in NodeType Literal.

2. WHY is "release" in the graph but not in the model?
   → Graph was built using source code (commit 086b5d0, which added "release"),
     but CLI is installed from PyPI v2.0.0a1 (pre-086b5d0).

3. WHY are source and installed CLI at different versions?
   → `rai memory build` ran from dev environment (source at HEAD),
     `rai session start` runs from `uv tool install` (v2.0.0a1).

4. WHY didn't tests catch this?
   → Tests verify build and load independently, never the cross-version scenario.
     No test exercises "load a graph that contains a NodeType I don't know about."

5. WHY is there no resilience for unknown node types?
   → The graph was designed assuming producer and consumer are always the same
     version. Strict Literal validation was chosen for type safety without
     considering serialization boundary implications.

ROOT CAUSE: Strict validation at a serialization boundary without schema versioning
or graceful degradation. The system treats persisted data as trusted internal data
instead of as external input that may evolve independently.
```

---

## Countermeasures

### CM-1: Graceful Degradation on Unknown Node Types (Priority: CRITICAL)

**What:** Change `UnifiedGraph.load()` to skip nodes with unknown types instead of crashing. Log a warning with the unknown type and node ID.

**Why:** At serialization boundaries, unknown data should be skipped, not cause crashes. This is the single most impactful fix — it converts a complete system failure into a minor data loss with observability.

**Implementation:**

```python
# In UnifiedGraph.load() or ConceptNode validation:
def load(cls, path: Path) -> UnifiedGraph:
    data = json.loads(path.read_text())
    valid_types = set(get_args(NodeType))
    graph = UnifiedGraph()

    for node_data in data.get("nodes", []):
        if node_data.get("type") not in valid_types:
            logger.warning(
                f"Skipping node '{node_data.get('id')}' with unknown type "
                f"'{node_data.get('type')}'. Graph may have been built with "
                f"a newer version. Run 'rai memory build' to rebuild."
            )
            continue
        node = ConceptNode.model_validate(node_data)
        graph.add_concept(node)
    ...
```

**User-facing message when this happens:**
```
⚠ Warning: Graph contains 2 nodes with unknown types (release).
  This usually means the graph was built with a newer CLI version.

  To fix:
  1. Upgrade CLI: uv tool upgrade raise-cli
  2. Or rebuild graph: rai memory build

  Session will continue with available nodes.
```

**Acceptance criteria:**
- [ ] Unknown node types are skipped with warning, not crash
- [ ] Warning message tells user how to fix
- [ ] Test: load graph with unknown type → succeeds with warning
- [ ] Test: all known types still load correctly

### CM-2: Schema Version in Graph Index (Priority: HIGH)

**What:** Add `schema_version` integer to `index.json`. Increment when `NodeType` or `EdgeType` change.

**Implementation:**

```python
# graph.py save():
{
    "schema_version": 2,  # Increment on NodeType/EdgeType changes
    "node_types": list(get_args(NodeType)),  # Self-documenting
    "nodes": [...],
    "edges": [...]
}

# graph.py load():
saved_version = data.get("schema_version", 1)
if saved_version > CURRENT_SCHEMA_VERSION:
    logger.warning(
        f"Graph schema version {saved_version} is newer than "
        f"CLI schema version {CURRENT_SCHEMA_VERSION}. "
        f"Some features may be unavailable."
    )
```

**Acceptance criteria:**
- [ ] `schema_version` field in index.json
- [ ] Version incremented when NodeType/EdgeType change
- [ ] Warning on version mismatch
- [ ] Test: load older schema version → succeeds
- [ ] Test: load newer schema version → warning + graceful

### CM-3: Build-Load Roundtrip Test (Priority: HIGH)

**What:** Add integration test that builds a graph with ALL node types and verifies save→load roundtrip.

**Implementation:**

```python
def test_build_save_load_roundtrip_all_types(tmp_path: Path) -> None:
    """Graph with all NodeType values survives save→load."""
    # Create project with all source types (governance, memory, work, etc.)
    builder = UnifiedGraphBuilder(project_with_all_sources)
    graph = builder.build()
    graph.save(tmp_path / "index.json")

    loaded = UnifiedGraph.load(tmp_path / "index.json")
    assert loaded.node_count == graph.node_count

    # Verify every NodeType is represented and loads
    for nt in get_args(NodeType):
        loaded.get_concepts_by_type(nt)  # Should not crash
```

**Acceptance criteria:**
- [ ] Test exists and passes
- [ ] Test covers all current NodeType values
- [ ] Test fails if a new NodeType is added without graph support

### CM-4: NodeType Change Guardrail (Priority: MEDIUM)

**What:** Add to `guardrails.md` a checklist for adding new NodeType values.

**Content:**
```markdown
### Adding a New NodeType

When adding a new value to `NodeType` in `context/models.py`:

1. [ ] Add to `NodeType` Literal in `context/models.py`
2. [ ] Add to `ConceptType` enum in `governance/models.py` (if governance-sourced)
3. [ ] Add builder support in `context/builder.py` (load method)
4. [ ] Add to `schema_version` increment
5. [ ] Verify build-load roundtrip test still passes
6. [ ] Run `rai memory build` to verify no crash
7. [ ] Verify installed CLI version can load the rebuilt graph
```

---

## Immediate Fix Applied

```bash
uv tool install --force /home/emilio/Code/raise-commons
# Installed rai-cli v2.0.0a8 from source (was v2.0.0a1)
# + rebuilt graph with `rai memory build`
# + verified `rai session start` works
```

---

## Patterns Extracted

**PAT-205:** Schema evolution without versioning causes silent breakage across execution contexts. When a serialized artifact (graph, config, state) is produced by one version and consumed by another, the format must declare its schema version and the consumer must handle unknown fields gracefully. Strict Literal types in Pydantic models are time bombs when the model evolves — use validation-with-warning at serialization boundaries.

**PAT-206:** Dual execution paths (source dev vs installed package) create version skew that unit tests cannot detect. Any CLI that developers use both to build AND consume artifacts must have an integration test that verifies the installed version can read what the source version produces.

---

## Conversation Reference

This bug was discovered and analyzed during session SES-174 (2026-02-15). The full Ishikawa analysis, investigation log, and fix verification are documented in this conversation.

---

*Analysis: 2026-02-15*
*Analyst: Rai (Claude Opus 4.6)*
*Verified by: Emilio Osorio*
