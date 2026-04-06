# Retrospective: RAISE-605

## Summary
- Root cause: CLI had no --parent flag, adapter resolved parent exclusively from routing config — no metadata["parent_id"] path existed
- Fix approach: Added --parent PAGE_ID to CLI (passes as metadata["parent_id"]), adapter reads it with priority chain: metadata["parent_id"] > routing.parent_title > error
- Classification: Interface/S2-Medium/Code/Missing

## Process Improvement
**Prevention:** When designing adapter methods that accept metadata dicts, document the supported keys and ensure common parameters (parent_id, labels, space) are wired from CLI flags from the start.
**Pattern:** Interface + Code + Missing → CLI-to-adapter parameter gap where the transport (metadata dict) supports the field but neither endpoint wires it.

## Heutagogical Checkpoint
1. Learned: The original bug referenced `mcp_confluence.py` (old MCP adapter) — the adapter was fully rewritten in S1051.2 but the parent_id gap persisted in the new implementation because it was never part of the spec.
2. Process change: When rewriting adapters, audit the bug backlog for unfixed issues that should carry forward to the new implementation.
3. Framework improvement: None — fix is self-contained.
4. Capability gained: Ad-hoc publishing to any location in Confluence without pre-configured routing. Enables programmatic placement by agents/pipelines.

## Patterns
- Added: none (pattern is specific to this adapter)
- Reinforced: none evaluated
