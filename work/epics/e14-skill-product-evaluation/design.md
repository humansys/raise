# Epic E14: Skill Product Evaluation — Design

> **Status:** IN PROGRESS
> **Jira:** [RAISE-1006](https://humansys.atlassian.net/browse/RAISE-1006)
> **Created:** 2026-03-28

## Gemba Walk Findings (2026-03-28)

Interactive audit of skill system with product owner. Key observations:

### What exists and works

1. **ADR-040 Skill Contract** (raise-commons) — 7-section canonical structure, ≤150 lines, quantitative targets, evidence-based positioning (primacy/recency). Enforced by `rai skill validate`.

2. **ADR-012 Skills + CLI Toolkit** — Deliberate separation: skills = probabilistic guidance for LLM, CLI toolkit = deterministic data extraction. This is the correct architecture.

3. **ADR-024 Deterministic Session Protocol** — CLI assembles context bundle deterministically. Skill interprets fresh inference over deterministic data.

4. **`/rai-skill-create`** (raise-commons) — Guided skill creation with ADR-040 compliance. Not synced to rai.

5. **Governance hooks** (rai-agent) — PreToolUse/PostToolUse/Stop hooks implemented. Disabled by SDK bug (RAISE-1007/RAI-29).

6. **`invoke_structured()`** (rai-agent) — Pydantic-validated structured output for pipelines. Pattern exists but not used in skill orchestration.

7. **Middleware pipeline** (rai-agent) — Auth, rate limit, coalescing, dispatch. Robust pre-execution control.

8. **Typed artifacts** — `rai-story-design` produces YAML artifacts with schema. Embryo of typed skill outputs, but isolated case.

### What's missing (gaps)

| Gap | Impact | Where it should live |
|-----|--------|---------------------|
| **Governance hooks disabled** (RAISE-1007) | No runtime enforcement of tool policies, HITL, auditing | rai-agent runtime |
| **Memory injection is opt-in** | Skills inconsistently use graph; most don't query it | rai-agent runtime (pre-skill injection) |
| **No typed skill outputs** | Skills declare outputs in metadata strings, no schema validation between skills | rai-agent orchestrator (post-skill validation) |
| **`<verification>` blocks ignored by LLM** | Deterministic intent without enforcement | rai-agent runtime (assertion mechanism) |
| **Metadata inputs/outputs not parseable** | `'- plan_md: file_path, required, previous_skill'` is a string, not schema | ADR-040 extension or new contract |
| **No skill orchestrator** | No pre/execute/post lifecycle in runtime | rai-agent (new layer) |
| **Skill sync gap** | /rai-skill-create, ADR-040, validate not in rai | rai-framework-sync or manual |
| **No free/PRO classification** | Users don't know which skills require license | Product definition |

### Architecture: Where enforcement should live

```
┌─────────────────────────────────────────────────┐
│ rai-agent Runtime                                │
│                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │ PRE-SKILL│   │ EXECUTE  │   │POST-SKILL│    │
│  │          │   │          │   │          │    │
│  │ • Validate│   │ • LLM    │   │ • Validate│   │
│  │   prereqs│   │   reads  │   │   outputs │   │
│  │ • Inject │   │   SKILL  │   │ • Record  │   │
│  │   graph  │   │   .md    │   │   metrics │   │
│  │   context│   │ • Calls  │   │ • Trigger │   │
│  │ • Check  │   │   CLI    │   │   next    │   │
│  │   inputs │   │   tools  │   │   skill   │   │
│  │ • Gov    │   │ • Gov    │   │ • Gov     │   │
│  │   hooks  │   │   hooks  │   │   hooks   │   │
│  └──────────┘   └──────────┘   └──────────┘    │
│                                                  │
│  Governance Hooks: PreToolUse / PostToolUse      │
│  Memory: auto-inject from graph based on skill   │
│  Assertions: runtime check of <verification>     │
└─────────────────────────────────────────────────┘
         ↑                              ↑
    ADR-040                    ADR-012 preserved
    (structure)            (skills = probabilistic,
                            toolkit = deterministic)
```

## Research Grounding

**Report:** `research-deterministic-harnesses.md` (42 sources, High confidence)

### Key findings applied to RaiSE

| State of Art Pattern | RaiSE Equivalent | Gap |
|---------------------|-------------------|-----|
| DSPy Assertions (Assert/Suggest) | `<verification>` blocks | No runtime enforcement — LLM ignores them |
| BAML/Instructor typed outputs | `invoke_structured()` | Exists for pipelines, not for skill outputs |
| NeMo pre/in/post guardrails | Governance hooks | Implemented but disabled (RAISE-1007) |
| A-MEM default memory | `rai graph query` | Opt-in per step, not default |
| LangGraph state machines | Sequential skill chaining | Linear only, no conditional routing |
| ADR-040 ≈ Anthropic skill contract | ADR-040 | Structure contract exists; behavior contract missing |

### RaiSE unique advantage (defensible)

**Natural language as harness language.** DSPy requires Python, BAML requires DSL, LangGraph requires graph definitions. RaiSE skills are readable markdown. The challenge: add rigor without losing accessibility.

### Contribution opportunity

**No published poka-yoke taxonomy for LLM systems exists** (confirmed across 42 sources). RaiSE could define and publish one based on the three mechanism types identified:
1. Structural (type schemas, grammar constraints)
2. Validation gates (pre/in/post checks)
3. Process sequencing (prerequisites, state machines)

## Key Contracts

### Skill Metadata (current — ADR-040)
```yaml
raise.prerequisites: story-plan      # string, not validated
raise.gate: gate-code                # string, not validated
raise.inputs: '- plan_md: ...'       # unparseable string
raise.outputs: '- code_commits: ...' # unparseable string
```

### Skill Metadata (proposed direction)
```yaml
raise.prerequisites: [story-plan]
raise.gate: gate-code
raise.inputs:
  - name: plan_md
    type: file_path
    required: true
    schema: plan-v1           # validatable
raise.outputs:
  - name: code_commits
    type: git_commits
    validation: tests_pass    # enforced by runtime
```

**Decision:** Whether to evolve metadata in ADR-040 or create a new ADR for "Skill Behavior Contract" → deferred to S14.3.

## Parking Lot

| Item | Origin | Priority | Promotion condition |
|------|--------|----------|-------------------|
| Skill composition (conditional routing, parallel) | Research §4 | Low | After v3.x linear skills are mature |
| Quantitative maturity scoring framework | Research §5 | Med | When industry standard emerges |
| Poka-yoke taxonomy publication | Research §2 | Med | After internal validation across 35 skills |
| Skill marketplace / registry | Gemba Q4 | Low | After PRO licensing (RAISE-621) |
