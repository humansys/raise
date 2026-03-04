# Epic Brief: Skill Set Ecosystem

| Field | Value |
|-------|-------|
| ID | RAISE-340 |
| Type | Feature |
| Priority | P1 (v2.2) |
| Requester | Emilio |

## Problem

Users and teams cannot customize RaiSE skill sets without risking loss
of changes on framework upgrades. No mechanism exists for teams to
maintain their own skill variants alongside builtins, or to select
which skill set to deploy.

## Strategic Objective

Enable team-level skill customization with safe upgrade paths, making
RaiSE's open core adoptable by teams with diverse workflows.

## Research

Formal research completed: `work/research/skill-set-patterns/`
- 14 projects analyzed (7 OSS tools + 7 AI coding tools)
- 5 convergent patterns identified
- Named skill sets identified as market differentiator

## Constraints

- KISS / DRY / YAGNI — no registry, no inheritance, no partial override
- Must work with existing three-hash manifest mechanism
- Open core scope — Pro/Enterprise features deferred
