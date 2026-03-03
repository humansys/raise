# E346: Skill Lifecycle Hardening — Scope

## Objective

Reinforce orchestrator skills, genericize review skills for language-agnosticism, and promote deployment-only review skills to builtin for proper distribution.

## In Scope

- Audit `/rai-epic-run` and `/rai-story-run` for skipped steps and missing gates
- Remove Python-specific bias from `/rai-quality-review` prompts
- Remove Python-specific bias from `/rai-story-review` prompts
- Promote `/rai-architecture-review` and `/rai-quality-review` from deployment-only to builtin

## Out of Scope

- Renaming skills (names are already correct: quality-review, architecture-review)
- New skill creation
- Skill architecture changes (ADR-040 is stable)
- CLI command changes (skill names are internal)
- Skill set ecosystem changes (E340 complete)
- Orchestrator rewrites (patch, don't rewrite)

## Planned Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S346.1 | Audit orchestrators | S | Audit epic-run + story-run, identify gaps in gates/phases |
| S346.2 | Language-agnostic quality-review | M | Remove Python bias from QR (*.py filter, pytest, type:ignore, except) |
| S346.3 | Language-agnostic story-review | S | Remove hardcoded `uv run pytest`, Python-specific verification |
| S346.4 | Promote AR+QR to builtin | S | Move from .claude/skills/ to src/rai_cli/skills_base/ + sync |

## Dependencies

- S346.2 and S346.3 can run in parallel (independent skills)
- S346.4 depends on S346.2 (QR content must be final before promoting)
- S346.1 is independent (audit only, no code changes expected)

## Done Criteria

- All 4 stories merged to epic branch
- Orchestrators execute full lifecycle without gaps (verified by S346.1 audit)
- Quality-review works on Python, JS/TS, and .NET codebases
- Story-review test verification is language-agnostic
- AR and QR exist in builtin with identical deployment copies
- All references updated (CLAUDE.md, skill manifests, etc.)
