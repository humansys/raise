# E355 Retrospective — Branch Model Evolution

**Epic:** E355 (RAISE-411)
**Date:** 2026-03-03
**Stories:** 2 (S355.1 + S355.2)

## Objective

Simplify branch model from 3 levels (dev → epic → story) to 2 levels (dev → story). Epics become logical containers (directory + tracker), not branches.

## Delivered

- Branch model updated across all live documentation and skill definitions
- methodology.yaml, MEMORY.md, CLAUDE.md, happy-path guides (EN/ES)
- 25+ files updated across builtin, deployment, and legacy skill locations
- All tests passing (3502), no regressions

## Stories

| ID | Summary | Size | Result |
|----|---------|:----:|--------|
| S355.1 | Update branch model — CLAUDE.md, skills, methodology | S | Done |
| S355.2 | Clean up stale epic-branch references across live files | S | Done |

## What Went Well

- **Two-story decomposition was correct** — S355.1 made the structural change, S355.2 cleaned up the blast radius. Natural split.
- **Meta-validation** — both stories used the new model themselves (branched from dev, no epic branch). Dogfooding worked.
- **Test coverage caught a bug** — distributable assets tests enforced `{development_branch}` placeholder, preventing hardcoded `v2` from shipping.

## What To Improve

- **Blast radius grep BEFORE S355.1 commit** — the follow-up story (S355.2) was entirely predictable. Could have been one story with better upfront scanning.
- **3-location copy pattern is expensive** — `.agent/skills/`, `.claude/skills/`, and `src/rai_cli/skills_base/` all need sync. This epic touched the same change in 3 places repeatedly. Consider consolidating or automating sync.
- **Run tests per task, not per phase** — S355.2 discovered a YAML parse error late because tests ran at review, not after each implementation task.

## Patterns Discovered

- **PAT-E-636:** Documentation-only changes have deceptive blast radius — grep BEFORE committing.
- **PAT-E-644:** methodology.yaml branch section must use `{development_branch}` placeholder, not literal branch names. YAML flow items with braces need quoting.

## Process Insight

This epic validated that epics-without-branches works. The epic directory (`work/epics/e355-branch-model-evolution/`) served as the knowledge container, Jira as the tracker, and stories branched directly from dev. No merge conflicts, no branch management overhead. The model is proven.
