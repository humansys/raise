# Epic Retrospective: RAISE-249 Artifact Ontology & Contract Chain

**Completed:** 2026-02-22
**Duration:** 2 days (started 2026-02-21)
**Stories:** 5 delivered, 1 cancelled (S6 — superseded by RAISE-211 as real-world validation)
**Commits:** 29

---

## Summary

Formalized input/output contracts between all lifecycle skills using industry-standard
formats (SAFe hypothesis, Connextra+Gherkin, SDLD blueprints). Five skills updated
with typed artifacts: epic-start (Epic Brief), epic-design (scope/design split),
story-start (User Story), story-design (Gemba Walk + interfaces), story-plan (SDLD
blueprints). The contract chain enables mechanical implementation with zero design
decisions during story-implement.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 5 of 6 | S6 cancelled — RAISE-211 serves as validation |
| Tests Added | 0 | Pure skill content (markdown), no code changes |
| Average Velocity | 3.55x | Across 5 stories |
| Calendar Days | 2 | Started 2026-02-21, completed 2026-02-22 |
| Total Effort | ~87 min | Sum of actual times |

### Story Breakdown

| Story | Size | Actual | Velocity | Key Learning |
|-------|:----:|:------:|:--------:|--------------|
| S1: story-design v1.2 | M | 30 min | 3.0x | Gemba Walk is the grounding mechanism — reading code before designing |
| S2: story-plan v1.1 | M | 20 min | 4.5x | SDLD blueprints with signatures make implementation mechanical |
| S5: story-start v1.1 | S | 15 min | 3.0x | Connextra + Gherkin gives story-design structured input to work from |
| S3: epic-start v1.1 | S | 12 min | 3.75x | SAFe hypothesis format + Shape Up no-gos/rabbit holes |
| S4: epic-design v1.2 | S | 10 min | 4.5x | Scope/design split — WHAT vs HOW as separate artifacts |

**Velocity trend:** Accelerating — each story was faster than the last (3.0x → 4.5x).
Format conventions established in early stories were reused in later ones.

---

## What Went Well

- **Contract chain concept validated:** Each skill's output directly feeds the next skill's input with zero ambiguity
- **Industry standards as foundation:** SAFe, Connextra, Gherkin, SDLD are well-documented — no need to invent formats
- **Accelerating velocity:** Shared conventions across skills meant later stories were faster
- **No code changes:** Pure skill content (markdown) — zero regression risk
- **Sequential execution was correct:** Each story informed the next; parallelism would have lost this compounding learning

## What Could Be Improved

- **S6 (Validation) should have been integrated, not separate:** A validation story that depends on all others is brittle scheduling-wise. Better to validate organically by using the skills on the next real epic.
- **Depth heuristics need real-world calibration:** Gemba Walk depth by story size (XS=skip, S=skim, M+=full) is documented but untested on actual implementation stories.
- **epic-plan was explicitly excluded:** The rationale was "scheduling, not design" — but the epic-plan skill also needs a plan.md artifact. Worth revisiting.

## Patterns Discovered

| Pattern | Context |
|---------|---------|
| Contract chain between skills eliminates design decisions during implementation | When skills produce typed artifacts that the next skill consumes as structured input |
| Scope/design split (WHAT vs HOW) prevents artifact bloat | When a single document tries to serve both stakeholders and implementers |
| Accelerating velocity in format-consistent work | When shared conventions compound across sequential stories |
| Real-world usage > synthetic validation | When a dedicated "validation story" can be replaced by using the system on the next real task |

## Process Insights

- **Skill content changes are the fastest story type** — no tests, no code, pure domain knowledge. 3-4.5x velocity is sustainable.
- **The Gemba principle applies to skills too** — reading the actual SKILL.md before modifying it (not relying on memory) prevented drift.
- **Contract formalization has compound returns** — the value isn't in any single artifact format, but in the chain. Each artifact is more valuable because the next skill knows exactly what to expect.

---

## Artifacts

- **Scope:** `work/epics/raise-249-artifact-ontology/scope.md`
- **Design:** `work/epics/raise-249-artifact-ontology/design.md`
- **Stories:** `work/epics/raise-249-artifact-ontology/stories/s249.{1-5}/`
- **Skills updated:**
  - `.claude/skills/rai-story-design/SKILL.md` — v1.2.0 (Gemba Walk + Target Interfaces)
  - `.claude/skills/rai-story-plan/SKILL.md` — v1.1.0 (SDLD Task Blueprints)
  - `.claude/skills/rai-story-start/SKILL.md` — v1.1.0 (User Story artifact)
  - `.claude/skills/rai-epic-start/SKILL.md` — v1.1.0 (Epic Brief artifact)
  - `.claude/skills/rai-epic-design/SKILL.md` — v1.2.0 (scope.md + design.md split)

---

## Next Steps

- **RAISE-211 (Adapter Foundation)** — first real epic using the updated contract chain. Serves as organic validation of all 5 updated skills.
- **Monitor:** Depth heuristics during RAISE-211 stories — are Gemba Walk and SDLD blueprints calibrated correctly for code-change stories (vs skill-content stories)?

---

*Epic retrospective — captures learning for continuous improvement*
*Closed: 2026-02-22 (SES-242)*
