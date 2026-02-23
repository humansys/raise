# Research Report: Architecture Review Heuristics

## Research Question

What architectural design principles are evaluable via code review with concrete heuristics and low false-positive rates? How do local (story) and systemic (epic) reviews differ methodologically?

## Decision Context

Design of `/rai-architecture-review` — a parametrized skill (`--scope story|epic`) that evaluates design principles (KISS, DRY, YAGNI, SOLID, cohesion/coupling) on code produced during RaiSE story/epic lifecycles.

---

## Key Findings

### Finding 1: Design Principles Map to Detectable Heuristics, Not Metrics

**Confidence: HIGH**

Design principles (KISS, YAGNI, DRY) are not directly measurable like cyclomatic complexity. They manifest as *code smells* — surface indicators of deeper problems. The canonical taxonomy (Fowler, S3) identifies 24 smells, of which a subset maps to architecture-level concerns:

| Principle | Smell Indicator | Detection Heuristic |
|-----------|----------------|---------------------|
| YAGNI | Speculative Generality | Abstract class with single implementation; unused parameters; methods used only by tests (S5) |
| YAGNI | Lazy Element | Class/function that doesn't justify its complexity cost (S4) |
| YAGNI | Dead Code | Unreachable code, unused exports (S4) |
| KISS | Middle Man | Class that delegates all work without adding value (S3) |
| KISS | Unnecessary Abstraction | Interface with one implementor, wrapper with no logic (S5) |
| DRY | Duplicated Code | Semantic duplication (same concept, different expression) — harder than textual (S3) |
| SRP | Divergent Change | One class modified for multiple unrelated reasons (S3) |
| SRP | Shotgun Surgery | One change requires modifying many classes (S3) |
| DIP | Feature Envy | Method uses more data from another class than its own (S3) |

**Evidence:** S3 (Fowler, Very High), S4 (Luzkan catalog, High), S5 (Refactoring Guru, High)

**Key insight:** These heuristics are *questions to ask*, not boolean checks. "Does this abstract class have only one implementation?" is verifiable. "Is this abstraction unnecessary?" requires judgment about future consumers.

### Finding 2: LLMs Are Good at Structural Smells, Weak at Design Smells

**Confidence: HIGH**

Empirical evidence (2024-2025) shows:
- LLMs achieve F1 0.85-0.88 on structural smells (Large Class, Long Method, Data Class) (S7)
- LLMs achieve F1 <0.40 on design smells requiring architectural understanding (Refused Bequest, Feature Envy) (S7)
- Specific prompts are 2.54x more effective than generic prompts for smell detection (S6)
- Ensemble (LLM + metric tools) outperforms LLM-only by 35% F1 increase (S8)

**Evidence:** S6 (Silva ESEM 2024, Very High), S7 (arxiv 2025, High), S8 (iSMELL ASE 2024, Very High)

**Implication for our skill:** Generic instructions like "check for YAGNI" will fail. The skill must provide:
1. **Concrete heuristics** (the questions to ask per principle)
2. **Architectural context** (what consumers exist, what the design intent is)
3. **Countable indicators** (number of implementations, import graph, export surface)

### Finding 3: Story-Level and Epic-Level Reviews Are Fundamentally Different Lenses

**Confidence: HIGH**

| Dimension | Story (Local) | Epic (Systemic) |
|-----------|--------------|-----------------|
| **Question** | "Did I build this the simplest way?" | "Is the whole simpler than the sum of parts?" |
| **Scope** | Files changed in story branch | Delta of entire epic vs base branch |
| **Smells detected** | Speculative Generality, Lazy Element, Middle Man | Cyclic Dependencies, Shotgun Surgery, Divergent Change |
| **Timing** | Post-implement, pre-review | Post last story, pre-epic-close |
| **Evidence type** | Local code inspection | Cross-module analysis, import graphs, pattern accumulation |

**Evidence:**
- Architecture reviews ask "will this design satisfy goals?" vs code reviews ask "does this implement its spec?" (S9, Medium)
- Cyclic dependencies grow complex over time through smell merging — early intervention critical (S15, Very High)
- Distributed code reviews cannot prevent systemic design failures; coupled microservices degrade regardless of individual code quality (S9)
- Coupling (CBO) is a reliable fault predictor; cohesion (LCOM) is NOT reliable (S11, Very High)

**Key insight:** Emergent problems (cyclic deps, coupling accumulation, abstraction orphaning) only become visible at epic scope. S211.0+S211.1's 18 subclasses + 5 Protocols without consumers is exactly this pattern — each story justified internally, the accumulation raises YAGNI flag.

### Finding 4: The Proportionality Principle Bridges KISS and YAGNI

**Confidence: MEDIUM**

Beck's Rule 4 ("Fewest elements") provides the falsifiable test: **if removing an element doesn't break rules 1-3 (tests, intent, duplication), it shouldn't exist** (S1, Very High).

This creates a hierarchy of review questions:
1. **Does it pass tests?** (automated, not our concern)
2. **Does it reveal intent?** (naming, structure clarity)
3. **Is there duplication?** (semantic, not just textual)
4. **Can any element be removed without violating 1-3?** (YAGNI test)

The proportionality question adds a nuance Beck doesn't address: **is the complexity proportional to the problem being solved?** An interface with one implementation isn't always wrong — but it needs justification (e.g., "consumers coming in S211.4"). Without that justification, it's Speculative Generality.

**Evidence:** S1 (Beck/Fowler, Very High), S2 (Rainsberger, High), S10 (Ford fitness functions, Very High)

**Disagreement:** Some practitioners argue that interfaces-before-implementation is always correct (SOLID adherents). Beck and Fowler's camp says this is Speculative Generality when no second implementation is planned. The evidence favors Beck: Ford's "Building Evolutionary Architectures" explicitly warns that "extra complexity for hypothetical flexibility usually makes systems harder to modify" (S10).

### Finding 5: A Practical Heuristic Set for LLM-Based Architecture Review

**Confidence: MEDIUM** (synthesized from evidence, not directly validated)

Based on findings 1-4, the following heuristics have the best signal-to-noise ratio for LLM-based review:

**Story-level (local, low false-positive):**

| # | Heuristic | Question | Red Flag | Principle |
|---|-----------|----------|----------|-----------|
| 1 | **Single Implementation** | Does any abstract class/Protocol have exactly one implementation? | Yes, with no documented future consumer | YAGNI |
| 2 | **Wrapper Without Logic** | Does any class delegate all work to another without adding behavior? | Pure pass-through with no transformation | KISS (Middle Man) |
| 3 | **Unused Parameters** | Are there parameters accepted but never used? | Parameter exists "for future use" | YAGNI |
| 4 | **Test-Only Consumers** | Is any public API used exclusively by tests? | Production code doesn't call it | YAGNI |
| 5 | **Proportionality** | Is the abstraction level proportional to the problem complexity? | 3-layer indirection for a 10-line operation | KISS |
| 6 | **Semantic Duplication** | Is the same concept expressed in multiple places with different code? | Two functions doing the same thing differently | DRY |
| 7 | **Responsibility Count** | Does any module change for more than one reason? | File modified in unrelated stories | SRP |

**Epic-level (systemic, requires cross-module view):**

| # | Heuristic | Question | Red Flag | Principle |
|---|-----------|----------|----------|-----------|
| 8 | **Orphaned Abstractions** | Did abstractions introduced early in the epic gain consumers by the end? | Protocol/Interface still has ≤1 implementor at epic close | YAGNI |
| 9 | **Coupling Direction** | Do dependencies flow toward stable modules? | Stable module imports from volatile module | DIP |
| 10 | **Cyclic Dependencies** | Are there circular import paths between modules? | A→B→C→A | Acyclic Dependencies |
| 11 | **Shotgun Surgery Pattern** | Does one logical change require modifying many files across modules? | Adding a new parser type touches 5+ files | OCP |
| 12 | **Pattern Duplication** | Did separate stories introduce similar patterns that should be consolidated? | Two modules solve the same structural problem differently | DRY |
| 13 | **Export Surface Growth** | Did `__all__` grow proportionally to functionality, or faster? | Public API grew 3x while behavior grew 1.5x | Interface Segregation |
| 14 | **Abstraction Justification** | Can every abstraction layer justify its existence via a consumer? | Layer exists because "it's the right pattern" but nothing uses it | YAGNI/KISS |

**Heuristics 1, 2, 5, 8, 14** are highest-value based on evidence: they map to well-documented smells (Speculative Generality, Middle Man, Lazy Element) with concrete indicators. Heuristics 10, 11 have strong empirical support for fault prediction (S11, S15).

### Finding 6: False Positive Mitigation Requires Context, Not Just Rules

**Confidence: HIGH**

The primary risk is false positives — flagging intentional design decisions as violations. Evidence shows:

- LLM smell detection with generic prompts: ~48% false positive rate (S6)
- LLM smell detection with specific prompts: ~35% false positive rate (S6)
- Ensemble (LLM + tools): ~25% false positive rate (S8)

**Mitigation strategies:**
1. **Require justification, don't auto-reject.** Finding: "Protocol X has one implementation" → Ask: "Is a second implementation planned and when?" — not "Remove Protocol X."
2. **Use story/epic scope context.** The skill knows the design doc and plan — use them to distinguish intentional from accidental.
3. **Severity tiers.** Not all findings are equal. "Cyclic dependency" is always a problem. "Single implementation" might be intentional with documented justification.
4. **The "next story" test.** At epic scope: "If S211.3 is the last story and Protocol X still has one implementation, flag it. If S211.3 specifically plans to add consumers, defer."

**Evidence:** S6 (prompt specificity, Very High), S8 (ensemble approach, Very High), S12 (Google: review as communication, Very High)

---

## Patterns & Insights

### The Two Lenses Are Complementary, Not Redundant

Quality review (existing `/rai-quality-review`) asks: "Is this code **correct**?"
Architecture review asks: "Is this code **necessary and proportional**?"

These are orthogonal concerns. A perfectly correct, well-tested, type-safe class can still be YAGNI. A simple, proportional design can still have a semantic bug. One doesn't subsume the other.

### The Beck Hierarchy as Universal Framework

Beck's four rules provide the evaluation framework that unifies all principles:
- KISS = Rule 4 (fewest elements)
- YAGNI = Rule 4 + Rule 1 (if no test needs it, why does it exist?)
- DRY = Rule 3 (no duplication)
- Reveals Intent = Rule 2
- SOLID principles are refinements of Rules 2-4 in OOP context

This means the skill doesn't need separate checklists per principle — it needs Beck's hierarchy applied at two zoom levels.

### Fitness Functions Are the Automated Complement

Architecture fitness functions (Ford, S10) automate what can be automated: cyclic dependency detection, coupling metrics, layer violations. Our skill is the inference complement — it catches what metrics miss: **intent, justification, proportionality.** Together they form a complete architecture governance layer.

---

## Gaps & Unknowns

1. **No empirical validation of LLM-based YAGNI detection.** Speculative Generality has no benchmark dataset (S13). Our heuristics are evidence-informed but not empirically validated at scale.

2. **Python-specific tooling gap.** No ArchUnit equivalent for Python. Import analysis (pydeps, pyan3) exists but requires manual interpretation. Our skill fills this gap with LLM inference.

3. **Proportionality is subjective.** "Is this abstraction proportional?" has no metric. It requires judgment informed by context (design docs, planned consumers, project stage). This is where the LLM adds value — and where false positives will concentrate.

4. **Epic-level review at scale.** Our evidence comes from small-to-medium codebases. At large scale (100+ files per epic), the LLM context window becomes a constraint. May need sampling strategies.

---

## Recommendation

**Decision:** Create `/rai-architecture-review` as a single parametrized skill with `--scope story|epic`.

**Confidence: HIGH**

**Rationale:**
1. The evidence clearly distinguishes local vs systemic review as different lenses on the same concern (Finding 3)
2. The heuristics are concrete enough for specific prompts, which evidence shows are 2.54x more effective than generic (Finding 2, S6)
3. Beck's four rules provide a unified framework that avoids principle-by-principle checklists (Pattern: Beck Hierarchy)
4. The skill complements, not replaces, both `/rai-quality-review` (correctness) and fitness functions (metrics)

**Structure:**
- **Story scope:** Heuristics 1-7 (local, per-file)
- **Epic scope:** Heuristics 8-14 (systemic, cross-module) + re-evaluate story findings in accumulation
- **Output format:** Same as quality-review (Critical / Recommended / Observations / Verdict) for consistency
- **False positive mitigation:** Require justification questions, not auto-rejection. Use design doc context.

**Trade-offs:**
- Accepts that proportionality judgment will have ~30% false positive rate (mitigated by asking instead of asserting)
- Does not replace automated fitness functions (complementary, not competitive)
- Epic-level review may hit context limits on large epics (mitigate with file prioritization)

**Risks:**
1. False positives erode trust → Mitigate with conservative tone ("question" not "finding")
2. Overlap with quality-review → Clear boundary: correctness (quality) vs proportionality (architecture)
3. YAGNI on the skill itself → Validate with S211.3 before formalizing

**Next step:** Design the skill using this evidence catalog as foundation. Run first on S211.0-S211.2 retroactively to calibrate false positive rate before embedding in lifecycle.
