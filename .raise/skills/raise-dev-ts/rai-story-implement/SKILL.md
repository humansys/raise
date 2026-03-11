---
name: rai-story-implement
overlay: raise-dev-ts
replaces: Step 3 (Verify Task)
description: TypeScript-specific verification commands for story implementation.
---

# Overlay: Verify Task (TypeScript)

This overlay replaces the generic manifest-lookup + language-detection table
in Step 3 of the base `rai-story-implement` skill with explicit TypeScript commands.

## Verification Commands

After each RED-GREEN-REFACTOR cycle, run:

```bash
# Tests
npx vitest run

# Lint
npx eslint src/

# Type check
npx tsc --noEmit
```

All three must pass before committing. If any fails: fix and re-verify (max 3 attempts before escalating).
