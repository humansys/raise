# Retrospective: RAISE-1278

## Summary
- Root cause: `write_record()` and `read_record()` used work_id without case normalization, creating duplicate directories on case-sensitive filesystems
- Fix approach: Pydantic `field_validator` on `work_id` to uppercase + `read_record()` normalization + migration of 7 existing dirs
- Classification: Data/S2-Medium/Code/Missing

## Process Improvement
**Prevention:** All identifier fields used in filesystem paths should normalize casing at the model boundary (Pydantic validator), not at call sites. This is a general pattern for any ID→path mapping.
**Pattern:** Data + Code + Missing → missing normalization at model boundary when identifier is used in filesystem paths.

## Heutagogical Checkpoint
1. Learned: Case-insensitive regex (`re.IGNORECASE`) in `derive.py` extracts work_id preserving original case — normalization must happen downstream at the model, not at extraction.
2. Process change: When adding fields that become path components, add normalization validator from day one.
3. Framework improvement: The `rai learn write` CLI command benefits automatically because it constructs `LearningRecord` — no CLI changes needed. Good separation of concerns.
4. Capability gained: Understanding of the full LEARN record I/O path from branch regex → model → disk.

## Patterns
- Added: none (fix is self-documenting via validator)
- Reinforced: none evaluated (no patterns were primed for this XS bug)
