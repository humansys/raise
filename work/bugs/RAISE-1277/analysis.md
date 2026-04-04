# RAISE-1277: Analysis

## 5 Whys

| # | Why | Evidence |
|---|-----|----------|
| 1 | Records missing because agent skipped LEARN marker | 5/9 story chains incomplete |
| 2 | Marker is advisory text, no structural enforcement | `> **LEARN**` is a markdown pointer in SKILL.md |
| 3 | Design defers enforcement to rai-agent (future) | aspects/introspection.md �� Stepping stone integration |
| 4 | rai-agent is on release/3.0.0, v2.4.0 has no enforcement | EP1 pipeline engine on 3.0.0 |
| 5 | **Root cause:** No gate validates record completeness at any workflow point | gates/builtin/ has tests/lint/types/format/coverage — no learning gate |

**Countermeasure:** New `LearningChainGate` that validates expected records exist for a work_id.

## Fix Approach

1. Create `check_learning_chain(work_id, base_dir)` function in `memory/learning.py` — returns which skills have records, which are missing
2. Create `LearningChainGate` in `gates/builtin/learning.py` — evaluates chain completeness for current branch's work_id
3. Register via entry point (`rai.gates`)
4. Workflow point: `before:story:review` — so story-review skill can be told "records are missing, produce them before proceeding"

**Design constraint:** The gate should WARN, not BLOCK. Missing records may be legitimate (story-design is optional for XS stories). The gate reports completeness; the skill decides what to do.

## Implementation

The fix is tracked as a proper story: **RAISE-1285** (S1001.5: Learning Chain Gate) under epic RAISE-1001 (Bug-Driven Process Improvement). This bug (RAISE-1277) is blocked by RAISE-1285.

Rationale: the fix requires 3 deliverables (function + gate + CLI) with TDD — story lifecycle is more appropriate than inline bugfix.
