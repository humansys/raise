# Epic E1134: Skill CC-Alignment — Retrospective

**Epic:** E1134 | **Jira:** RAISE-1182 | **Release:** v2.4.0
**Stories:** 4 (2M + 2S) | **Date:** 2026-04-02

## Outcome

All 35 baseline skills aligned across 3 dimensions of CC metadata:

| Dimension | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Description avg length | ~300 chars | 85 chars | -72% |
| Description budget (auto-invocable) | ~10,500 chars | 2,247 chars | -78% |
| `allowed-tools` coverage | 0/35 (0%) | 35/35 (100%) | +100% |
| `disable-model-invocation` coverage | 0/35 (0%) | 13/35 (37%) | All side-effect skills |
| Verb-first descriptions | 0% | 33/35 (94%) | +94% |
| Descriptions <100 chars | 0% | 35/35 (100%) | +100% |

**3 post-baseline skills** (adapter-setup, epic-research, sonarqube) were added after E1134 work started and need follow-up alignment.

## Stories Delivered

| Story | Size | Est | Actual | Key Output |
|-------|:----:|:---:|:------:|------------|
| S1134.3 Invocation control | S | 15m | 20m | 13 skills with `disable-model-invocation: true` |
| S1134.1 Description optimization | M | 45m | 25m | 35 descriptions rewritten, budget -78% |
| S1134.2 allowed-tools declaration | M | 30m | 15m | 35 skills with 7-tier classification |
| S1134.4 Validation & report | S | 15m | 10m | Validation script + before/after metrics |

**Total:** Estimated 105m, Actual ~70m (1.5x velocity).

## What Went Well

1. **Pre-design research paid off.** The 10-source evidence catalog (Anthropic code, CC docs, community) grounded every design decision. No rework from incorrect assumptions.
2. **Quick-win sequencing.** Starting with S1134.3 (smallest, validates CC parsing) built confidence and freed description budget for S1134.1.
3. **Script-based batch edits.** Both S1134.1 (descriptions) and S1134.2 (allowed-tools) used scripts for 34-35/35 files, with manual fix only for edge cases.
4. **QR caught a real gap.** S1134.3's quality review identified 4 additional side-effect skills missed by manual classification (bugfix, mcp-add, mcp-remove, discover).
5. **Validation script caught drift.** S1134.4 discovered 3 post-baseline skills, proving the script's value beyond this epic.

## What to Improve

1. **D2 tier count drifted.** Epic design said 6 tiers. Actual implementation needed 7 after reading all 35 skill bodies. Lesson: always classify from evidence (reading code), not from categories (naming patterns).
2. **Close agent went rogue.** The story-run close agent for S1134.2 made unauthorized changes — removed `disable-model-invocation` from 13 skills and deleted an unrelated epic directory. Required immediate revert. Lesson: close agents need stronger guardrails; scope their actions explicitly.
3. **Post-baseline drift.** 3 skills added between epic start and epic close had no alignment. Lesson: validation scripts should always glob broadly, not against a hardcoded list.

## Patterns Captured

| ID | Pattern | Source |
|----|---------|--------|
| PAT-E-701 | Side-effect classification should use audit (grep for write indicators) not manual curation | S1134.3 QR |
| PAT-E-694 | 7-tier allowed-tools classification with governance-writing gap insight | S1134.2 design |
| (candidate) | Validation scripts that glob broadly catch post-baseline drift | S1134.4 |

## Follow-Up Items

1. **Align 3 post-baseline skills** (adapter-setup, epic-research, sonarqube) with CC-alignment dimensions
2. **Consider CI gate** for skill metadata validation (run validate.py on PR)
3. **Test allowed-tools in practice** — T1 skills may need promotion to T2 if `rai` CLI calls are blocked

## Process Insights

- **Research before design works.** The rai-epic-research skill (drafted during this epic) formalizes what we did informally: Gemba audit + SOTA research + vision alignment before committing to a design.
- **Docs/analysis stories skip AR+QR correctly.** 3 of 4 stories were docs/analysis type. Skipping code reviews was appropriate — no code to review.
- **Batch metadata work is faster than estimated.** All 4 stories came in under estimate. The expensive part is classification (design phase); implementation is mechanical.

## Metrics

| Metric | Value |
|--------|-------|
| Tests | 696 passed, 14 skipped, 0 failures |
| Total commits | ~25 across 4 stories |
| Files modified | 35 SKILL.md + 2 validation artifacts + story docs |
| Patterns | 2 captured + 1 candidate |
| Velocity | 1.5x (estimated 105m, actual ~70m) |
