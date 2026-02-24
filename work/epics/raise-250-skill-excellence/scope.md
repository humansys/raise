# Epic E250: Skill Excellence — Scope

> **Status:** IN PROGRESS
> Branch: `epic/e250/skill-excellence`
> Created: 2026-02-23
> Base: `v2`

---

## Objective

Redesign the 23 built-in RaiSE skills with a conscious, evidence-based structural pattern
that maximizes agent reliability. These skills are the open-core reference implementation —
they should represent our best work.

**Value proposition:** Skills that agents follow reliably, with minimal token waste,
consistent structure, and zero stale references. Every line earns its place.

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Skill Contract | ADR-040 | 7-section canonical structure, ≤150 lines, ≤15 rules, ≥80% substance |
| Research | RES-SKILL-CONTRACT-001 | 23 sources: compliance ≈ p(each)^n; U-shaped attention; examples > rules |
| Hooks & Gates | ADR-039 | Cross-cutting content moves to hooks, not duplicated in skills |

---

## Stories

| ID | Story | Size | Dependencies | Description |
|----|-------|:----:|:------------:|-------------|
| S250.1 | Contract infrastructure + pilot | M | — | Extract shared base, create contract template, pilot-refactor 3 diverse skills |
| S250.2 | Refactor lifecycle skills | M | S250.1 | Apply contract to 12 skills: session(2) + epic(4) + story(6) |
| S250.3 | Refactor utility skills | S | S250.1 | Apply contract to 11 skills: discovery(4) + meta(7) |
| S250.4 | Compliance validation + sync | XS | S250.2, S250.3 | Final audit, `rai skill validate` contract checks, skills_base→.claude sync |

**Total:** 4 stories, ~23 skills refactored

### Story Details

**S250.1: Contract infrastructure + pilot (M)**
- Extract shared preamble from cross-cutting content (ShuHaRi rules, gate declarations)
- Create contract template reflecting ADR-040's 7-section structure
- Pilot refactor 3 diverse skills: `rai-session-start` (148 lines, smallest), `rai-story-implement` (236 lines, most-used), `rai-epic-design` (627 lines, largest lifecycle)
- Validate: pilot skills ≤150 lines, ≥80% substance, 7 sections
- Establish the pattern that S250.2 and S250.3 follow mechanically

**S250.2: Refactor lifecycle skills (M)**
- Apply contract to 12 skills in the core lifecycle path:
  - Session: `session-start` (done in pilot), `session-close`
  - Epic: `epic-start`, `epic-design` (done in pilot), `epic-plan`, `epic-close`
  - Story: `story-start`, `story-design`, `story-plan`, `story-implement` (done in pilot), `story-review`, `story-close`
- Fix terminology: "feature" → "story" consistently
- Fix stale refs (file paths, command names, memory model)
- 9 net-new refactors (3 done in pilot)

**S250.3: Refactor utility skills (S)**
- Apply contract to 11 remaining skills:
  - Discovery: `discover-start`, `discover-scan`, `discover-validate`, `discover-document`
  - Meta: `research`, `debug`, `docs-update`, `problem-shape`, `welcome`, `project-create`, `project-onboard`
- These are less interconnected → mechanical application of the pattern
- Expected high velocity per PAT-E-442 (3rd batch is mechanical)

**S250.4: Compliance validation + sync (XS)**
- Audit all 23 skills against ADR-040 targets (lines, substance ratio, section count)
- Update `rai skill validate` to check contract compliance (7 sections present, line count)
- Sync `skills_base/` → `.claude/skills/` for this project
- Final stale-ref grep across all skills

---

## In Scope

**MUST:**
- All 23 skills follow ADR-040 canonical structure (7 sections, fixed order)
- All skills ≤150 lines (was avg 337)
- All skills ≥80% substance ratio (was 35-75%)
- ≤15 discrete rules per skill
- Zero stale references (files, commands, terminology)
- Consistent terminology across all skills
- Shared base extracted for cross-cutting content
- 1-2 examples per skill where applicable

**SHOULD:**
- Affirmative phrasing throughout (audit and fix negative phrasing)
- Decision tables replacing prose conditionals
- `rai skill validate` checks contract compliance

---

## Out of Scope (defer)

- Skill Builder (RAISE-242/S2) — separate epic, builds on this foundation
- Semantic Validator CLI code (RAISE-242/S1) — reassess after this epic
- New skills — this epic improves existing, doesn't create new
- Skill runtime/execution engine — skills remain markdown instructions
- XML tag adoption in skills — research supports it but markdown-only is sufficient for now
- Shared base as CLI mechanism — manual extraction first, `rai skill base` command later

---

## Done Criteria

### Per Story
- [ ] All target skills ≤150 lines
- [ ] All target skills have exactly 7 sections in canonical order
- [ ] Zero stale references in target skills
- [ ] Substance ratio ≥80% for target skills
- [ ] Tests pass, type checks pass, lint passes

### Epic Complete
- [ ] All 23 skills follow ADR-040 contract
- [ ] Total skill lines reduced from 7,753 to ≤3,450 (23 × 150)
- [ ] Shared base extracted and functional
- [ ] `rai skill validate` checks contract compliance
- [ ] skills_base/ synced to .claude/skills/
- [ ] Epic retrospective done
- [ ] Merged to `v2`

---

## Dependencies

```
S250.1 (contract infra + pilot)
  ├──→ S250.2 (lifecycle skills)
  └──→ S250.3 (utility skills)    ← parallel with S250.2
         │              │
         └──────┬───────┘
                ↓
         S250.4 (validation + sync)
```

**External:** ADR-040 (accepted), ADR-039 (hooks/gates inform shared base extraction)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Over-compression loses critical nuance | Medium | Medium | Pilot in S250.1 validates before batch |
| 150-line target too aggressive for complex skills | Low | Low | Allow ≤200 for top-3 complex skills with justification |
| Shared base mechanism unclear | Medium | Low | Start with simple file include, formalize later |

---

## Velocity Assumptions

- S250.1: Normal velocity (establishing pattern)
- S250.2: 1.5-2x velocity (pattern established, PAT-E-442 2nd batch)
- S250.3: 2-3x velocity (mechanical, PAT-E-442 3rd batch)
- S250.4: Normal velocity (validation, different task type)

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-23

### Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:------------:|:---------:|-----------|
| 1 | S250.1: Contract infra + pilot | M | — | M1 | Establishes pattern; validates 150-line target on 3 diverse skills |
| 2 | S250.2: Lifecycle skills | M | S250.1 | M2 | Core path — session+epic+story. Highest impact on daily usage |
| 2 | S250.3: Utility skills | S | S250.1 | M2 | Parallel with S250.2. Mechanical (PAT-E-442 3rd batch) |
| 3 | S250.4: Compliance validation | XS | S250.2, S250.3 | M3 | Final audit + `rai skill validate` contract checks |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Pattern Proven** | S250.1 | 3 pilot skills ≤150 lines, 7 sections, ≥80% substance. Shared base extracted. Contract template works. |
| **M2: All Skills Refactored** | S250.2, S250.3 | All 23 skills follow ADR-040 contract. Zero stale refs. Terminology unified. |
| **M3: Epic Complete** | S250.4 | `rai skill validate` checks contract. skills_base→.claude synced. Retrospective done. Merged to v2. |

### Parallel Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: S250.1 ─────► S250.2 (12 lifecycle) ──► S250.4
                   ↓                                 ↑
Stream 2:        split ► S250.3 (11 utility) ───────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          M1              M2                    M3
```

S250.2 and S250.3 can run in parallel after S250.1 (different skill sets, no overlap).
In practice, likely sequential within a single session — but designed for parallelism.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S250.1 | M | ✅ Done | — | — | 148→96, 176→115, 236→91. Preamble + template created. |
| S250.2 | M | Pending | — | — | |
| S250.3 | S | Pending | — | — | |
| S250.4 | XS | Pending | — | — | |

**Milestone Progress:**
- [x] M1: Pattern Proven
- [ ] M2: All Skills Refactored
- [ ] M3: Epic Complete

### Sequencing Rationale

**S250.1 first (risk-first + walking skeleton):**
- Highest uncertainty: will the 150-line target work? Does the shared base concept hold?
- Pilot on 3 diverse skills (smallest/most-used/largest) validates the range
- Failure here = adjust contract before batch work. Success = mechanical application

**S250.2 and S250.3 parallel (independence + compounding):**
- No file overlap between lifecycle and utility skills
- S250.2 touches the daily-use skills (higher impact, slightly more care)
- S250.3 is the most mechanical batch (PAT-E-442: 3rd extraction = 2-3x velocity)
- Designed as parallel streams; likely sequential in practice but either order works

**S250.4 last (validation after all changes):**
- Cannot validate contract compliance until all skills are refactored
- Small scope: audit + CLI validation code + sync
- Natural epic close prep

---

*Created: 2026-02-23*
*Updated: 2026-02-23 (epic-plan added)*
