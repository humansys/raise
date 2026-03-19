# RAISE-504: Analysis

## Tier: S (single causal chain)

## 5 Whys

Problem: `rai discover build` produces a redundant unified.json that no consumer reads.

1. Why? -> discover build writes to `.raise/graph/unified.json` (hardcoded L378)
   instead of `.raise/rai/memory/index.json`
2. Why? -> It has its own path instead of using `_get_default_index_path()`
3. Why? -> discover build was created BEFORE graph build (commit 96669de9, E13 f13.4)
4. Why? -> graph build (E11) absorbed all functionality but discover build was never removed
5. Why? -> No post-unification cleanup

Root cause: `discover build` is legacy dead code that survived the graph unification.

## Fix approach

1. Remove `build_command` from discover.py
2. Remove its formatter from output/formatters/discover.py
3. Remove 4 deprecated skills from both .claude/skills/ and skills_base/
4. Clean any remaining references
