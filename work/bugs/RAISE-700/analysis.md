# Analysis: RAISE-700

## Tier: XS — cause is structurally evident

## Root Cause

scaffold_skills() is a monolithic function that handles three distinct
responsibilities inline:

1. Per-skill dispatch (5 mutually exclusive action branches: CURRENT,
   AUTO_UPDATE, KEEP_USER, CONFLICT, LEGACY) — each with nested conditionals
2. Interactive conflict resolution (4 sub-actions: KEEP, KEEP_ALL,
   OVERWRITE/OVERWRITE_ALL, BACKUP_OVERWRITE) — embedded in the CONFLICT branch
3. Skill-set overlay logic — a separate iteration loop inside the same function

The CONFLICT branch alone contributes ~30 complexity points due to 4 levels of
nesting (force/batch → skip/dry_run → interactive → sub-action).

The function was intentionally deferred with # noqa: C901 pending S370.5; that
story never materialised. This bug closes the deferred work.

## Fix Approach

Extract 6 private helpers, reducing scaffold_skills to a dispatcher:

1. _apply_skill_write() — shared write+copy_tree+manifest_update pattern
2. _handle_new_skill()  — "skill doesn't exist" install path
3. _handle_auto_update() — AUTO_UPDATE action
4. _resolve_conflict_interactive() — interactive prompt branch of CONFLICT
5. _resolve_conflict()  — full CONFLICT handler (wraps batch + interactive)
6. _apply_skill_set_overlay() — skill-set overlay block

batch_keep / batch_overwrite mutable flags stay in scaffold_skills and are
returned from _resolve_conflict() as a (bool, bool) tuple.
