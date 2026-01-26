# Deep Research: Deterministic Extraction Patterns for Reliable Rule Generation

**Role**: Senior Reliability Engineer specializing in Reproducible Software Analysis
**Objective**: Investigate proven patterns for ensuring deterministic, reproducible rule extraction from codebases, addressing the gap between probabilistic pattern mining and governance-grade reliability.

---

## Meta-Instructions for Reasoning

1. **Reliability First**: We're building governance infrastructure—probabilistic approaches are insufficient
2. **Failure Mode Analysis**: For each pattern, analyze how it can fail and how to detect failures
3. **Reproducibility Standard**: Same codebase + same tools + same config → identical output
4. **Evidence Over Theory**: Cite real implementations, benchmarks, or case studies
5. **Falsification**: State conditions under which each pattern would not work

---

## Context: The Problem

Current AI-assisted rule extraction is probabilistic:
- Amazon CodeGuru achieves 73% acceptance rate (27% noise)
- LLM-based pattern detection varies across runs
- Semi-automated approaches require human curation

**Goal**: Identify patterns that achieve >95% determinism in rule extraction, where "determinism" means:
1. **Repeatability**: Running extraction twice produces identical results
2. **Predictability**: Given input characteristics, output is foreseeable
3. **Auditability**: Every extracted rule traces to specific evidence

---

## Research Questions

### 1. Reproducibility in Static Analysis

**Primary Question**: How do established static analysis tools ensure reproducible results?

Investigate:
- **SonarQube**: How does it maintain rule consistency across scans?
- **CodeClimate**: Quality engine reproducibility guarantees
- **Coverity**: Deterministic defect detection
- **Infer (Facebook)**: Compositional analysis for reproducibility
- **ErrorProne (Google)**: Compile-time pattern detection

For each, document:
- What makes their detection deterministic?
- How do they handle non-deterministic language features (reflection, dynamic typing)?
- Version pinning and configuration management
- Known sources of non-determinism and mitigations

**Deliverable**: Reproducibility patterns extracted from production tools.

### 2. Deterministic Scoring Algorithms

**Primary Question**: How should pattern candidates be scored to ensure consistent prioritization?

Investigate:
- **Frequency-based scoring**: Count occurrences, threshold selection
- **Criticality assessment**: Security vs maintainability vs style
- **Stability metrics**: Git history age, change frequency
- **Confidence intervals**: Statistical approaches to pattern significance

Specific questions:
- What thresholds are empirically validated? (e.g., "3+ occurrences" rule)
- How to handle edge cases (patterns appearing exactly at threshold)?
- How to combine multiple scoring dimensions?
- What normalization approaches prevent bias?

**Deliverable**: Scoring algorithm specification with mathematical formulation.

### 3. Evidence Collection Standards

**Primary Question**: What evidence standards ensure extracted rules are defensible?

Investigate:
- **Example requirements**: How many positive/negative examples validate a pattern?
- **Counter-example importance**: Role of violations in rule definition
- **Evidence freshness**: How old can examples be before they're stale?
- **Evidence distribution**: Should examples span multiple modules/authors?

Look at:
- Academic standards for empirical software engineering
- Legal/compliance documentation requirements
- Amazon CodeGuru's evidence collection methodology
- Google's C++ style guide evolution process

**Deliverable**: Evidence specification for rule extraction (minimum viable evidence set).

### 4. Handling Non-Deterministic Inputs

**Primary Question**: How do we achieve determinism when the codebase itself has non-deterministic elements?

Investigate:
- **Generated code**: How to handle auto-generated files?
- **Dynamic patterns**: Reflection, metaprogramming, macros
- **External dependencies**: Patterns in node_modules, vendor directories
- **Configuration-dependent code**: #ifdef, feature flags
- **Test vs production code**: Different pattern expectations

For each:
- Detection heuristics (how to identify non-deterministic code)
- Exclusion strategies (when to skip)
- Normalization approaches (how to make comparable)

**Deliverable**: Decision tree for handling edge cases.

### 5. Version Control and Reproducibility

**Primary Question**: How do we ensure extraction results are reproducible over time?

Investigate:
- **Tool version pinning**: Lock files, container images
- **Configuration as code**: Storing extraction config in repo
- **Codebase snapshots**: Git commit pinning
- **Intermediate artifact caching**: Avoiding re-extraction
- **Audit trails**: Logging extraction decisions

Look at:
- Reproducible builds movement (reproducible-builds.org)
- Nix/Guix deterministic package management
- Docker multi-stage builds for reproducibility
- SLSA framework (Supply-chain Levels for Software Artifacts)

**Deliverable**: Reproducibility checklist for rule extraction pipeline.

### 6. Validation and Verification Patterns

**Primary Question**: How do we verify that extraction is correct and complete?

Investigate:
- **Ground truth comparison**: Human-labeled patterns vs extracted
- **Cross-validation**: Multiple extraction runs, different tools
- **Mutation testing**: Inject known patterns, verify detection
- **Recall vs precision trade-offs**: What's acceptable for governance?
- **Drift detection**: Identifying when extraction quality degrades

Metrics to define:
- True positive rate (correctly identified patterns)
- False positive rate (noise in extracted rules)
- Coverage (% of actual patterns detected)
- Consistency (variance across runs)

**Deliverable**: Validation framework specification.

---

## Required Output Structure

### Section 1: Reproducibility Principles (~1,500 words)

Extract core principles from static analysis tools:
- Principle 1: [Name] - [Description] - [Evidence from tools]
- Principle 2: ...
- ...

Include failure modes for each principle.

### Section 2: Deterministic Scoring Algorithm (~2,000 words)

Propose a scoring algorithm:
```
Score = f(frequency, criticality, stability, clarity)
```

Include:
- Mathematical formulation
- Threshold justification (with citations)
- Edge case handling
- Normalization approach
- Sensitivity analysis (how does score change with input variations?)

### Section 3: Evidence Standards Specification (~1,500 words)

Define minimum viable evidence for rule extraction:

| Evidence Type | Minimum Count | Quality Criteria | Staleness Threshold |
|---------------|---------------|------------------|---------------------|
| Positive examples | 3 | Must compile, diverse locations | < 6 months |
| Counter-examples | 2 | Actual violations, not synthetic | < 12 months |
| ... | ... | ... | ... |

### Section 4: Non-Determinism Handling (~1,500 words)

Decision tree:
```
Is code generated? → [Action]
Is code dynamic? → [Action]
Is code external? → [Action]
...
```

With rationale for each decision.

### Section 5: Reproducibility Checklist (~1,000 words)

Actionable checklist:
- [ ] Tool versions pinned in `tool-versions.yaml`
- [ ] Extraction config committed to repo
- [ ] Codebase commit hash recorded
- [ ] ...

### Section 6: Validation Framework (~1,500 words)

Specify:
- Metrics to track (precision, recall, consistency)
- Target thresholds (>95% precision, >80% recall)
- Validation workflow (when to run, how to interpret)
- Regression detection (alert on quality drop)

---

## Quality Criteria

- [ ] At least 5 production static analysis tools analyzed
- [ ] Scoring algorithm is mathematically specified
- [ ] Evidence standards cite empirical research
- [ ] Reproducibility patterns from real-world systems
- [ ] Validation framework includes specific metrics
- [ ] All recommendations include falsification conditions

---

## Constraints

- **Governance-Grade**: This is for reliable AI software engineering—not best-effort
- **Agent-Executable**: Patterns must be implementable by AI agents following Katas
- **Auditable**: Every extraction decision must be traceable
- **Cross-Language**: Patterns should work for Python, TypeScript, Go, Java (at minimum)

---

**Target Length**: 9,000-10,000 words
**Confidence Level Required**: HIGH for core patterns, MEDIUM acceptable for edge cases
**Output Location**: `specs/main/research/deterministic-rule-extraction/deterministic-extraction-patterns.md`
