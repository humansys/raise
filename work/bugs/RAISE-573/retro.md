# Retrospective: RAISE-573

## Summary
- Root cause: `_infer_depends_on` only processed `type="module"` nodes, skipping components that also carry `depends_on` metadata — 161 dependency entries silently dropped
- Fix approach: Extend type filter to `("module", "component")`, add name→id index for component class name resolution with module fallback
- Classification: Functional/S2-Medium/Code/Missing

## Process Improvement
**Prevention:** When adding metadata fields to new node types (e.g., `depends_on` on components), audit all edge inference functions that consume that metadata. A simple grep for the field name in `extractors/` would catch this.
**Pattern:** Functional + Code + Missing → new node type carries metadata but existing consumers filter by old type only.

## Heutagogical Checkpoint
1. Learned: Component IDs use `comp-{module}-{ClassName}` while `depends_on` entries are bare class names. Resolution requires a name→id index — can't just prefix like modules do.
2. Process change: When discovery/scanner adds metadata to components, add a test that verifies the metadata flows to edges.
3. Framework improvement: The `comp_name_index` pattern (name→id lookup) could be reused by other inferrers if components get more relationship types.
4. Capability gained: Understanding of the full edge inference pipeline and how node types interact across loaders.

## Patterns
- Added: PAT-E-729 (audit edge inferrers when adding metadata to new node types)
- Reinforced: none evaluated
