# Epic RAISE-249: Artifact Ontology & Contract Chain — Scope

> **Status:** IN PROGRESS
> **Branch:** `epic/raise-249/artifact-ontology`
> **Created:** 2026-02-21
> **Jira:** RAISE-249

---

## Hypothesis

If we formalize the input/output contracts between lifecycle skills using
industry-standard formats (SAFe hypothesis, Connextra+Gherkin, SDLD blueprints),
then implementation becomes mechanical execution with zero design decisions,
as measured by architectural questions raised during story-implement.

## Objective

Maximize implementation pipeline reliability by establishing a formal artifact
ontology and contract chain across the epic/story lifecycle skills.

**Value proposition:** Every skill produces a typed artifact that the next skill
consumes as structured input. No skill needs to infer what the previous one meant.

---

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S1 | story-design v1.2 | M | Pending | Gemba Walk + Integration Design at function level |
| S2 | story-plan v1.1 | M | Pending | SDLD Task Blueprints with signatures, tests, file paths |
| S3 | epic-start v1.1 | S | Pending | Epic Brief artifact (SAFe hypothesis + Shape Up) |
| S4 | epic-design v1.2 | S | Pending | Separate scope.md / design.md artifacts |
| S5 | story-start v1.1 | S | Pending | User Story template (Connextra + Gherkin + SbE) |
| S6 | Validation | S | Pending | Run a real story through the new pipeline end-to-end |

**Total:** 6 stories, 2M + 4S

---

## In Scope

**MUST:**
- story-design adds Gemba Walk + function-level Integration Design
- story-plan produces SDLD task blueprints (file paths, signatures, test specs)
- epic-start produces Epic Brief in SAFe+Shape Up format
- epic-design separates scope.md (what/why) from design.md (how/interfaces)
- story-start produces/validates User Story in Connextra+Gherkin format
- Each skill's output format is documented as the next skill's input contract

**SHOULD:**
- Validation story uses RAISE-247 S1 as the real-world test case
- Templates updated in `.raise/templates/` for new artifact formats

## No-Gos (explicit exclusions)

- DO NOT change epic-plan (scheduling, not design — orthogonal to grounding cascade)
- DO NOT change story-implement beyond consuming the new plan format
- DO NOT change story-review or story-close
- DO NOT touch the katas (`.raise/katas/`) — skills are the active artifacts
- DO NOT change CLI code — this is pure skill content (markdown)

## Rabbit Holes

- Over-specifying the Epic Brief format with all SAFe Lean Business Case fields (keep it lean)
- Trying to make Gherkin acceptance criteria executable (we're not building a test runner)
- Templating engine or code generation from artifacts (future scope)

---

## Done Criteria

### Per Story
- [ ] Skill SKILL.md updated with new steps/format
- [ ] Version bumped in metadata
- [ ] Changelog entry added

### Epic Complete
- [ ] All 6 stories complete
- [ ] Contract chain documented: each skill's output → next skill's input
- [ ] One real story successfully run through full pipeline (S6)
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Dependencies

```
S1 (story-design) ──┐
                     ├── S6 (validation) — needs all skills updated
S2 (story-plan) ────┘

S3 (epic-start) ────┐
                     ├── S6 (validation)
S4 (epic-design) ───┘

S5 (story-start) ───── S6 (validation)
```

S1 and S2 are independent but highest priority (immediate use in RAISE-247).
S3, S4, S5 are independent of each other.
S6 depends on all others.

---

## Notes

### Why This Epic

The design cascade (epic-design → story-design → story-plan → implement) has a
grounding gap in the middle. Epic-design v1.1 added Gemba Walk and Integration
Design at component level, but story-design still says "trust AI for HOW" and
story-plan produces generic tasks. The implementer AI still makes architectural
decisions that should have been made in design/planning.

### Research Foundation

Three parallel research threads informed this design:
- **Epic Briefs:** SAFe Hypothesis + Shape Up (Appetite, No-Gos, Rabbit Holes)
- **User Stories:** Connextra + Gherkin + Specification by Example
- **Plans:** SDLD Task Blueprints (file paths, signatures, paired test tasks)

### Execution Strategy

S1+S2 first — they address the immediate pain (story-plan producing insufficient
detail for mechanical implementation). These will be used immediately in RAISE-247
stories. S3-S5 complete the upstream chain.

---

*Created: 2026-02-21*
