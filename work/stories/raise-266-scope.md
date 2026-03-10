# RAISE-266: Contract Chain Lean

> **Status:** In Progress
> **Branch:** `story/standalone/raise-266-contract-chain-lean`
> **Epic:** RAISE-144 (Engineering Health)
> **Size:** M
> **Origin:** RAISE-249 (Artifact Ontology) — chain designed but lost in E250 skill compression

---

## In Scope

Restore the Contract Chain in the current ADR-040 compliant skills (≤150 lines).
Each skill produces a typed artifact that the next skill consumes as structured input.

### Artifacts to restore

| Artifact | Skill | Format | Consumed by |
|----------|-------|--------|-------------|
| `brief.md` | `rai-epic-start` | SAFe hypothesis + boundaries | `rai-epic-design` |
| `story.md` | `rai-story-start` | Connextra + Gherkin AC + SbE | `rai-story-design` |
| AC refs in tasks | `rai-story-plan` | RED tests reference story.md scenarios | `rai-story-implement` |
| scope/design split | `rai-epic-design` | Separate WHAT (scope.md) from HOW (design.md) | `rai-story-design` |

### Constraints

- Skills MUST stay ≤150 lines (ADR-040)
- Templates live in `skills/{name}/templates/` — reference, don't inline
- Lean formats: minimal YAML frontmatter, no ceremony for ceremony's sake
- Depth adapts to size: XS/S = light, M/L = full

## Out of Scope

- New skills or CLI code changes
- Skill runtime changes
- Validation of the chain end-to-end (separate story)
- SDLD blueprint format in story-plan (keep current task format, add AC refs only)

## Done Criteria

- [ ] `rai-epic-start` produces `brief.md` with template
- [ ] `rai-epic-design` references `brief.md` as input, produces separate `design.md`
- [ ] `rai-story-start` produces `story.md` with template
- [ ] `rai-story-design` references `story.md` AC as input
- [ ] `rai-story-plan` tasks reference story.md AC scenarios
- [ ] All modified skills ≤150 lines
- [ ] Templates exist in each skill's `templates/` directory

---

*Created: 2026-02-24*
