# Retrospective: RAISE-235 — Skill Sync on Upgrade

## Summary
- **Story:** RAISE-235
- **Size:** M (planned), M (actual)
- **Started:** 2026-02-20
- **Completed:** 2026-02-20
- **Commits:** 8 (scope, research+design, plan, 4 impl, progress)
- **Lines:** +2183 / -27 across 16 files
- **Tests added:** 57 (21 manifest + 12 conflict + 24 skill upgrade)
- **Test suite:** 2343 pass, 90.03% coverage

## What Went Well

- **Research-first paid off massively.** The dpkg three-hash algorithm was the clear winner — 50+ sources, zero disagreement. Implementation was straightforward because the model was well-understood before touching code.
- **4 parallel research agents** covered 4 domains in ~4 minutes total wall-clock. Would have taken hours sequentially.
- **TDD velocity** — tests wrote cleanly because the algorithm was pure and well-defined. The detection logic (`classify_skill`) is a pure function with no I/O, making it trivially testable.
- **Tasks 1-3 merged naturally** — models, hash, and detection are one cohesive unit. Plan had them separate for safety but implementation showed they belong together.
- **Zero regressions** — 14 existing tests adapted cleanly. Backward compat preserved on `SkillScaffoldResult`.
- **Clean separation of concerns** — manifest (data), conflict (UX), skills (orchestration) each in their own module.

## What Could Improve

- **Dry-run table prints twice with multi-agent init.** The `init_command` loops over agents and each gets its own `scaffold_skills()` call. The dry-run exit happens after the loop, but the summary function is called once per agent implicitly. Minor cosmetic issue — should print once for the first agent only, or aggregate across agents.
- **Plan had 11 tasks, actual was ~7 logical chunks.** Tasks 1-3 and 8-9 were too granularly split for what turned out to be tightly coupled code. Better to plan cohesive units rather than artificial separations.

## Heutagogical Checkpoint

### What did you learn?
- The dpkg conffile algorithm is genuinely elegant — 3 hashes, 4 states, 25 years of production proof. "Standing on shoulders" delivered.
- The `Traversable` API from importlib.resources works well for reading bundled files but makes hash computation slightly tricky (need to read content, not path).
- Rails Thor's interactive prompt design (default=safe, batch shortcuts) is battle-tested wisdom worth adopting.

### What would you change about the process?
- The research depth was right for this story. Emilio's instinct to do full research on DX-foundational work was correct — it prevented design churn.
- Task granularity in the plan could be coarser for well-understood algorithms. The dpkg model is simple enough that models+hash+detection are one task.

### Are there improvements for the framework?
- **Plan template could note "cohesive unit" as valid task scope** — not everything needs to be split into the smallest possible pieces. The T-shirt sizing should drive granularity, not an arbitrary task count.
- **Research skill works well at standard depth with 4 parallel agents** — this should be the default pattern for M+ stories with design decisions.

### What are you more capable of now?
- Implementing package-manager-style file tracking in Python
- Designing interactive CLI conflict resolution with batch shortcuts
- Applying the dpkg conffile algorithm to non-package-manager contexts

## Action Items
- [ ] Fix dry-run table printing twice for multi-agent (cosmetic, minor)
- [ ] Consider adding `.raise/manifests/` to `.gitignore` template (manifest is machine state, not committed)
