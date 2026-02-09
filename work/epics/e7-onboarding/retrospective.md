# Epic Retrospective: E7 Onboarding

**Completed:** 2026-02-08
**Duration:** 1 day (started 2026-02-08)
**Stories:** 3 stories delivered (S + M + M)

---

## Summary

Delivered the complete onboarding pipeline: CLI scaffolding (`raise init`), greenfield skill (`/project-create`), and brownfield skill (`/project-onboard`). A developer can now go from zero to a working `/session-start` in under 10 minutes on either new or existing projects. The guardrails format harmonization fix ensures `raise init --detect` output is directly parseable by `raise memory build`.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 3 | S7.1, S7.2, S7.3 |
| Total Time | ~125 min | 30 + 50 + 45 min |
| Average Velocity | 1.44x | Faster than estimated across all 3 |
| Calendar Days | 1 | Single session delivery |

### Story Breakdown

| Story | Size | Estimated | Actual | Velocity | Key Learning |
|-------|:----:|:---------:|:------:|:--------:|--------------|
| S7.1: Governance scaffolding | S | 45 min | 30 min | 1.5x | PAT-202: templates-as-contract |
| S7.2: /project-create | M | 75 min | 50 min | 1.5x | Parser contracts are the skill's backbone |
| S7.3: /project-onboard | M | 60 min | 45 min | 1.33x | PAT-205: zombie cwd from temp dir deletion |

---

## What Went Well

- **Incremental architecture:** S7.1 → S7.2 → S7.3 built cleanly on each other. Each story reused patterns from the previous one.
- **Templates-as-contract (PAT-202/203):** Bundled governance templates in `rai_base` via `importlib.resources` — same distribution pattern as other assets.
- **Separate skills (PAT-201):** Greenfield and brownfield as distinct skills with shared parser contracts. Clear user experience for each case.
- **Integration tests:** Real end-to-end validation caught the guardrails format mismatch that unit tests wouldn't have found.
- **Single-day epic:** Full onboarding pipeline in one focused session.

## What Could Be Improved

- **Guardrails format drift:** `raise init --detect` generated guardrails in a different format than the parser expected. Fixed in S7.3, but this should have been caught earlier (integration test in S7.1 would have flagged it).
- **Shell cwd management:** Deleting a temp directory while cwd was inside it killed the shell for the rest of the session. Simple mistake, but cost time.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-202 | Templates-as-contract: scaffold files ARE the contract | CLI scaffolding + parser integration |
| PAT-203 | Same as PAT-202 (reinforced) | Governance templates |
| PAT-205 | Never delete dir while shell cwd is inside it | Integration testing with temp directories |

## Process Insights

- **Skill reuse with adaptation** is a powerful pattern: `/project-onboard` was ~80% structural reuse from `/project-create`, adapted for the brownfield flow.
- **Parser contracts as the shared interface** between skills and CLI: both skills generate the same format because both feed the same parsers. The contract is the integration point.
- **Convention detection → guardrails → graph** is a complete pipeline now. Discovery feeds governance, governance feeds the graph, the graph feeds sessions.

---

## Artifacts

- **Scope:** `work/epics/e7-onboarding/scope.md`
- **Stories:** `work/epics/e7-onboarding/stories/s7.{1,2,3}-*/`
- **Skills:** `.claude/skills/project-create/`, `.claude/skills/project-onboard/`
- **CLI:** `src/raise_cli/onboarding/governance.py` (guardrails format fix)
- **Tests:** 19 governance tests (1 new parser-compatibility test)

---

## Next Steps

- This epic completes the onboarding pipeline
- New projects: `raise init` → `/project-create` or `/project-onboard` → `/session-start`
- Next epic TBD

---

*Epic retrospective — captures learning for continuous improvement*
