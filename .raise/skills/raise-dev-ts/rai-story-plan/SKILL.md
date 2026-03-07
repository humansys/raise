---
name: rai-story-plan
overlay: raise-dev-ts
replaces: Step 2 task verification template
description: TypeScript-specific verification commands for task decomposition.
---

# Overlay: Task Verification Template (TypeScript)

This overlay replaces the generic "resolve from manifest" guidance
in Step 2 of the base `rai-story-plan` skill with explicit TypeScript commands.

## Per-Task Verification Commands

When defining verification criteria for each task in the plan, use:

```bash
# Tests
npx vitest run

# Lint
npx eslint src/

# Type check
npx tsc --noEmit
```

Include these in every task's verification section. All three must pass before the task is considered complete.
