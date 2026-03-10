# Bug 464 Plan

Root cause: Skills written before rai backlog CLI existed; never updated.

## Tasks

1. **rai-epic-start**: Remove backlog.md fallback, keep only CLI paths
2. **rai-epic-close**: Replace direct backlog.md edit with `rai backlog transition`
3. **rai-framework-sync**: Replace backlog.md reference with `rai backlog update`
4. Commit all changes together (single skill-fix commit)
