---
name: rai-story-implement
overlay: raise-dev
replaces: Step 3 (Verify Task)
description: Python-specific verification commands for story implementation.
---

# Overlay: Verify Task (Python)

This overlay replaces the generic manifest-lookup + language-detection table
in Step 3 of the base `rai-story-implement` skill with explicit Python commands.

## Verification Commands

After each RED-GREEN-REFACTOR cycle, run:

```bash
# Tests
uv run pytest --tb=short -x

# Lint
uv run ruff check

# Type check
uv run pyright
```

All three must pass before committing. If any fails: fix and re-verify (max 3 attempts before escalating).
