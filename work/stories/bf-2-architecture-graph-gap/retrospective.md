# Retrospective: BF-2 Architecture Graph Gap

## Summary
- **Story:** BF-2 (bugfix, systemic)
- **Started:** 2026-02-10
- **Completed:** 2026-02-10
- **Size:** L (estimated), actual execution was efficient
- **Commits:** 7 (scope, expanded scope, design, plan, templates+validate, skills, scaffold tests)
- **Files changed:** 14 (977 insertions, 16 deletions)

## What Went Well
- **Ishikawa from SES-133 paid off** — root cause analysis in the previous session meant we started with a clear scope document, no guesswork
- **TDD caught the scaffold regression** — adding domain-model.md to `_GOVERNANCE_TEMPLATES` broke 4 tests. Full suite run caught it before review. Exactly what PAT-202 (templates-as-contract) predicts.
- **Pre-design conversation was valuable** — Emilio's insight about graph completeness validation elevated BF-2 from "fix templates" to "fix the class of bug." F5 (completeness check) was added before design, not as an afterthought.
- **Parser is correct, data is wrong** — correctly identified that builder.py needed no changes. The fix was entirely in templates and skill instructions. This kept scope tight.

## What Could Improve
- **Scaffold test counts are fragile** — hardcoded `6` in 4 tests broke when we added 1 template. These should either use `len(_GOVERNANCE_TEMPLATES)` or be structured as "at least N" assertions. Fragile literal counts are a recurring issue.
- **Full test suite should run before committing** — I ran focused tests after Tasks 1-6 but only ran the full suite at review time. The scaffold failures would have been caught earlier with a full run after the governance.py change.

## Heutagogical Checkpoint

### What did you learn?
- Silent parser failures (returning None instead of raising) create a class of bugs where absence is invisible. The completeness check is a minimal but effective countermeasure — it doesn't prevent the bug, but it makes the symptom visible.
- Skill instructions ARE code in the RaiSE model. A false statement in a skill ("architecture docs don't produce nodes") propagated silently because skills aren't tested the way code is.

### What would you change about the process?
- Run full test suite after ANY change to `_GOVERNANCE_TEMPLATES` or similar registry lists — these have downstream test dependencies that focused tests won't catch.

### Are there improvements for the framework?
- **Parking lot captured:** Lifecycle-aware graph health contract (beyond the minimal check we added)
- **Parking lot captured:** Tools for human to understand and care for Rai's memory state
- **Future consideration:** Skill testing — could we lint skills for factual claims about the codebase? The false statement on line 413 sat there across multiple sessions.

### What are you more capable of now?
- Understanding the full template → scaffold → parse → graph pipeline end-to-end
- Recognizing that "silent success with empty output" is a systematic risk pattern in parser-based systems

## Improvements Applied
- Templates now have YAML frontmatter (contract matches parser)
- `raise memory validate` includes completeness check
- Skills corrected and expanded with module doc generation
- Parking lot entries for systemic follow-up

## Action Items
- [ ] Consider deriving scaffold test counts from `_GOVERNANCE_TEMPLATES` length instead of hardcoding
- [ ] Full lifecycle graph health contract (parking lot)
- [ ] Skill factual accuracy linting (parking lot — longer term)
