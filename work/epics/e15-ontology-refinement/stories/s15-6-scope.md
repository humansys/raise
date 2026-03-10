# Feature Scope: S15.6 Skills Integration

## Summary

Create a reusable "Load Architectural Context" step for design skills. Update `/story-design`, `/epic-design`, and `/story-plan` to query the ontology graph before designing.

## In Scope

- Reusable architectural context step pattern for skills
- Update `/story-design` SKILL.md with architectural context step
- Update `/epic-design` SKILL.md with architectural context step
- Update `/story-plan` SKILL.md with architectural context step
- Skills present "Architectural Context" section showing: bounded context, layer, constraints, dependencies, guardrails

## Out of Scope

- Automated validation of designs against constraints (future epic)
- Changes to other skills beyond the 3 design skills
- New CLI commands (S15.5 already provides `rai memory context`)
- Conflict detection or violation warnings

## Done Criteria

- [ ] `/story-design` queries `rai memory context <module>` before designing
- [ ] `/epic-design` queries architectural context for relevant modules
- [ ] `/story-plan` references architectural context in task decomposition
- [ ] Skills output "Architectural Context" section in their artifacts
- [ ] Dogfood: verify the context step works with a real module query
- [ ] Tests pass (>90% coverage)
- [ ] Retrospective complete
