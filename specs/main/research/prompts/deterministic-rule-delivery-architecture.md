# Deep Research: Deterministic Rule Delivery Architecture for Governance-as-Code

**Role**: Senior Systems Architect specializing in AI Governance and Reliability Engineering
**Objective**: Design a **maximally reliable** rule delivery system for CLI-based AI coding agents, where "reliable" means: predictable, complete, and verifiable.

## Context: The Problem We're Solving

Current AI coding assistants (Cursor, Copilot, Claude Code) suffer from **model-selected rule application**—the agent decides which rules to apply and when. This introduces unacceptable variability for governance-critical workflows.

**Observed failure modes** (to be validated/expanded by research):
- Agent ignores rules it has access to
- Agent applies rules inconsistently across similar contexts
- Agent fails to recognize when a rule's prerequisites apply
- Agent retrieves semantically similar but incorrect rules (vector search drift)

**Design constraint**: Remove model discretion from rule selection. The system determines WHAT rules apply; the agent's job is to APPLY them.

## The Proposed Architecture (To Be Validated & Refined)

### Three-Tier Rule System

| Tier | Mechanism | Retrieval | Example |
|------|-----------|-----------|---------|
| **HOT** | IDE-native static files | None (always in context) | CLAUDE.md, .cursorrules |
| **WARM** | CLI call mandated by workflow | Deterministic, phase-scoped | `raise rules get --phase=design` |
| **COLD** | CLI call for specific contexts | Deterministic, context-triggered | `raise rules get --for=security-review` |

### The Graph's Role

A semantic graph models rule relationships (dependencies, conflicts, phase-applicability). The CLI queries this graph and returns a **dense, complete rule set**—not similarity-ranked results.

**Determinism sources**:
1. **Timing**: Workflow prompts mandate when CLI is called (not model choice)
2. **Selection**: Graph traversal returns exact rules for context (not probabilistic ranking)

---

## Research Questions (Investigate, Don't Presuppose)

### 1. Reliability Engineering for Rule Delivery

**Primary question**: What architectural patterns maximize reliability in deterministic rule delivery systems?

Investigate:
- How do mission-critical systems (avionics, medical devices) handle configuration/rule delivery?
- What verification mechanisms ensure "same input → same output" over time?
- How is "completeness" defined and tested in closed-world vs. open-world systems?
- What are the failure modes of graph-based systems? (stale graphs, missing edges, circular dependencies)

**Deliverable**: A reliability model with testable properties (e.g., idempotency, determinism, completeness guarantees).

### 2. Graph Schema Design for Governance Rules

**Primary question**: What graph schema maximizes both semantic expressiveness and retrieval reliability?

Investigate:
- Compare: Property Graphs vs. RDF/OWL vs. JSON-LD vs. simpler DAG structures
- What relationship types are essential? (`requires`, `conflicts_with`, `extends`, `scoped_to_phase`, `applies_when`)
- How to handle conditional applicability (e.g., "applies if microservices architecture")?
- How to version the graph and handle rule evolution without breaking determinism?

**Deliverable**: A recommended schema with formal relationship definitions and example rule objects.

### 3. Dense Output Format for LLM Consumption

**Primary question**: How should retrieved rules be formatted to maximize LLM comprehension while minimizing token cost?

Investigate:
- Token efficiency: Compare JSON vs. YAML vs. Markdown vs. custom DSL for the same rule set
- Semantic density: Which formats preserve cross-references and hierarchy best?
- LLM parsing reliability: Which formats are least prone to misinterpretation?
- Compression strategies: Schema-reference vs. inline expansion vs. lazy loading

**Deliverable**: A recommended output format with benchmarks (tokens per rule, parsing accuracy).

### 4. CLI Interface Design

**Primary question**: What CLI interface design enforces reliable, predictable rule retrieval?

Investigate:
- Input parameters: What context must be provided? (phase, command, file types, explicit flags)
- Output guarantees: What contract does the CLI provide? (completeness, ordering, conflict resolution)
- Error handling: What happens on ambiguous input? Fail-explicit vs. default-safe?
- Caching/staleness: How to ensure retrieved rules reflect current graph state?

**Deliverable**: CLI command specification with input/output contracts.

### 5. SDLC Phase Mapping

**Primary question**: How should governance rules be scoped to SDLC phases for Spec-Kit integration?

Investigate:
- Define a phase taxonomy compatible with Spec-Kit commands (specify, plan, implement, test, deploy)
- How do rules propagate across phases? (e.g., security rules from design → implementation)
- How to handle phase-transition rules (apply only when moving from X to Y)?

**Deliverable**: Phase-rule matrix with propagation logic.

### 6. Comparative Analysis: Where (If Anywhere) Do Vectors Belong?

**Primary question**: Is there a legitimate role for vector/semantic search in this architecture, or should it be fully deterministic?

Investigate:
- Could vectors help with *discovery* (finding relevant rules to add to the graph) while graph handles *delivery*?
- Are there edge cases where fuzzy matching is genuinely needed?
- What is the reliability cost of introducing any probabilistic component?

**Deliverable**: Decision matrix with clear recommendation and boundary conditions.

---

## Required Output: Architecture Specification

Produce a technical report (~8,000 words) containing:

1. **Reliability Model**
   - Testable properties the system must satisfy
   - Failure modes and mitigations
   - Verification/testing strategy

2. **Graph Schema Specification**
   - Recommended format with rationale
   - Formal relationship type definitions
   - Code samples of rule objects
   - Versioning and migration strategy

3. **Dense Output Format Specification**
   - Recommended format with benchmarks
   - Token cost analysis for 50/100/200 rule systems
   - Example outputs for different retrieval contexts

4. **CLI Interface Specification**
   - Command reference with parameters
   - Input/output contracts
   - Error handling behavior

5. **SDLC Phase Matrix**
   - Phase-to-rule-category mapping
   - Propagation rules
   - Spec-Kit command integration

6. **Architectural Decision Record**
   - Graph vs. Vector vs. Hybrid: Final recommendation with evidence
   - Trade-offs acknowledged
   - Conditions under which recommendation should be revisited

---

## Research Methodology Constraints

- **No confirmation bias**: Investigate failure modes of the proposed architecture as rigorously as alternatives
- **Evidence-based**: Cite prior art, case studies, or benchmarks—not just theoretical arguments
- **Actionable**: Every recommendation must be implementable with current technology
- **Falsifiable**: State conditions under which each recommendation would be wrong
