# RAISE-573: Plan

## Tasks

### T1: Regression test — component depends_on not wired (RED)
- Test that `_infer_depends_on` produces edges for component nodes with depends_on metadata
- Test: component with `depends_on: ["RaiseError"]` → edge to `comp-exceptions-RaiseError`
- Test: component dep not found → no edge (no crash)
- Test: module behavior unchanged
- Verify: `uv run pytest packages/raise-cli/tests/context/test_relationships.py -x -k depends_on` — FAILS
- Commit: `test(RAISE-573): regression test for component depends_on edge inference`

### T2: Extend _infer_depends_on for components (GREEN)
- Build `comp_name_index: dict[str, str]` mapping `metadata["name"]` → `node.id` for component nodes
- Extend loop: process `type in ("module", "component")`
- For modules: target = `mod-{dep_name}` (unchanged)
- For components: target = `comp_name_index.get(dep_name)` then fallback `mod-{dep_name}`
- Verify: `uv run pytest packages/raise-cli/tests/context/test_relationships.py -x -k depends_on` — PASSES
- Commit: `fix(RAISE-573): wire component depends_on to graph edges`
