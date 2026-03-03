# E346: Skill Lifecycle Hardening — Scope

## Objective

Reinforce orchestrator skills, rename and genericize review skills so the full skill lifecycle is reliable and language-agnostic.

## In Scope

- Audit `/rai-epic-run` for skipped steps and missing gates
- Rename quality-review → code-review, arch-review → architecture-review
- Remove Python-specific bias from review skill prompts
- Insert review skills into story-run and epic-run orchestrator flows

## Out of Scope

- New skill creation
- Skill architecture changes (ADR-040 is stable)
- CLI command changes (skill names are internal)
- Skill set ecosystem changes (E340 complete)

## Planned Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S346.1 | Audit epic-run orchestrator | S | Identify skipped steps, add missing gates |
| S346.2 | Rename review skills | S | quality-review → code-review, arch-review → architecture-review |
| S346.3 | Language-agnostic reviews | M | Remove Python bias from review prompts |
| S346.4 | Integrate reviews into orchestrators | S | Insert review skills at correct points in flows |

## Done Criteria

- All 4 stories merged to epic branch
- Orchestrators execute full lifecycle without gaps
- Review skills work on Python, JS/TS, and .NET codebases
- All references updated (CLAUDE.md, skill manifests, etc.)
