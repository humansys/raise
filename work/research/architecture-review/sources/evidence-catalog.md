# Evidence Catalog: Architecture Review Heuristics

## Research Question
What architectural design principles are evaluable via code review with concrete heuristics and low false-positive rates? How do local (story) and systemic (epic) reviews differ methodologically?

---

## Sources

### S1: Beck Design Rules (Fowler interpretation)
- **Source**: [Beck Design Rules](https://martinfowler.com/bliki/BeckDesignRules.html)
- **Type**: Primary (practitioner-originated, widely cited)
- **Evidence Level**: Very High
- **Key Finding**: Four rules in priority order: passes tests > reveals intention > no duplication > fewest elements. Rule 4 directly maps to YAGNI.
- **Relevance**: The canonical minimalist design framework. "Fewest elements" is the falsifiable heuristic for YAGNI: if removing an element doesn't violate rules 1-3, it shouldn't exist.

### S2: J.B. Rainsberger — Four Elements of Simple Design
- **Source**: [The Four Elements of Simple Design](https://blog.jbrains.ca/permalink/the-four-elements-of-simple-design)
- **Type**: Secondary (practitioner synthesis)
- **Evidence Level**: High
- **Key Finding**: Reframes Beck's rules as: tests pass, removes duplication, reveals intent, has fewest elements. Argues rules 2 and 3 are synergistic — removing duplication often reveals intent.
- **Relevance**: Provides the insight that DRY and clarity reinforce each other, suggesting a combined heuristic rather than separate checks.

### S3: Fowler — Code Smells (Refactoring, 2nd ed.)
- **Source**: [Code Smell (bliki)](https://martinfowler.com/bliki/CodeSmell.html) + Refactoring (2018)
- **Type**: Primary (foundational text)
- **Evidence Level**: Very High
- **Key Finding**: 24 code smells cataloged. Architecture-relevant subset: Speculative Generality, Lazy Element, Shotgun Surgery, Divergent Change, Feature Envy, Middle Man. Smells are "surface indications of deeper problems."
- **Relevance**: Establishes that design smells are heuristic indicators, not metrics. Subjectivity is inherent — experienced reviewers "sniff" them.

### S4: Code Smells Catalog (Luzkan)
- **Source**: [Code Smells Catalog](https://luzkan.github.io/smells/)
- **Type**: Secondary (comprehensive catalog)
- **Evidence Level**: High
- **Key Finding**: Maps smells to categories. Architecture-relevant "Unnecessary Complexity" smells: Speculative Generality, Dead Code, Lazy Element. Each has detection heuristics.
- **Relevance**: Provides structured taxonomy. Speculative Generality = "abstractions based on speculated requirements." Lazy Element = "does not do enough to pay for itself."

### S5: Speculative Generality (Refactoring Guru)
- **Source**: [Speculative Generality](https://refactoring.guru/smells/speculative-generality)
- **Type**: Secondary (practitioner reference)
- **Evidence Level**: High
- **Key Finding**: Concrete indicators: abstract class used by only one subclass, unused method parameters, methods whose only users are test cases. Refactorings: Collapse Hierarchy, Inline Function, Remove Dead Code.
- **Relevance**: Most directly maps to YAGNI review. The "only one implementation" heuristic is mechanically detectable with low false-positive risk.

### S6: Silva et al. — Detecting Code Smells using ChatGPT (ESEM 2024)
- **Source**: [ESEM 2024](https://dl.acm.org/doi/10.1145/3674805.3690742)
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: ChatGPT with specific prompts: F-measure 0.52 (critical severity), 0.43 (minor). Specific prompts 2.54x more effective than generic. Failed completely on Blob detection (0% correct). Better on Data Class.
- **Relevance**: Validates that LLM code smell detection requires highly specific prompts. Generic "check for YAGNI" will fail. Need concrete heuristics in the prompt.

### S7: LLM Code Smell Detection — Beyond Strict Rules (2025)
- **Source**: [arxiv 2601.09873](https://arxiv.org/html/2601.09873)
- **Type**: Primary (peer-reviewed preprint)
- **Evidence Level**: High
- **Key Finding**: 4 LLMs on 9 smells. Strong on structural smells (Large Class F1=0.88, Long Method F1=0.87). Weak on design smells (Refused Bequest <0.40, Feature Envy variable). LLMs outperformed rule-based tools on 6/9 smells.
- **Relevance**: Critical finding: LLMs are good at structural smells but struggle with smells requiring "deeper understanding of architectural intent." Our architecture review skill must provide that architectural context explicitly.

### S8: iSMELL — Ensemble LLM + Tools (ASE 2024)
- **Source**: [ASE 2024](https://conf.researchr.org/details/ase-2024/ase-2024-research/108/)
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: Ensemble approach (LLM + 7 expert toolsets) achieved F1 75.17%, outperforming LLM-only by 35% increase. Best results when LLM provides reasoning and tools provide metrics.
- **Relevance**: Validates hybrid approach: LLM does the reasoning/judgment, concrete metrics provide grounding. Our skill should combine LLM review with countable heuristics.

### S9: Architecture vs Implementation Reviews
- **Source**: [Arguing with Algorithms](https://www.arguingwithalgorithms.com/posts/14-12-02-architecture-reviews.html)
- **Type**: Tertiary (practitioner blog)
- **Evidence Level**: Medium
- **Key Finding**: Architecture reviews ask "will this design satisfy business goals?" vs implementation reviews ask "does this code meet its spec?" Architectural changes require different reviewers (system thinkers, not detail checkers). Early review prevents costly restructuring.
- **Relevance**: Confirms our intuition that story-level and epic-level reviews are fundamentally different lenses, not just different scopes.

### S10: Neal Ford — Architecture Fitness Functions
- **Source**: [Building Evolutionary Architectures](https://fundamentalsofsoftwarearchitecture.com/)
- **Type**: Primary (book, widely cited)
- **Evidence Level**: Very High
- **Key Finding**: Fitness functions = automated architecture governance. Examples: cyclic dependency detection, layer violation checks, coupling metrics. Can be wired into CI. ArchUnit (Java) and equivalents enforce rules as tests.
- **Relevance**: The gold standard for automated architecture review. Our skill is the LLM-inference complement to fitness functions — catches what metrics miss (intent, justification, proportionality).

### S11: Cohesion/Coupling Metrics — Empirical Validation
- **Source**: [Springer: LCOM/CBO empirical](https://link.springer.com/article/10.1007/s10664-017-9535-z)
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: CBO (coupling) is a good predictor of fault-proneness. LCOM (cohesion) is NOT a reliable predictor — results are inconsistent across studies. High coupling correlates with low cohesion.
- **Relevance**: Coupling metrics are reliable; cohesion metrics are not. Our heuristics should focus on coupling indicators (import graphs, dependency direction) over cohesion metrics.

### S12: Google — Software Engineering at Google
- **Source**: [SE at Google](https://www.oreilly.com/library/view/software-engineering-at/9781492082781/)
- **Type**: Primary (book, industry leader)
- **Evidence Level**: Very High
- **Key Finding**: Code review is "not primarily about defect detection — it's a communication exercise." Requires LGTM (correctness) + OWNER approval (belongs here). Emphasizes readability and maintainability over catching bugs.
- **Relevance**: Reinforces that architecture review is about communication of intent and proportionality, not defect hunting. Different concern than quality-review.

### S13: Systematic Literature Review — Code Smell Datasets (ACM 2023)
- **Source**: [ACM Computing Surveys](https://dl.acm.org/doi/10.1145/3596908)
- **Type**: Primary (peer-reviewed SLR)
- **Evidence Level**: Very High
- **Key Finding**: Most datasets support God Class, Long Method, Feature Envy. 6 of Fowler's smells have NO dataset support. Datasets suffer from imbalanced samples and are restricted to Java. Tool precision varies heavily by dataset.
- **Relevance**: Speculative Generality and Lazy Element (our key YAGNI indicators) likely have no benchmark datasets. We cannot rely on tool precision numbers for these — must use heuristic judgment.

### S14: Python Cohesion/Coupling Measurement
- **Source**: [Caterbum: Python Metrics](https://www.caterbum.com/blog/measuring-cohesion-and-coupling-in-python-codebases-practical-metrics-kpis-and-an-implementation-plan)
- **Type**: Tertiary (practitioner guide)
- **Evidence Level**: Medium
- **Key Finding**: Python-specific metrics: efferent coupling (Ce, outgoing deps), afferent coupling (Ca, incoming deps). Tools: pydeps (dependency graphs), pyan3 (call graphs). No Python ArchUnit equivalent exists.
- **Relevance**: Provides concrete Python tooling we could reference. Import analysis is the most practical coupling indicator for Python.

### S15: Architectural Smells Evolution (Empirical SE 2022)
- **Source**: [Springer: AS Evolution](https://link.springer.com/article/10.1007/s10664-022-10132-7)
- **Type**: Primary (peer-reviewed)
- **Evidence Level**: Very High
- **Key Finding**: Cyclic dependencies grow increasingly complex over time through smell merging. Hub-like dependencies remain stable. Unstable dependencies grow slowly. Early intervention is critical for cyclic deps.
- **Relevance**: Validates that epic-level review catches accumulation patterns that story-level misses. Cyclic dependencies are emergent — they form across stories.

---

## Summary Statistics
- Total sources: 15
- Primary (peer-reviewed/foundational): 9
- Secondary (expert synthesis): 3
- Tertiary (practitioner guides): 3
- Evidence levels: Very High (8), High (4), Medium (3)
