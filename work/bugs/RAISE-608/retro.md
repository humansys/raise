# Retrospective: RAISE-608

## Summary
- Root cause: `pattern add` defaulted to `personal` scope; `pattern reinforce` defaulted to `project` scope — different files, silent round-trip failure
- Fix approach: Change `pattern add` default from `"personal"` to `"project"` — one-line change

## Heutagogical Checkpoint
1. Learned: Inconsistent defaults between paired commands create silent failures. The existing test `test_add_pattern_defaults_to_personal_scope` was documenting the bug as intended behavior — a sign that the asymmetry had been present from the start.
2. Process change: Before finalizing paired commands (write/read, add/reinforce), verify that the default scope round-trip works end-to-end without explicit flags.
3. Framework improvement: `/rai-bugfix` analyse step could include "check default symmetry for paired commands" as a heuristic for CLI scope bugs.
4. Capability gained: Can detect asymmetric defaults between related commands by reading the signature defaults — no reproduction needed.

## Patterns
- Added: PAT-F-045 (inconsistent defaults between paired CLI commands cause silent round-trip failures)
- Reinforced: none evaluated
