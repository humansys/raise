---
story: S16.2
title: Graph Diff Engine
size: M
type: feature
status: designed
epic: E16
modules: [context, memory, cli]
---

## What & Why

**Problem:** The unified graph is rebuilt from scratch each `rai memory build`, but there's no way to know what changed. Without a diff, `/docs-update` (S16.3) can't know which modules need doc updates, forcing full re-examination every time.

**Value:** A structured diff between graph builds tells downstream consumers exactly what changed, enabling targeted doc updates at story-close. This is the foundation for incremental coherence — small-batch updates instead of periodic big-bang audits.

## Approach

Pure function `diff_graphs(old, new)` in `context/diff.py` compares two `UnifiedGraph` instances by node presence and semantic fields. No edge comparison — edges are derived from nodes and rebuilt each build. The diff is computed by default on every `rai memory build` and persisted for downstream consumption.

**Components:**

| Component | Change | Location |
|-----------|--------|----------|
| `GraphDiff`, `NodeChange` models | Create | `src/rai_cli/context/diff.py` |
| `diff_graphs()` function | Create | `src/rai_cli/context/diff.py` |
| `rai memory build` command | Modify | `src/rai_cli/cli/commands/memory.py` |
| context module `__init__.py` | Modify | `src/rai_cli/context/__init__.py` |

## Data Models

```python
class NodeChange(BaseModel):
    node_id: str
    change_type: Literal["added", "removed", "modified"]
    old_value: ConceptNode | None     # None for "added"
    new_value: ConceptNode | None     # None for "removed"
    changed_fields: list[str]         # e.g. ["metadata", "content"]

class GraphDiff(BaseModel):
    node_changes: list[NodeChange]
    impact: Literal["none", "module", "architectural"]
    affected_modules: list[str]       # mod-* IDs from changed nodes
    summary: str                      # deterministic template string
```

## Core Function

```python
def diff_graphs(old: UnifiedGraph, new: UnifiedGraph) -> GraphDiff
```

**Node comparison:** Two nodes with the same `id` are compared on three fields only: `content`, `type`, `metadata`. Fields `created` and `source_file` are ignored — timestamps regenerate every build and file paths are cosmetic.

**Change detection:**
- Node in new but not old → `added`
- Node in old but not new → `removed`
- Same ID, different `content`/`type`/`metadata` → `modified` with `changed_fields` listing which

**Impact classification:**
- Any `bounded_context` or `layer` node changed/added/removed → `architectural`
- Any `module` node changed/added/removed → `module`
- Otherwise → `none` (only memory, work, pattern nodes changed)

**Affected modules:** Filter `node_changes` for nodes where `type == "module"`, collect their IDs.

**Summary:** Deterministic template:
```
"3 nodes changed (2 modified, 1 added), 2 modules affected (mod-context, mod-memory)"
```

**Edge case — first build (no previous graph):** Return diff with all nodes as `added`, impact derived normally.

## CLI Integration

**`rai memory build` updated flow:**

```
1. Load old graph from index.json (if exists)
2. Build new graph (existing behavior)
3. Diff old vs new (unless --no-diff or no old graph)
4. Save new graph to index.json
5. Save diff to .raise/rai/personal/last-diff.json
6. Print: node/edge counts + diff summary + impact
```

**New flag:** `--no-diff` to skip diff computation (escape hatch for rapid iterative builds).

**CLI output example:**
```
$ rai memory build
Built graph: 347 nodes, 412 edges
Diff: 3 nodes changed (2 modified, 1 added), 2 modules affected (mod-context, mod-memory)
Impact: module
Saved diff to .raise/rai/personal/last-diff.json
```

**No changes example:**
```
$ rai memory build
Built graph: 345 nodes, 410 edges
Diff: no changes
```

## Persistence

- **Diff location:** `.raise/rai/personal/last-diff.json` (gitignored, developer-local)
- **Format:** JSON serialization of `GraphDiff` model
- **Lifecycle:** Overwritten each build. Consumed by `/docs-update` (S16.3). Transient by nature.

## Design Decisions

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Module placement | `context/diff.py` | Diff is a graph operation; all graph types live in context |
| 2 | Comparison fields | `content`, `type`, `metadata` | Avoids false positives from timestamps and file path changes |
| 3 | Old graph source | Load `index.json` before overwriting | Zero extra files, natural flow |
| 4 | Impact levels | `none` / `module` / `architectural` | Three levels match consumer needs; four was over-classified |
| 5 | Edge tracking | Skipped | Edges are derived from nodes, rebuilt each build. Node changes capture the signal. |
| 6 | Summary | Deterministic template | PAT-200: deterministic for structure, inference for content |
| 7 | Diff persistence | `.raise/rai/personal/last-diff.json` | Gitignored, transient, developer-local |
| 8 | Default behavior | Diff on by default, `--no-diff` to skip | Ensures diff always available for lifecycle integration |

## Acceptance Criteria

**MUST:**
- `diff_graphs()` detects added, removed, and modified nodes correctly
- Impact classification distinguishes none/module/architectural
- `affected_modules` derived accurately from node changes
- `rai memory build` diffs by default and persists result
- `--no-diff` flag skips diff computation
- First build (no previous graph) handled gracefully
- Tested against real raise-commons graph snapshots
- All quality gates pass (ruff, pyright, bandit, >90% coverage)

**SHOULD:**
- Diff computation adds negligible overhead to build time
- Summary string is human-readable at a glance

**MUST NOT:**
- Compare `created` or `source_file` fields
- Track edge changes
- Use inference/AI for any part of the diff
