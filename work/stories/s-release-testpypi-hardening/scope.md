# Story Scope: S-RELEASE — Pre-Release Hardening

**Type:** Standalone pre-release story (branchless epic pattern)
**Branch:** `story/s-release/testpypi-hardening` off `v2`

## In Scope

- Add `**/vendor/**` to scanner default excludes (PAT-247)
- Absorb `/discover-complete` into `/discover-validate` — one less step for new users
- Rename `discover-describe` → `discover-document` — name for what it produces

## Delivered

- [x] `**/vendor/**` added to DEFAULT_EXCLUDE_PATTERNS + CLI defaults
- [x] `discover-complete` absorbed into `discover-validate` (Step 6: Export)
- [x] `discover-complete` skill deleted from both `.claude/skills/` and `skills_base/`
- [x] `discover-describe` renamed to `discover-document` in both locations
- [x] All cross-references updated (methodology.yaml, migration.py, CLI hints, skill-create, models.py)
- [x] Tests updated and passing (1696 passed)
- [x] Ruff + pyright clean on modified files

## Deferred to Pre-Release Stories

- **S-RENAME:** Command entry point `raise` → `rai`, package `raise-cli` → `rai-cli`
- **S-NAMESPACE:** Skill namespace prefix (research needed)
- **Publish to PyPI** — blocked on S-RENAME

## Out of Scope

- Drift detector calibration (post-F&F)
- Cloud/commercial features
