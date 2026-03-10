---
story: S-MULTIDEV
size: M
modules: [mod-session, mod-memory, mod-context]
domain: bc-ontology
layer: lyr-integration
---

# Design: S-MULTIDEV — Multi-Developer Safety

## Problem

Two developers on the same repo will corrupt shared state: session-state overwrites, pattern ID collisions, calibration mixing, and guaranteed merge conflicts on index.json.

## Value

Fer can pull v2 and work safely alongside Emilio without data corruption or merge conflicts.

## Approach

Implement 5 decisions from spike (`work/stories/S-MULTIDEV/recommendations.md`):

1. **Gitignore index.json** — derived artifact, rebuild with `rai memory build`
2. **Move session-state.yaml to personal/** — per-developer by definition
3. **Developer-prefixed pattern IDs** — `PAT-{X}-NNN` from `~/.rai/developer.yaml`
4. **Move calibration.jsonl to personal/** — coaching data is per-developer
5. **Delete empty sessions/index.jsonl** — already in personal/

## Files Affected

| File | Change | Why |
|------|--------|-----|
| `.gitignore` | Add `index.json` entry | D1 |
| `src/rai_cli/session/state.py` | Read/write from `personal/session-state.yaml` | D2 |
| `src/rai_cli/memory/writer.py` | `_get_next_id()` uses `{prefix}-{X}-{num}` format | D3 |
| `src/rai_cli/context/builder.py` | Load calibration from personal/ tier | D4 |
| `src/rai_cli/session/bundle.py` | No change (already reads from personal/) | — |
| `src/rai_cli/config/paths.py` | Add helper for personal session-state path | D2 |
| `.raise/rai/memory/patterns.jsonl` | Migrate PAT-001..259 → PAT-E-001..259 | D3 |

## Examples

### D3: Pattern ID format change

**Before:**
```jsonl
{"id": "PAT-204", "type": "pattern", "content": "Never delete a temp directory..."}
```

**After:**
```jsonl
{"id": "PAT-E-204", "type": "pattern", "content": "Never delete a temp directory..."}
```

**New pattern by Fer:**
```jsonl
{"id": "PAT-F-001", "type": "pattern", "content": "First pattern from Fer..."}
```

### D3: Prefix source

```yaml
# ~/.rai/developer.yaml
name: Emilio
pattern_prefix: E
```

**`_get_next_id()` reads `pattern_prefix` from developer profile, falls back to first letter of name.**

### D2: Session state path change

**Before:** `.raise/rai/session-state.yaml` (tracked)
**After:** `.raise/rai/personal/session-state.yaml` (gitignored)

Migration: on first `load_session_state()`, if old path exists and new doesn't, move it.

## Acceptance Criteria

**MUST:**
- `index.json` is in `.gitignore` and removed from git tracking
- `session-state.yaml` reads/writes from `.raise/rai/personal/`
- Pattern IDs include developer prefix (`PAT-E-NNN`, `PAT-F-NNN`)
- `calibration.jsonl` loads from personal/ scope (already partially there)
- Empty `sessions/index.jsonl` removed from tracking
- All existing tests pass
- New tests cover migration paths and prefix logic

**MUST NOT:**
- Break `rai session start` / `rai session close` flow
- Lose existing patterns during migration
- Require Fer to do anything beyond `rai session start --name "Fer"`
