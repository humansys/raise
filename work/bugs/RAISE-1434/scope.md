# RAISE-1434: Epic/story close skips CLAUDE.local.md update

## WHAT
After epic/story close, CLAUDE.local.md shows stale state (e.g., completed epic still listed as "next focus"). Next session starts with wrong context.

## WHERE
- `.agent/skills/rai-story-close/SKILL.md:137` — instructs update of CLAUDE.local.md
- `.agent/skills/rai-epic-close/SKILL.md:115` — instructs update of CLAUDE.local.md
- `.agent/skills/rai-welcome/SKILL.md:90,116` — scaffolds CLAUDE.local.md

## WHEN
Every epic/story close. Subagents deprioritize secondary artifacts when context saturates.

## Reproduces
Yes — CLAUDE.local.md does not exist in repo (already drifted and lost).

## Impact
Next session starts with stale context. Mitigated by GH-15 (GitStateDeriver, ADR-038) — session bundle derives from git.

TRIAGE: Functional / S3-Low / Design / Missing
