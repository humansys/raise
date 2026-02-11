# Governance-as-Code for AI Agents: Executive Summary

**Research ID**: RES-KATA-HARNESS-GOV-001
**Date**: 2026-01-29
**Status**: Complete
**Reading Time**: 5 minutes

---

## The Challenge

**Question**: Can we enforce governance policies as executable code rather than relying on LLM prompt compliance?

**Context**: RaiSE's Jidoka principle requires stopping execution on defects. Current implementation embeds "STOP" instructions in prompts:

```markdown
> **Si no puedes continuar**: File not found → **JIDOKA**: Ask user...
```

**Problem**: This is not deterministic. LLM must interpret when to stop. Sometimes it doesn't.

---

## The Answer

**YES.** Governance can be enforced through policy-as-code.

**Solution**: Separate three concerns currently conflated in `.raise/commands/`:

| Layer | Current State | Proposed State | Technology |
|-------|---------------|----------------|------------|
| **Process** | Mixed in command | Pure kata (Markdown) | `flujo-01-discovery.md` |
| **Policy** | Mixed in command | Separate YAML files | `discovery-policy.yaml` |
| **Enforcement** | LLM interprets | Deterministic harness | `kata_executor.py` |

**Result**: Harness reads policy, enforces checks, stops on failures. No LLM interpretation needed.

---

## How It Works

### Before (Current State)

```markdown
<!-- .raise/commands/project/create-prd.md -->
2. **Paso 1: Recopilar Contexto**:
   - **Verificación**: La documentación existe
   - > **Si no puedes continuar**: Documentación no encontrada → **JIDOKA**: Preguntar al usuario
```

**Problem**: LLM must parse text, decide if condition met, execute STOP instruction. Sometimes misses it.

---

### After (Proposed State)

**Kata** (pure process):
```markdown
<!-- .raise/katas/flujo-01-discovery.md -->
### Paso 1: Recopilar Contexto
Recopilar documentación existente del proyecto.
```

**Policy** (executable rules):
```yaml
# .raise/policies/discovery-policy.yaml
checks:
  - check_id: PRE-001
    validator: file_exists_any
    params:
      paths: [docs/context.md, docs/product-brief.md]
    severity: error
    on_fail:
      action: stop_execution
      message: "No context documents found"
      recovery_guidance:
        - "Add docs/context.md"
        - "Or run: /raise.setup.analyze-codebase"
```

**Harness** (enforces):
```python
# raise/kata_executor/executor.py
def execute_kata(kata_id):
    policy = load_policy(f"{kata_id}-policy.yaml")

    # Pre-execution gate
    for check in policy.preconditions:
        result = evaluate(check)
        if not result.passed and check.severity == "error":
            display_error(check.on_fail)
            sys.exit(1)  # STOP (deterministic)

    # Execute kata
    run_kata_steps(kata_id)

    # Post-execution gate
    run_validation_gate(policy.gate_id)
```

**User Experience**:
```
User: /raise.1.discovery

Kata Executor: Running pre-execution checks...
Kata Executor:   [❌ FAIL] PRE-001: Context documents not found

🛑 JIDOKA: Execution stopped.

No context documents found at: docs/context.md or docs/product-brief.md

🛠️  Recovery:
  1. Add docs/context.md with project context
  2. Or run: /raise.setup.analyze-codebase
  3. Re-run: /raise.1.discovery

Execution halted.
```

**Benefit**: Deterministic. Clear. Actionable. No tokens wasted.

---

## Key Findings (From 57k Word Research)

### 1. Policy-Mechanism Separation Works

**Industry Proof**: OPA (Kubernetes), Guardrails AI (LLM validation), NeMo Guardrails (conversational AI) all use this pattern successfully.

**Application to RaiSE**: Separate policy (YAML files) from harness (Python executor). Update policies without changing code.

---

### 2. Three Enforcement Points

| Timing | Purpose | RaiSE Status | Gap |
|--------|---------|--------------|-----|
| **Pre-execution** | Check preconditions before starting | ❌ Missing | **Major Gap** |
| **Runtime** | Monitor during execution | ❌ Missing | Phase 3 |
| **Post-execution** | Validate output after completion | ✅ Exists (but not automated) | Need automation |

**Critical**: Pre-execution gates missing. Katas waste tokens executing, then fail at the end.

---

### 3. Custom DSL Recommended

**Alternatives Evaluated**:
- **OPA/Rego**: Too complex (learning curve for Orquestador)
- **Cedar (AWS)**: Too AWS-specific
- **Constitutional AI**: Not enforceable (training-time only)

**Recommendation**: Custom YAML-based DSL

**Why**:
- Familiar (YAML used in CI/CD, Docker Compose, etc.)
- LLM-friendly (agent can read/explain policies)
- Simple (5 core policy types, 10 built-in validators)
- Aligns with Heutagogy (self-directed learning, low barrier)

---

### 4. Executable Gates Beat Text Checklists

**Current Gates**: Markdown checklists (`.raise/gates/gate-discovery.md`)

**Problem**: Interpretive. Human or LLM must verify. Not deterministic.

**Solution**: YAML gates with executable validators

**Before**:
```markdown
- [ ] >= 5 requisitos funcionales
```

**After**:
```yaml
checks:
  - validator: count
    params:
      file: specs/main/project_requirements.md
      selector: "## Requisitos Funcionales > list items"
      operator: ">="
      threshold: 5
    severity: error
```

**Benefit**: Same artifact always produces same result. Testable. Auditable.

---

### 5. Trade-Off: 70% Strict, 30% Flexible

**Strict Enforcement** (70%):
- File existence checks
- Schema validation (frontmatter, sections)
- Artifact completeness (min requirements)
- Terminology compliance

**Heuristic Guidelines** (30%):
- Writing style (agent chooses phrasing)
- Example selection (agent picks relevant examples)
- Diagram style (Mermaid vs PlantUML)

**Why This Balance**:
- Strict rules prevent catastrophic failures
- Heuristics allow Shu-Ha-Ri progression (adapt to context)
- 70/30 aligns with Lean (eliminate waste, don't over-constrain)

---

## Proposed Architecture

### File Structure (After Implementation)

```
.raise/
├── katas/                  # Layer 1: Process knowledge
│   ├── flujo-01-discovery.md
│   ├── flujo-02-solution-vision.md
│   └── flujo-03-tech-design.md
│
├── policies/               # Layer 2: Governance rules
│   ├── pre-discovery-policy.yaml
│   ├── discovery-policy.yaml
│   ├── pre-vision-policy.yaml
│   └── vision-policy.yaml
│
├── gates/                  # Validation gates (YAML, not Markdown)
│   ├── gate-discovery.yaml
│   ├── gate-vision.yaml
│   └── gate-design.yaml
│
└── schemas/                # JSON Schemas for validation
    └── policy-schema.json

raise/
├── policy_engine/          # Layer 3: Enforcement harness
│   ├── loader.py
│   ├── executor.py
│   └── validators/
│       ├── file_exists.py
│       ├── count.py
│       └── ...
└── kata_executor/
    ├── executor.py
    ├── pre_gate_runner.py
    └── gate_runner.py
```

---

## Implementation Roadmap

### Phase 1: MVP (Weeks 1-4)

**Goal**: Prove concept with basic enforcement

**Week 1**: Policy DSL + Engine Core
- Define JSON Schema
- Implement policy loader/executor
- Unit tests

**Week 2**: Built-In Validators
- 5 core validators (file_exists, count, section_present, etc.)
- Markdown parser utility
- Validator tests

**Week 3**: Pre-Execution Gates
- Create 3 pre-execution policies
- Integrate into kata executor
- Fail-fast enforcement

**Week 4**: Post-Execution Gates
- Convert 3 Markdown gates to YAML
- Implement gate runner
- CLI commands (`rai gate run`)

**Deliverable**: User runs `/raise.1.discovery`, pre-gate checks, kata executes, post-gate validates. Deterministic enforcement.

---

### Phase 2: Observability (Weeks 5-8)

**Goal**: Add telemetry and reporting

**Week 5**: Audit Logging (PostgreSQL)
**Week 6**: Gate Dashboard (CLI report)
**Week 7**: Policy Versioning (SemVer, upgrades)
**Week 8**: Custom Validators (plugin system)

**Deliverable**: Team uses gate reports to identify patterns, optimize policies.

---

### Phase 3: Runtime Monitoring (Weeks 9-12, Optional)

**Goal**: Detect deviations mid-execution

**Week 9-10**: File Watcher (monitor file modifications)
**Week 11**: Token Budget Monitor (detect runaway loops)
**Week 12**: Time Limit Monitor (detect hung executions)

**Deliverable**: Real-time violation detection (Phase 3 complexity, can defer).

---

## Success Metrics

### MVP (Phase 1)

**Quantitative**:
- 3 pre-execution policies created
- 3 post-execution gates converted to YAML
- 5 built-in validators implemented
- 100% test coverage for policy engine
- 3 katas execute with enforcement

**Qualitative**:
- Clear pass/fail messages
- Actionable recovery guidance
- Deterministic Jidoka stops
- Team consensus: "Better than Markdown checklists"

---

## ROI Analysis

### Current State (Cost)

**Problem**: Katas waste tokens on failed preconditions

**Example**:
1. User runs `/raise.4.tech-design`
2. Solution Vision missing (precondition not met)
3. LLM executes full kata (5,000 tokens consumed)
4. Post-gate fails: "Solution Vision not found"
5. User realizes mistake, runs `/raise.2.vision`
6. Re-runs `/raise.4.tech-design` (another 5,000 tokens)

**Cost**: 10,000 tokens ($0.50 at $0.05/1k tokens). Repeated 10x/month = $5/month wasted per user.

---

### Proposed State (Savings)

**Solution**: Pre-execution gate checks preconditions

**Example**:
1. User runs `/raise.4.tech-design`
2. Pre-gate checks: Solution Vision missing
3. **STOP immediately** (0 kata tokens consumed)
4. Clear error: "Run /raise.2.vision first"
5. User runs Vision, then Design (correct order)

**Savings**: 5,000 tokens saved per failed attempt. 10 failures/month = 50,000 tokens = $2.50/month per user.

**Additional Benefits**:
- Better UX (clear errors, faster feedback)
- Reduced frustration (no wasted work)
- Higher adoption (trust in system)

---

## Risks & Mitigations

### Risk 1: Policy DSL Too Complex

**Likelihood**: Medium
**Impact**: High (defeats purpose if unused)

**Mitigation**:
- Start with simplest possible DSL
- Provide migration tool (Markdown → YAML)
- Document with examples
- Get feedback from 3 teams before finalizing

---

### Risk 2: Performance Overhead

**Likelihood**: Medium
**Impact**: Medium (users skip gates if slow)

**Mitigation**:
- Benchmark validators (<100ms each)
- Cache policy loads
- Parallelize independent checks
- Add `--skip-gates` flag for dev mode

---

### Risk 3: False Positives

**Likelihood**: High (initial iterations)
**Impact**: High (trust erosion)

**Mitigation**:
- Start with warning-only mode
- Collect data for 2 weeks, tune thresholds
- Implement override mechanism
- User feedback loop

---

## Recommendations (Priority Order)

### P0: Approve Phase 1 Scope (4 weeks)

**Decision Point**: Commit to MVP implementation

**Action**:
- Review research documents (this + 3 detailed docs)
- Approve 4-week roadmap
- Allocate developer time
- Schedule daily standups

**Timeline**: Decision by 2026-01-31

---

### P1: Start Week 1 Implementation

**Action**:
- Create project structure (`raise/policy_engine/`, `.raise/policies/`)
- Define JSON Schema for policy YAML
- Implement policy loader
- Write unit tests

**Timeline**: Week of 2026-02-03

---

### P2: Alpha Testing (Week 3)

**Action**:
- Recruit 1 external team
- Deploy pre-execution gates
- Collect feedback
- Iterate rapidly

**Timeline**: Week of 2026-02-17

---

### P3: Beta Release (Week 4)

**Action**:
- Deploy to 3 teams
- Announce to RaiSE community
- Collect metrics (pass rate, time saved)
- Plan Phase 2 based on feedback

**Timeline**: Week of 2026-02-24

---

## Questions for Decision

### Q1: Custom DSL or OPA?

**Recommendation**: Custom DSL (Phase 1). Adopt OPA if complexity grows.

**Rationale**: Lower learning curve, LLM-friendly, aligns with Heutagogy.

---

### Q2: 4-Week MVP or 8-Week Full?

**Recommendation**: 4-week MVP (pre-gates + post-gates only).

**Rationale**: Faster to production, prove concept, get user feedback sooner.

---

### Q3: Big Bang or Gradual Migration?

**Recommendation**: Gradual (convert 3 gates in Phase 1, rest in Phase 2).

**Rationale**: Lower risk, validate approach incrementally.

---

## Resources

### Research Documents (This Package)

1. **README.md** (13k words) - Overview, architecture, quick reference
2. **governance-patterns-research.md** (57k words) - Comprehensive research
3. **policy-dsl-specification.md** (26k words) - Technical spec, YAML schema
4. **implementation-roadmap.md** (30k words) - Week-by-week plan
5. **EXECUTIVE-SUMMARY.md** (this doc) - 5-minute overview

**Total**: 136,000 words of research and specifications

---

### External References

- **OPA**: https://www.openpolicyagent.org/
- **Guardrails AI**: https://www.guardrailsai.com/
- **Semgrep**: https://semgrep.dev/

---

## Next Steps (Immediate)

1. **Read This Summary** (5 minutes)
2. **Review README** (15 minutes)
3. **Skim Research** (30 minutes) - focus on Section 2, 7
4. **Review Roadmap** (10 minutes) - focus on Phase 1
5. **Decision Meeting** (60 minutes) - approve scope
6. **Start Implementation** (Week 1, Day 1)

---

## Contact

**Research Lead**: Claude Sonnet 4.5 (Assisted)
**Project Owner**: Emilio (RaiSE Framework)
**Date**: 2026-01-29
**Status**: Research Complete, Awaiting Approval

---

**End of Executive Summary**

**Key Takeaway**: Governance-as-code is feasible, proven, and aligned with RaiSE's Constitution. The MVP (4 weeks) delivers deterministic policy enforcement with clear ROI. Recommend immediate approval and implementation.
