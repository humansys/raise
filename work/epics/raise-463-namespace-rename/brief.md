# RAISE-463: Package Namespace Rename — Brief

## Problem Hypothesis

Users installing `rai-cli` from PyPI get Robotec.AI's `rai-core` instead of
HumanSys's internal `rai-core`. This causes import failures because
`rai_core.graph.models` doesn't exist in Robotec.AI's package.

The workaround (downgrade to rai-cli 2.1.0) is temporary — the namespace
collision must be resolved at the source.

## Success Metrics

1. `pip install raise-cli` resolves `raise-core` correctly from PyPI
2. Zero `rai_core` imports remain in source (all become `raise_core`)
3. CLI command stays `rai` — no user-facing change
4. All tests pass after rename
5. Published as v2.2.1 on PyPI under `raise-cli` / `raise-core`

## Appetite

Small-medium. Mechanical rename across 3 packages (~35+ files).
Target: 1-2 sessions.

## Rabbit Holes

- Don't refactor module structure — pure rename only
- Don't change CLI command name
- Don't rename work artifacts, governance docs, or historical references
- Don't deprecate old `rai-cli` PyPI package (separate effort if needed)
