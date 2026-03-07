---
name: rai-bugfix
overlay: raise-dev-ts
replaces: Step 4 (Fix) verification
description: TypeScript-specific verification commands for bugfix workflow.
---

# Overlay: Fix Verification (TypeScript)

This overlay replaces the generic manifest-lookup priority chain
in Step 4 of the base `rai-bugfix` skill with explicit TypeScript commands.

## Verification Commands

After each RED (regression test) - GREEN (fix) - REFACTOR cycle, run:

```bash
# Tests
npx vitest run

# Lint
npx eslint src/

# Type check
npx tsc --noEmit
```

All three must pass before committing. The bug must no longer reproduce.
