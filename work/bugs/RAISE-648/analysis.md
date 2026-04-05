# RAISE-648: Analysis

## Method: Document directly (cause evident from code)

The crash site is `builder.py:93-102`:

```python
if node.id in seen_ids:
    raise ValueError(msg)  # ← crashes entire build
```

When any two loaders produce nodes with the same ID (e.g., two epic dirs that resolve to the same `epic-e14` ID), the entire graph build fails with an unhandled `ValueError`.

## Root Cause

`GraphBuilder.build()` raises `ValueError` on duplicate node IDs with no recovery path. The design comment says "silent overwrites lose data" — true, but crashing loses the entire graph.

## Fix Approach

1. Add `strict: bool` parameter to `GraphBuilder.__init__()` (default `False`)
2. In `build()`: if duplicate detected and `strict=True`, raise as today. If `strict=False`, log warning with both source files and skip the duplicate (keep first seen).
3. Add `--strict` flag to `rai graph build` CLI command
4. Return list of warnings from `build()` so CLI can report them
