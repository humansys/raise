---
name: rai-story-plan
overlay: raise-dev
replaces: Step 2 task verification template
description: Python-specific verification commands for task decomposition.
---

# Overlay: Task Verification Template (Python)

This overlay replaces the generic "resolve from manifest" guidance
in Step 2 of the base `rai-story-plan` skill with explicit Python commands.

## Per-Task Verification Commands

When defining verification criteria for each task in the plan, use:

```bash
# Tests
uv run pytest --tb=short -x

# Lint
uv run ruff check

# Type check
uv run pyright
```

Include these in every task's verification section. All three must pass before the task is considered complete.
