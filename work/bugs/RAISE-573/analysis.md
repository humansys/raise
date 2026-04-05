# RAISE-573: Analysis

## Method: Direct (cause evident from code)

`_infer_depends_on` in `relationships.py:148` filters `if node.type != "module": continue`.

Component nodes (from scanner/discovery) have `depends_on` in metadata with class names (e.g., `["RaiseError"]`), but are never processed because they have `type="component"`.

Two ID resolution strategies coexist:
- **Modules:** `depends_on` contains module names → target is `mod-{name}` (direct)
- **Components:** `depends_on` contains class names → target is `comp-{module}-{ClassName}` (needs name→id lookup)

## Root Cause

`_infer_depends_on` was written for module-to-module edges only. When components were added (discovery/scanner), their `depends_on` metadata was populated but the edge inference was never extended.

## Fix Approach

1. Build a `name→id` index for component nodes: `{metadata["name"]: node.id}`
2. Extend `_infer_depends_on` to also process `type="component"` nodes
3. For component deps: look up target by name in the component index, then fallback to `mod-{name}` for cross-type deps
4. For module deps: unchanged behavior (`mod-{name}` lookup)
