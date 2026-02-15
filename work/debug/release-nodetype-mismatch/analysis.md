# Debug: Release NodeType Validation Error

## Problem Statement

```
WHAT: `rai session start --context` crashes with ValidationError: type 'release'
      not in NodeType Literal when loading graph index.json
WHEN: Every session start since graph was rebuilt after ontology changes (2026-02-13)
WHERE: UnifiedGraph.load() → ConceptNode.model_validate() in context/graph.py
EXPECTED: Session starts cleanly, graph loads all node types including 'release'
```

## 5 Whys Analysis

**Problem:** `rai session start` crashes with `ValidationError: Input should be 'pattern', 'calibration', ... or 'layer'` — `release` not accepted.

1. **Why does validation fail?**
   → The installed CLI (v2.0.0a1) has `NodeType` without `"release"`, but the graph index.json contains nodes with `type: "release"`.

2. **Why is the graph incompatible with the installed CLI?**
   → The graph was built using the **source code** (`rai memory build` from dev environment with editable install or direct execution), which has `"release"` in `NodeType`. But the **installed tool** is an older published version (v2.0.0a1) that predates the ontology change.

3. **Why are the source code and installed package at different versions?**
   → `rai memory build` was run using the local dev source (which includes commit `086b5d0` adding `"release"`), while `uv tool install` still points to PyPI v2.0.0a1. The developer environment has two execution paths: source (for development) and installed (for CLI usage).

4. **Why didn't tests catch this incompatibility?**
   → Tests validate the **build** path (graph creation) and the **load** path (graph deserialization) **independently**, but never test the **cross-version scenario**: graph built by version N loaded by version N-1. There is no schema version or compatibility check in the graph format.

5. **Why is there no schema versioning in the graph?**
   → The graph was designed as an internal artifact where builder and consumer are always the same version. The dual-path execution model (source vs installed) was not anticipated as a failure mode.

**Root Cause:** Missing schema version in graph index.json + no validation of schema compatibility at load time + dual execution paths (dev source vs installed package).

---

## Ishikawa Analysis

```
                    ┌─── Method
                    │    ✓ No schema version in index.json
                    │    ✓ No compatibility check at graph load time
                    │    ✓ Graph format has no migration strategy
                    │
                    ├─── Machine
                    │    (not applicable)
                    │
                    ├─── Material
                    │    ✓ Graph built with source v2 (has "release")
                    │    ✓ CLI consumer is installed v2.0.0a1 (no "release")
VALIDATION ERROR ◄──┤    ✓ Dual execution path: `python -m` vs `uv tool`
                    │
                    ├─── Measurement
                    │    ✓ No cross-version roundtrip test
                    │    ✓ No test for "load graph built by newer version"
                    │    ✓ No integration test: build → save → load cycle
                    │
                    ├─── Manpower
                    │    ✓ Ontology change done in 3 commits across 2 modules
                    │      (models, extractor, parser) — graph consumer not verified
                    │
                    └─── Milieu
                         ✓ Dev machine has source at HEAD but tool at old version
                         ✓ `rai memory build` picks up whichever is in PATH
```

**Most Likely Causes (confirmed):**

1. **No schema version** → Graph format doesn't declare which NodeType set it uses
2. **No forward-compatibility guard** → `ConceptNode` uses strict `Literal` validation — any unknown type is a hard crash instead of a warning
3. **Dual execution path** → Developer runs `build` from source but `session start` from installed package

---

## Investigation Log

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| `release` missing from installed NodeType | Read installed models.py | No `release` in Literal | **Confirmed** |
| `release` present in source NodeType | Grep source models.py | `"release"` on line 36 | **Confirmed** |
| Installed version is old | `uv tool list` | v2.0.0a1 (vs source at HEAD) | **Confirmed** |
| Graph built from source | node source_file says `governance/roadmap.md` | Builder ran with source parsers | **Confirmed** |
| Tests cover cross-version load | Grep tests for schema/version | No tests found | **Confirmed gap** |
| Commit history | `086b5d0` adds release, `9d159ed` is v2.0.0a8 | Fix is post-a1, pre-a8 | **Confirmed** |

---

## Countermeasures

### Immediate Fix (unblock session)

**Option A — Upgrade installed CLI:**
```bash
uv tool upgrade raise-cli  # or reinstall from source
```
This aligns installed ↔ source, but doesn't prevent recurrence.

**Option B — Remove release nodes from graph:**
```bash
# Quick patch to index.json
python3 -c "
import json
data = json.load(open('.raise/rai/memory/index.json'))
data['nodes'] = [n for n in data['nodes'] if n.get('type') != 'release']
json.dump(data, open('.raise/rai/memory/index.json', 'w'), indent=2)
"
```
Lossy — deletes data. Not recommended.

### Structural Prevention (3 measures)

#### P1: Schema Version in Graph (prevent silent incompatibility)

Add a `schema_version` field to `index.json` that tracks the `NodeType` set used at build time. On load, compare and warn/fail gracefully.

```python
# In graph.py save():
{"schema_version": 2, "node_types": list(get_args(NodeType)), "nodes": [...]}

# In graph.py load():
if saved_version > current_version:
    logger.warning("Graph built with newer schema — some nodes may be skipped")
```

#### P2: Graceful Degradation on Unknown Node Types (resilience)

Change `ConceptNode.type` from strict `Literal` validation to accept-and-warn:

```python
# Option: Use a validator that logs warnings for unknown types
@field_validator("type", mode="before")
def validate_type(cls, v):
    valid = get_args(NodeType)
    if v not in valid:
        logger.warning(f"Unknown node type '{v}' — skipping node")
        raise ValueError(f"Unknown node type: {v}")
    return v
```

Or filter at load time in `UnifiedGraph.load()` instead of crashing.

#### P3: Build-Load Roundtrip Test (catch regressions)

Add a test that builds a graph with ALL node types (including release) and verifies it can be loaded back:

```python
def test_build_save_load_roundtrip_all_types(tmp_path):
    """Graph with all NodeType values survives save→load."""
    builder = UnifiedGraphBuilder(project_with_all_sources)
    graph = builder.build()
    graph.save(tmp_path / "index.json")
    loaded = UnifiedGraph.load(tmp_path / "index.json")
    assert loaded.node_count == graph.node_count
    # Verify every NodeType is represented
    for nt in get_args(NodeType):
        assert len(loaded.get_concepts_by_type(nt)) >= 0  # no crash
```

---

## Pattern Extracted

**PAT-205:** Schema evolution without versioning causes silent breakage across execution contexts. When a serialized artifact (graph, config, state) is produced by one version and consumed by another, the format must declare its schema version and the consumer must handle unknown fields gracefully. Strict Literal types in Pydantic models are time bombs when the model evolves — use validation-with-warning at serialization boundaries.

**PAT-206:** Dual execution paths (source dev vs installed package) create version skew that unit tests cannot detect. Any CLI that developers use both to build AND consume artifacts must have an integration test that verifies the installed version can read what the source version produces.

---

## Decision

**Recommended:** Option A (upgrade CLI) for immediate unblock + P1, P2, P3 for structural prevention.

P2 (graceful degradation) is the highest-priority structural fix because it converts hard crashes into warnings, which is the correct behavior at a serialization boundary — you should never crash on data you don't understand, you should skip and warn.

---

*Analysis: 2026-02-15*
*Root cause: Schema evolution without versioning + strict validation at serialization boundary*
*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
