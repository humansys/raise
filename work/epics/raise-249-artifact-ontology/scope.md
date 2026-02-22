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
| S1 | story-design v1.2 | M | ✅ Done | Gemba Walk + Integration Design at function level |
| S2 | story-plan v1.1 | M | ✅ Done | SDLD Task Blueprints with signatures, tests, file paths |
| S3 | epic-start v1.1 | S | ✅ Done | Epic Brief artifact (SAFe hypothesis + Shape Up) |
| S4 | epic-design v1.2 | S | ✅ Done | Separate scope.md / design.md artifacts |
| S5 | story-start v1.1 | S | ✅ Done | User Story template (Connextra + Gherkin + SbE) |
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

## Architecture References

| Document | Key Insight |
|----------|-------------|
| `design.md` (this epic) | Contract chain: 6 artifact formats, grounding cascade from hypothesis to code signatures |

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

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-21

### Feature Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S1: story-design v1.2 | M | None | M1 | Upstream of S2; produces input story-plan will consume. Highest immediate impact. |
| 2 | S2: story-plan v1.1 | M | Soft on S1 | M1 | Consumes story-design output. Together with S1 = usable pipeline for RAISE-247. |
| 3 | S5: story-start v1.1 | S | None | M2 | User Story artifact feeds story-design. Logically upstream of S1 but lower priority. |
| 4 | S3: epic-start v1.1 | S | None | M2 | Epic Brief artifact. Independent of story chain. |
| 5 | S4: epic-design v1.2 | S | S3 (soft) | M2 | Scope/design split. Benefits from S3's brief format being defined. |
| 6 | S6: Validation | S | S1-S5 | M3 | End-to-end proof with real RAISE-247 story. |

**Sequential execution** — single developer, all skills share format conventions that benefit from sequential learning. Each story informs the next.

### Milestones

| Milestone | Stories | Success Criteria | Demo |
|-----------|---------|------------------|------|
| **M1: Grounded Pipeline** | S1 + S2 | story-design produces Gemba + interfaces; story-plan produces SDLD blueprints | Run RAISE-247 S1 through story-design → story-plan and inspect output quality |
| **M2: Full Chain** | + S3 + S4 + S5 | All 5 skills updated; every skill produces typed artifact; every input contract documented | Walk through artifact chain from epic brief → plan showing progressive grounding |
| **M3: Validated** | + S6 | Real story executed through full pipeline; implementation was mechanical | Zero architectural questions during story-implement of validation story |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sequential: S1 ─► S2 ─► S5 ─► S3 ─► S4 ─► S6
            ╰─ M1 ──╯   ╰──── M2 ────╯    ╰M3╯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

No parallel streams — single developer + shared format conventions across skills make sequential learning more valuable than parallelism. Each story refines understanding of the contract chain that the next story uses.

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S1: story-design v1.2 | M | ✅ Done | 30 min | 3.0x velocity |
| S2: story-plan v1.1 | M | ✅ Done | 20 min | 4.5x velocity |
| S5: story-start v1.1 | S | ✅ Done | 15 min | 3.0x velocity |
| S3: epic-start v1.1 | S | ✅ Done | 12 min | 3.75x velocity |
| S4: epic-design v1.2 | S | ✅ Done | 10 min | 4.5x velocity |
| S6: Validation | S | Pending | — | |

**Milestone Progress:**
- [x] M1: Grounded Pipeline (S1 + S2) ✅
- [x] M2: Full Chain (+ S3 + S4 + S5) ✅
- [ ] M3: Validated (+ S6)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| S1 Gemba step makes story-design too long | Medium | Medium | Depth heuristic by story size (XS=skip, S=skim, M+=full) |
| SDLD blueprint format is too rigid for novel work | Medium | Medium | Adapt detail level to story size; XS/S get lighter blueprints |
| S6 validation reveals contract gap between skills | Low | High | Each story includes self-test: write a mini-example artifact and verify next skill could consume it |

### Velocity Assumptions

- **Baseline:** These are skill content changes (markdown), not code. Faster than typical stories.
- **Estimated per story:** S = 30-60 min, M = 1-2 hours
- **Total estimated:** ~5-7 hours across 6 stories
- **Buffer:** 30% for iteration after S6 reveals improvements

---

*Plan created: 2026-02-21*
*Next: S1 — `/rai-story-design` for story-design v1.2*

---

*Created: 2026-02-21*
