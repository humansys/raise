# E476: Skillset Evolution — Scope

## Objective
Separate language-specific gate configuration from core skills so RaiSE works cleanly across any tech stack.

## In Scope
1. **raise-dev skillset** — Python-specific gate config (test: pytest, lint: ruff, typecheck: pyright)
2. **Language-agnostic skills** — core skills reference gates by role, not tool name
3. **Gate invocation** — skills call configured gate commands before merge/commit
4. **Skillset management** — `rai skill set create/list/diff` support for the new structure

## Out of Scope
- Full CI/CD pipeline generation
- Auto-detection of project language
- Rewriting skills that don't reference gate commands

## Planned Stories
1. Gate configuration schema — define how skillsets declare test/lint/typecheck commands
2. Create `raise-dev` skillset with Python gate configuration
3. Refactor `rai-story-implement` to use gate config instead of hardcoded commands
4. Refactor `rai-bugfix` to use gate config instead of hardcoded commands
5. Refactor `rai-story-close` gate verification to use gate config
6. Example `raise-dev-ts` skillset for TypeScript (optional, SHOULD)
7. Documentation — skillset creation guide

## Done Criteria
- Core skills work without language-specific hardcoding
- `raise-dev` skillset provides Python-specific gates
- A TypeScript project can configure its own skillset and use RaiSE skills
- Existing Python workflow unchanged (backwards compatible)
