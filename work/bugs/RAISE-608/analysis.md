# Analysis: RAISE-608

## 5 Whys

Problem: `rai pattern add` reports success but pattern not found by `rai pattern reinforce`

Why 1: `reinforce` looks in `.raise/rai/memory/patterns.jsonl` (project scope) but pattern was written to `.raise/rai/personal/patterns.jsonl` (personal scope).

Why 2: `pattern add` defaults to `"personal"` scope (pattern.py:176); `pattern reinforce` defaults to `"project"` scope (pattern.py:72). Inconsistent defaults.

Why 3: The default was set to `personal` under the assumption that patterns are developer-specific learnings. But the skill lifecycle (`/rai-bugfix`, `/rai-story-review`) calls `rai pattern add --scope project`, and `reinforce` is called on the same patterns — the intended usage is project scope.

Why 4: No integration test covers the add→reinforce round-trip without explicit --scope flags. The existing test `test_add_pattern_defaults_to_personal_scope` explicitly validates the broken behavior.

Root cause: `pattern add` default scope (`personal`) is inconsistent with `pattern reinforce` default scope (`project`), making the default add→reinforce workflow silently broken.

## Fix Approach

Change `pattern add` default scope from `"personal"` to `"project"`.

Rationale:
- Aligns defaults between `add` and `reinforce`
- Patterns from stories/bugs belong in project scope (committed, shared)
- Personal scope should require explicit intent (`--scope personal`)
- Skills already use `--scope project` explicitly — no skill-level change needed

Tests to update:
- `test_add_pattern_basic`: Creates memory/ dir → unchanged (now writes there by default ✓)
- `test_add_pattern_with_type`: Same ✓
- `test_add_pattern_creates_missing_dir`: Checks personal_dir.exists() → update to check memory_dir
- `test_add_pattern_defaults_to_personal_scope`: Invert assertion — now tests project default
