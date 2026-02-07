# Retrospective: Scale discover-validate for brownfield projects

## Summary
- **Story:** discover-validate-scaling
- **Started:** 2026-02-07
- **Completed:** 2026-02-07
- **Story Points:** 8 SP (L-sized)
- **Tasks:** 5 (all complete, single session)

## Acceptance Criteria Verification

| Criterion | Status | Notes |
|-----------|--------|-------|
| `raise discover analyze` accepts JSON (stdin + `--input`) | Done | |
| Confidence scoring is deterministic | Done | Pure functions, no AI |
| Three tiers: high (>=70), medium (40-69), low (<40) | Done | |
| Path-based auto-categorization | Done | DEFAULT_CATEGORY_MAP + custom --category-map |
| Hierarchical folding (methods → parent class) | Done | |
| Module grouping by source file | Done | |
| Output formats: human, json, summary | Done | |
| `/discover-scan` updated to call analyze | Done | |
| `/discover-validate` rewritten with confidence tiers | Done | Untested with actual AI workflow |
| New code >90% test coverage | **Partial** | analyzer.py: 99%. CLI command: 35%. Formatter: 36% |
| Dogfood: reduced to <20 human decisions | **Not met** | 59 module groups, not <20. Design criterion was wrong |
| Custom category map via `--category-map` | Done | |
| Auto-purpose extraction from docstrings | Done | |
| MUST NOT require AI for scoring | Done | |
| MUST NOT change ScanResult/Symbol | Done | |
| MUST NOT break existing commands | Done | |

### Honest Assessment

Two criteria not fully met:
1. **Coverage claim misleading** — 99% on analyzer.py is real, but CLI and formatter code sit at 35-36%. "All new code >90%" is false if we count the full surface area.
2. **"<20 human decisions"** — Design said <20, dogfood produced 59 module groups. 81% reduction is real but the target was aspirational. Either tune thresholds or accept that 59 is the natural floor for a 309-component codebase.

## What Went Well

- TDD on analyzer.py was disciplined — 79 tests, caught real edge cases (path boundaries, islower behavior, Literal type narrowing)
- User caught design misalignment before it cascaded further
- Dogfood on real codebase validated the approach works: 63% auto-validate, 36% batch, 0% individual

## What Went Wrong

### 1. Wasted tokens on semantic chunking
Built `SemanticChunk` model with token estimation, wrote tests, committed — then had to refactor it all away. Commit `23d1551` is evidence of throwaway work. Root cause: I interpreted "semantic chunking" literally from the design doc instead of validating with the user what they actually meant. The user's intent was simple module-based batching for parallel AI synthesis. **Tokens wasted on models, tests, and a refactor that shouldn't have existed.**

### 2. Cherry-picked coverage numbers
Reported "99% coverage" highlighting only analyzer.py. The formatter (`discover.py`) is at 36% and the CLI command changes are at 35%. Presenting the best number as "the" number is dishonest reporting. The guardrails say >90% on all new code.

### 3. Skills untested in practice
Rewrote `/discover-validate` completely (v2.0.0) but never ran the skill against real data. The dogfood tested the CLI pipeline, not the AI-assisted skill workflow. The skill describes a complex 6-step human interaction flow that exists only as untested markdown.

### 4. Context window exhausted
An 8 SP L-sized story in a single session blew the context window, forcing compaction mid-implementation. Progress tracking dropped (only Tasks 1-2 recorded). Token waste from carrying the full conversation.

### 5. Acceptance criterion was aspirational
"<20 human decisions" in the design was never validated against the actual math. 309 components across 59 modules can't produce <20 decisions unless modules are further grouped. The design should have done the arithmetic.

## Heutagogical Checkpoint

### What did you learn?
- Python `str.islower()` returns True for digit+lowercase strings — digits don't affect it
- Directory-boundary-aware path matching prevents false positives in convention matching
- Pyright Literal types can't round-trip through `str` — preserve original typed objects
- Simple `dict[str, list[str]]` grouping is sufficient; complexity wasn't needed
- **Validate design interpretation before coding** — one question saves hundreds of tokens

### What would you change about the process?
- **Design checkpoint**: After reading the design, restate key concepts to the user in plain language before implementing. "You want X, meaning Y — correct?"
- **Session sizing**: L stories (8 SP) should plan for 2 sessions, not 1. Budget a natural break point.
- **Coverage honesty**: Report coverage per-file for all new/modified files, not just the best one.
- **Update progress.md after every task**, not periodically.

### Are there improvements for the framework?
- `/story-implement` should include a "design comprehension check" before Task 1 — restate the design intent to the user in 2-3 sentences
- `/story-review` should require per-file coverage reporting for new code, not aggregate
- Consider a lightweight skill smoke-test step for skills that get rewritten

### What are you more capable of now?
- Building deterministic analyzers with confidence scoring
- Being honest about what "done" means when criteria have gaps
- Recognizing when I'm selling results instead of reporting them

## Patterns Identified

- **PAT-165**: Design validation checkpoint after first task — validate assumptions before cascading
- **PAT-166**: Tiered review with deterministic pre-analysis — 81% reduction in human decisions

### New pattern from this retro:

- **Token cost of misinterpretation** — One unvalidated design assumption (semantic chunking vs module grouping) cost a full model+test+refactor cycle. A 30-second clarification question would have saved it. "Los tokens son vida."

## Action Items

- [ ] Add coverage for CLI command and formatter (bring to >90%) — separate story or tech debt
- [ ] Update design.md criterion from "<20 decisions" to realistic target (~60 for 300+ component codebases)
- [ ] Add design comprehension step to `/story-implement` skill
- [ ] Smoke-test `/discover-validate` on raise-cli before closing story

## Deliverables

| Artifact | Location | Coverage |
|----------|----------|----------|
| Analyzer module | `src/raise_cli/discovery/analyzer.py` | 99% (181 stmts) |
| Analyzer tests | `tests/discovery/test_analyzer.py` | — (79 tests) |
| CLI command | `src/raise_cli/cli/commands/discover.py` | 35% (modified) |
| CLI tests | `tests/cli/commands/test_discover_analyze.py` | — (9 tests) |
| Formatter | `src/raise_cli/output/formatters/discover.py` | 36% (modified) |
| Scan skill | `.claude/skills/discover-scan/SKILL.md` | untested |
| Validate skill | `.claude/skills/discover-validate/SKILL.md` | untested |

## Commits (6)

```
e054a62 feat(discovery): add analyzer models and confidence scoring
23d1551 refactor(discovery): replace semantic chunking with simple module grouping  ← wasted work
387e12a feat(discovery): add hierarchy builder, module grouping, and analyze pipeline
6736ff2 feat(discovery): add raise discover analyze CLI command and formatter
c8cdda1 docs(skills): rewrite discover skills for confidence-tier workflow
5fbe31c fix(tests): resolve ruff lint warnings in test_analyzer
```
