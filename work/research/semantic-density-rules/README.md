# Semantic Density Rules - Research Directory

This directory contains research on achieving determinism and semantic density in LLM-based rule systems for the RaiSE Framework.

## Documents

### 1. Determinism Patterns Catalog
**File**: `determinism-patterns-catalog.md`
**Status**: Completed
**Date**: 2026-01-29

Comprehensive catalog of patterns for achieving deterministic behavior in LLM-based agent systems, specifically for RaiSE Kata execution.

**Key Findings**:
- Structured output enforcement (tool use, grammar-constrained generation) achieves >95% schema compliance
- State machine approaches provide deterministic flow control
- "Thin LLM" architecture (LLM decides, code executes) is optimal for governance
- Verification layers provide safety nets but don't prevent invalid generation

**Recommended Architecture for RaiSE**:
1. **XState for Flow Control**: Kata workflows as state machines
2. **Structured Outputs**: All LLM outputs use typed schemas (Pydantic)
3. **Thin LLM Pattern**: LLM selects tools, deterministic code executes
4. **Guardrails**: Safety net for file operations and Git commands

**Patterns Covered**:
- Structured Output Enforcement (Tool Use, Grammar-Constrained Decoding, Schema Validation)
- State Machine Approaches (XState, FSM)
- Program Synthesis (DSPy, Prompt Chaining)
- Hybrid Architectures (LLM Router, Planning vs Execution)
- Verification Layers (Guardrails AI, Constitutional AI)

**Implementation Roadmap**: ~11 weeks
- Phase 1: Structured Outputs for Gates (2 weeks)
- Phase 2: Tool Use for File Operations (2 weeks)
- Phase 3: Thin LLM Architecture (3 weeks)
- Phase 4: XState for Kata Flow (3 weeks)
- Phase 5: Guardrails for Safety (1 week)

---

## Related Research

### In raise-commons Repository

- **Deterministic Rule Extraction**: `specs/main/research/deterministic-rule-extraction/deterministic-extraction-patterns.md`
  - Patterns for reproducible rule extraction from codebases
  - Evidence standards and scoring algorithms
  - Validation frameworks

- **Deterministic Rule Delivery**: `specs/main/research/deterministic-rule-delivery/architecture-specification.md`
  - Graph-based rule delivery architecture
  - YAML-MD format for rules
  - CLI design for deterministic retrieval

- **Semantic Density Research Prompt**: `specs/main/research/prompts/semantic-density-research.md`
  - Original research prompt defining the investigation
  - Domains of investigation
  - Evaluation criteria

### External References

**Structured Outputs**:
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Instructor](https://github.com/jxnl/instructor)
- [Outlines](https://github.com/outlines-dev/outlines)

**State Machines**:
- [XState](https://xstate.js.org/)
- [Python Transitions](https://github.com/pytransitions/transitions)

**Verification**:
- [Guardrails AI](https://github.com/guardrails-ai/guardrails)
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails)

---

## Usage

### For Kata Developers

When implementing new Katas, apply these patterns:

1. **Define validation gates as structured outputs**:
```python
from pydantic import BaseModel

class GateResult(BaseModel):
    gate_id: str
    passed: bool
    criteria_met: list[str]
    criteria_failed: list[str]
    evidence: str
```

2. **Use tools for all file operations**:
```python
tools = [
    {
        "name": "write_file",
        "description": "Write content to file",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            }
        }
    }
]
```

3. **Model Kata flow as state machine** (future):
```typescript
const kataFlowMachine = createMachine({
  id: 'kata',
  initial: 'init',
  states: {
    init: { on: { START: 'load_template' } },
    load_template: { on: { LOADED: 'execute', ERROR: 'jidoka' } },
    execute: { on: { COMPLETE: 'verify' } },
    verify: { on: { PASSED: 'complete', FAILED: 'jidoka' } },
    jidoka: { on: { RETRY: 'execute', ABORT: 'error' } },
    complete: { type: 'final' },
    error: { type: 'final' }
  }
});
```

### For Researchers

To extend this research:

1. **Benchmark determinism**: Create test suite with expected outputs, measure reproducibility across LLM versions
2. **Formal verification**: Explore TLA+ specifications for Kata workflows
3. **Adaptive tool selection**: ML-based selection of most reliable tools per Kata step

---

## Open Questions

1. Can grammar-constrained generation work with hosted APIs (OpenAI/Anthropic)?
2. At what complexity do state machines become unmaintainable?
3. How to ensure deterministic multi-agent collaboration?
4. Can we formally verify Kata workflows?

---

## Metrics

Track these metrics to measure determinism:

| Metric | Target | Current |
|--------|--------|---------|
| Schema Compliance | 98% | TBD |
| Tool Call Success | 95% | TBD |
| Flow Consistency | 100% | TBD |
| Reproducibility | 90%+ | TBD |
| Validation Pass Rate | 85%+ | TBD |

---

**Maintained by**: RaiSE Research Team
**Last Updated**: 2026-01-29
