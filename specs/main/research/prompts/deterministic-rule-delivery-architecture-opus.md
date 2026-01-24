# Deep Research: Deterministic Rule Delivery Architecture for Governance-as-Code

## Meta-Instructions for This Research

You are conducting foundational architectural research for the RaiSE framework (Reliable AI Software Engineering). Your output will directly inform implementation decisions. Apply the following throughout:

**Reasoning Standards**:
- For each claim, distinguish between: (a) established fact, (b) reasonable inference, (c) informed speculation
- When comparing approaches, use explicit trade-off analysis with named dimensions
- State your confidence level (high/medium/low) for recommendations
- Identify assumptions that, if wrong, would invalidate your conclusions

**Epistemic Honesty**:
- If evidence is thin in an area, say so explicitly rather than filling with plausible-sounding content
- Distinguish between "no evidence exists" and "I couldn't find evidence"
- When industry practice conflicts with theoretical best practice, note both

---

## Context: The Problem Space

### The Reliability Problem in AI-Assisted Development

Current AI coding assistants (Cursor, Copilot, Claude Code) suffer from **model-selected rule application**—the agent decides which rules to apply and when. This introduces unacceptable variability for governance-critical workflows.

**Observed failure modes**:
| Failure Mode | Description | Severity |
|--------------|-------------|----------|
| Rule Ignorance | Agent has access to rules but doesn't apply them | High |
| Inconsistent Application | Same context yields different rule application across sessions | High |
| Prerequisite Blindness | Agent applies rule without its dependencies | Medium |
| Semantic Drift | Vector search returns similar-but-wrong rules | Medium |
| Context Overload | Too many rules degrade agent performance | Medium |

**The Core Insight**: The problem isn't retrieval technology—it's **model discretion**. When the agent decides what applies and when, reliability suffers.

### The Proposed Architecture

**Design Principle**: Remove model discretion from rule selection. The system determines WHAT rules apply; the agent's job is to APPLY them.

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOT RULES                                │
│  Static files, always in context (CLAUDE.md, .cursorrules)       │
│  Retrieval: None | Discretion: None | Reliability: Maximum       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WARM RULES                                  │
│  CLI call mandated by workflow step                              │
│  Example: `raise rules get --phase=design`                       │
│  Retrieval: Deterministic | Discretion: Timing only | Rel: High  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      COLD RULES                                  │
│  CLI call for specific contexts                                  │
│  Example: `raise rules get --for=security-review`                │
│  Retrieval: Deterministic | Discretion: Context-triggered | Med  │
└─────────────────────────────────────────────────────────────────┘
```

**The Graph's Role**: A semantic graph models rule relationships. The CLI queries this graph and returns a **complete, deterministic rule set**—not similarity-ranked results.

---

## Research Questions

For each question, I provide: the core question, required reasoning approach, specific sub-questions, and quality criteria for your output.

---

### 1. Reliability Engineering Patterns

**Core Question**: What architectural patterns from reliability engineering apply to deterministic rule delivery?

**Reasoning Approach**:
Draw from established reliability engineering disciplines (safety-critical systems, configuration management, formal methods). Map their patterns to our domain. Evaluate applicability critically.

**Investigate**:

1.1. **Mission-Critical Precedents**
- How do avionics systems handle configuration/rule delivery?
- How do medical device regulations (IEC 62304) approach configuration integrity?
- What patterns from industrial control systems (IEC 61508) apply?
- *For each: What's the pattern? What problem does it solve? How does it map to our domain?*

1.2. **Determinism Guarantees**
- What formal properties define "deterministic" in this context? (same input → same output, idempotency, referential transparency)
- How do we verify determinism? (property-based testing, formal verification, runtime assertions)
- What are the boundaries of determinism? (when is non-determinism acceptable or unavoidable?)

1.3. **Completeness Models**
- Closed-world assumption: What guarantees can we make if the rule graph is the complete universe?
- Open-world considerations: What happens with rules the graph doesn't know about?
- How do we handle "unknown unknowns" in a governance context?

1.4. **Graph-Based System Failure Modes**
- Stale graph state (graph doesn't reflect current rules)
- Missing edges (dependencies not modeled)
- Circular dependencies (infinite traversal)
- Inconsistent state (partial updates)
- *For each: Likelihood? Severity? Mitigation strategy?*

**Quality Criteria for This Section**:
- [ ] At least 3 concrete precedents from reliability engineering with explicit mapping to our domain
- [ ] Formal definition of "deterministic" with testable properties
- [ ] Completeness model with explicit assumptions stated
- [ ] Failure mode table with likelihood/severity/mitigation for each

**Target Length**: 1,500-2,000 words

---

### 2. Graph Schema Design

**Core Question**: What graph schema maximizes semantic expressiveness while guaranteeing retrieval reliability?

**Reasoning Approach**:
Compare schema options using explicit criteria. Don't just describe each—analyze trade-offs. Recommend with clear rationale.

**Investigate**:

2.1. **Schema Comparison**

Evaluate each against these criteria:
- **Expressiveness**: Can it model all required relationship types?
- **Query Reliability**: Are queries deterministic and efficient?
- **Tooling Maturity**: What's the ecosystem for validation, querying, visualization?
- **LLM Compatibility**: How well do LLMs parse/understand this format?
- **Maintenance Burden**: How hard is it to author and update?

| Schema Type | Evaluate |
|-------------|----------|
| Property Graphs (Neo4j-style) | Native relationship modeling, rich queries |
| RDF/OWL | Formal semantics, reasoning capabilities |
| JSON-LD | JSON compatibility, linked data |
| Simple DAG (JSON/YAML) | Minimal complexity, easy tooling |
| Custom DSL | Maximum control, maximum maintenance |

2.2. **Required Relationship Types**

For each relationship type, define:
- Semantics (what does it mean?)
- Transitivity (does A→B→C imply A→C?)
- Cardinality (one-to-one, one-to-many, many-to-many?)
- Query patterns (how is it used in retrieval?)

| Relationship | Purpose | Example |
|--------------|---------|---------|
| `requires` | Dependency | "SQL injection rule requires input validation rule" |
| `conflicts_with` | Mutual exclusion | "Strict mode conflicts with legacy mode" |
| `extends` | Inheritance/specialization | "React security extends frontend security" |
| `scoped_to_phase` | SDLC applicability | "Code review rules scoped to implementation" |
| `applies_when` | Conditional activation | "Applies when architecture=microservices" |
| `supersedes` | Version evolution | "Rule v2 supersedes rule v1" |

2.3. **Conditional Applicability**

Rules often apply conditionally. How do we model:
- Technology-specific rules (applies if using React)
- Architecture-specific rules (applies if microservices)
- Context-specific rules (applies if high-security project)
- Compound conditions (applies if React AND microservices AND high-security)

*Evaluate: Should conditions be in the graph schema or in a separate predicate system?*

2.4. **Versioning Strategy**

- How do rules evolve without breaking determinism?
- How do we handle: additions, modifications, deprecations, removals?
- What's the migration path when the graph schema itself changes?
- How do we maintain backwards compatibility for existing workflows?

**Quality Criteria for This Section**:
- [ ] Comparison matrix with explicit scores/rankings on each criterion
- [ ] Clear winner recommendation with confidence level and dissenting considerations
- [ ] Complete relationship type definitions with formal semantics
- [ ] Conditional applicability design with examples
- [ ] Versioning strategy with migration path

**Target Length**: 2,000-2,500 words

---

### 3. Dense Output Format for LLM Consumption

**Core Question**: How should retrieved rules be formatted to maximize LLM comprehension while minimizing token cost?

**Reasoning Approach**:
This is an empirical question. Where possible, reference benchmarks or studies. Where evidence is thin, reason from first principles about LLM behavior and state uncertainty clearly.

**Investigate**:

3.1. **Token Efficiency Analysis**

For the same semantic content (a rule with metadata, relationships, and content), measure/estimate token counts:

| Format | Tokens (est.) | Overhead vs. Minimum |
|--------|---------------|----------------------|
| Verbose JSON | ? | ? |
| Compact JSON | ? | ? |
| YAML | ? | ? |
| Markdown with frontmatter | ? | ? |
| Custom DSL | ? | ? |
| Plain text | ? | ? |

*Provide concrete examples showing the same rule in each format.*

3.2. **Semantic Preservation**

Which formats best preserve:
- Cross-references between rules (`@id` references, links)
- Hierarchical structure (sections, sub-rules)
- Metadata (phase, priority, version)
- Conditional logic (when clauses)

3.3. **LLM Parsing Reliability**

Based on known LLM behavior:
- Which formats are least prone to hallucination/misinterpretation?
- How do LLMs handle deeply nested structures vs. flat structures?
- What's the impact of format on instruction-following for the rules contained?

*Note: If empirical evidence is lacking, state assumptions clearly.*

3.4. **Compression Strategies**

Evaluate approaches for large rule sets:

| Strategy | Description | Trade-off |
|----------|-------------|-----------|
| Full inline | All rules fully expanded | Maximum clarity, maximum tokens |
| Schema reference | Define schema once, rules reference it | Reduced tokens, requires schema understanding |
| ID reference + lazy load | Return IDs, agent requests full content as needed | Minimum initial tokens, multiple round-trips |
| Hierarchical summary | Return summaries, expand on demand | Balanced, requires good summarization |

3.5. **Benchmark Estimates**

Estimate token loads for realistic systems:

| System Size | Full Inline | With Compression | Typical Context Budget |
|-------------|-------------|------------------|------------------------|
| 50 rules | ? | ? | 8K-32K |
| 100 rules | ? | ? | 32K-100K |
| 200 rules | ? | ? | 100K-200K |

**Quality Criteria for This Section**:
- [ ] Concrete token measurements or well-reasoned estimates with methodology stated
- [ ] Same-rule examples in at least 4 formats for direct comparison
- [ ] Clear format recommendation with rationale
- [ ] Compression strategy recommendation based on system size

**Target Length**: 1,500-2,000 words

---

### 4. CLI Interface Design

**Core Question**: What CLI interface design enforces reliable, predictable rule retrieval?

**Reasoning Approach**:
Design for reliability first, usability second. Every interface decision should have a clear rationale tied to reliability properties.

**Investigate**:

4.1. **Input Parameters**

What context must be provided for deterministic retrieval?

| Parameter | Required? | Purpose | Example |
|-----------|-----------|---------|---------|
| `--phase` | Yes | SDLC phase scoping | `design`, `implement`, `test` |
| `--command` | Yes | Spec-Kit command context | `specify`, `plan`, `tech-design` |
| `--context` | Optional | Additional filters | `--context=security,performance` |
| `--format` | Optional | Output format | `json`, `yaml`, `markdown` |
| `--include-deps` | Optional | Dependency expansion | `true` (default), `false` |

*For each: Why is it required/optional? What happens if omitted?*

4.2. **Output Contract**

Define the guarantees the CLI provides:

```
GIVEN: identical input parameters
AND: identical graph state (version/hash)
THEN: output is byte-identical

GIVEN: rule A is requested
AND: rule A requires rule B
THEN: output includes both A and B

GIVEN: rule A conflicts with rule B
AND: both would be retrieved
THEN: [define behavior: error? priority-based resolution? user prompt?]
```

4.3. **Error Handling Philosophy**

Two approaches:
- **Fail-explicit**: Any ambiguity or error stops execution with clear message
- **Default-safe**: System makes safe assumptions and continues with warnings

*Recommend one with rationale. For a reliability-focused system, which is more appropriate?*

4.4. **Caching and Staleness**

- Should the CLI cache results? (performance vs. freshness trade-off)
- How does the CLI know if the graph has changed?
- What's the invalidation strategy?
- Should the CLI include a graph version/hash in output for reproducibility?

4.5. **Command Reference**

Provide complete command specifications:

```bash
# Primary retrieval command
raise rules get --phase=<phase> --command=<command> [options]

# Validation/diagnostic commands
raise rules validate --rule=<id>      # Check rule integrity
raise rules graph --format=<format>   # Export full graph
raise rules deps --rule=<id>          # Show dependency tree
```

**Quality Criteria for This Section**:
- [ ] Complete parameter specification with rationale for each
- [ ] Formal output contract with testable properties
- [ ] Clear error handling philosophy with examples
- [ ] Caching strategy with invalidation logic
- [ ] Full command reference

**Target Length**: 1,200-1,500 words

---

### 5. SDLC Phase Mapping

**Core Question**: How should governance rules be scoped to SDLC phases for Spec-Kit integration?

**Reasoning Approach**:
Start from Spec-Kit's existing command structure. Map phases to rule categories. Define propagation logic clearly.

**Investigate**:

5.1. **Phase Taxonomy**

Define phases aligned with Spec-Kit commands:

| Phase | Spec-Kit Command | Description | Rule Categories |
|-------|------------------|-------------|-----------------|
| Specify | `/speckit.specify` | Requirements capture | Requirements rules, scope rules |
| Plan | `/speckit.plan` | Architecture/design planning | Design rules, architecture rules |
| Design | `/raise.tech-design` | Technical design | Implementation patterns, security design |
| Implement | `/speckit.implement` | Code writing | Coding standards, security coding |
| Test | (future) | Testing | Test coverage, test patterns |
| Deploy | (future) | Deployment | Deployment rules, operational rules |

5.2. **Rule Propagation**

Some rules span multiple phases. Define propagation semantics:

| Propagation Type | Semantics | Example |
|------------------|-----------|---------|
| **Cascade-down** | Rule applies to this phase and all subsequent | Security rules from Design cascade to Implement |
| **Phase-specific** | Rule applies only to this phase | "Spec must include user stories" only in Specify |
| **Transition** | Rule applies only when moving between phases | "Design review required before Implement" |
| **Cross-cutting** | Rule applies to all phases | "All artifacts must be in Git" |

5.3. **Inheritance and Override**

- Can phase-specific rules override cross-cutting rules?
- How do project-level rules interact with framework-level rules?
- What's the precedence order when rules conflict?

5.4. **Integration with Spec-Kit Commands**

For each Spec-Kit command, specify:
- Which phases it activates
- What rule query it triggers
- Where in the command prompt the rules are injected

**Quality Criteria for This Section**:
- [ ] Complete phase taxonomy aligned with Spec-Kit
- [ ] Propagation logic with formal semantics
- [ ] Precedence rules for conflicts
- [ ] Command-to-rule-query mapping

**Target Length**: 1,000-1,200 words

---

### 6. Comparative Analysis: Graph vs. Vector vs. Hybrid

**Core Question**: Is there a legitimate role for vector/semantic search in this architecture, or should it be fully deterministic?

**Reasoning Approach**:
Steel-man the vector approach before dismissing it. Identify legitimate use cases. Recommend with clear boundary conditions.

**Investigate**:

6.1. **Vector Search: Where It Excels**

Be fair to vector search. Where might it legitimately help?
- Rule discovery (finding rules you didn't know existed)
- Fuzzy matching (handling variant phrasings of the same concept)
- Similarity detection (finding related rules)

6.2. **Vector Search: Where It Fails for Governance**

Why is it problematic for our use case?
- Non-determinism (same query can yield different results)
- Incomplete retrieval (no dependency guarantees)
- Semantic drift (similar ≠ applicable)
- Auditability (why was this rule returned?)

6.3. **Hybrid Possibilities**

Could we use vectors for some purposes while keeping delivery deterministic?

| Component | Graph | Vector | Rationale |
|-----------|-------|--------|-----------|
| Rule delivery | ✓ | | Determinism required |
| Dependency resolution | ✓ | | Completeness required |
| Rule discovery/search | | ✓ | Exploration acceptable |
| Conflict detection | ✓ | | Consistency required |
| Rule authoring assistance | | ✓ | Suggestions acceptable |

6.4. **Decision Matrix**

| Criterion | Graph | Vector | Hybrid | Winner |
|-----------|-------|--------|--------|--------|
| Determinism | ✓✓✓ | ✗ | ✓✓ | Graph |
| Completeness guarantee | ✓✓✓ | ✗ | ✓✓ | Graph |
| Token efficiency | ✓✓ | ✓ | ✓✓ | Graph |
| Maintenance burden | ✓ | ✓✓✓ | ✓✓ | Vector |
| Discovery/exploration | ✗ | ✓✓✓ | ✓✓✓ | Vector/Hybrid |
| Auditability | ✓✓✓ | ✗ | ✓✓ | Graph |
| **Overall for Governance** | | | | ? |

6.5. **Recommendation with Boundary Conditions**

State your recommendation clearly:
- Primary recommendation
- Confidence level (high/medium/low)
- Conditions under which you would change this recommendation
- What evidence would falsify this recommendation

**Quality Criteria for This Section**:
- [ ] Fair treatment of vector search strengths
- [ ] Clear articulation of why vectors fail for governance
- [ ] Hybrid option evaluated honestly
- [ ] Decision matrix with explicit reasoning
- [ ] Recommendation with falsification conditions

**Target Length**: 1,200-1,500 words

---

## Output Structure

Organize your response as follows:

```
## Executive Summary (300-400 words)
- Key findings
- Primary recommendations
- Confidence levels
- Critical assumptions

## 1. Reliability Engineering Patterns
[1,500-2,000 words]

## 2. Graph Schema Design
[2,000-2,500 words]

## 3. Dense Output Format
[1,500-2,000 words]

## 4. CLI Interface Design
[1,200-1,500 words]

## 5. SDLC Phase Mapping
[1,000-1,200 words]

## 6. Comparative Analysis
[1,200-1,500 words]

## 7. Synthesis: The Complete Architecture
[800-1,000 words]
- How the pieces fit together
- Implementation priority order
- Open questions for future research

## Appendix A: Rule Object Examples
- Same rule in multiple formats
- Complete examples with all relationship types

## Appendix B: CLI Command Reference
- Full command specifications

## Appendix C: Glossary
- Terms used in this document
```

**Total Target Length**: 10,000-12,000 words

---

## Final Checklist

Before concluding, verify:

- [ ] Every recommendation has a stated confidence level
- [ ] Every recommendation has falsification conditions
- [ ] Trade-offs are explicit, not hidden
- [ ] Assumptions are stated, not implicit
- [ ] Evidence quality is characterized (established fact / inference / speculation)
- [ ] Failure modes are addressed for the recommended architecture
- [ ] The architecture is implementable with current technology
- [ ] The architecture scales to realistic rule counts (100-500 rules)
