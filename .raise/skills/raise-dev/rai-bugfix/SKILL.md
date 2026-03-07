---
name: rai-bugfix
overlay: raise-dev
replaces: Step 4 (Fix) verification
description: Python-specific verification commands for bugfix workflow.
---

# Overlay: Fix Verification (Python)

This overlay replaces the generic manifest-lookup priority chain
in Step 4 of the base `rai-bugfix` skill with explicit Python commands.

## Verification Commands

After each RED (regression test) - GREEN (fix) - REFACTOR cycle, run:

```bash
# Tests
uv run pytest --tb=short -x

# Lint
uv run ruff check

# Type check
uv run pyright
```

All three must pass before committing. The bug must no longer reproduce.
