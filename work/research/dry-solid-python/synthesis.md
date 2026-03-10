# Synthesis: DRY and SOLID Principles in Python

> Research ID: DRY-SOLID-PYTHON-20260205
> Based on 28 sources (7 Very High, 10 High, 6 Medium, 2 Low evidence)

---

## Major Claims (Triangulated)

### Claim 1: The Rule of Three Should Guide DRY Application

**Statement**: Wait until code is duplicated THREE times before creating an abstraction. The first two instances reveal different aspects; only by the third can you see the true pattern.

**Confidence**: HIGH

**Evidence**:
1. [Sandi Metz - The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) - "Duplication is far cheaper than the wrong abstraction"
2. [Incus Data - Refactoring and Rule of Three](https://incusdata.com/blog/refactoring-the-rule-of-three) - "Wait until code is repeated at least three times before abstracting"
3. [Los Techies - Abstraction: The Rule of Three](https://lostechies.com/derickbailey/2012/10/31/abstraction-the-rule-of-three/) - "First time: just implement. Second time: let it be. Third time: NOW consider abstraction"
4. [Understanding Legacy Code](https://understandlegacycode.com/blog/refactoring-rule-of-three/) - "Focus on meaning, not syntax; only abstract when code represents the SAME concept"

**Disagreement**: None found. This principle has strong consensus across sources spanning 2012-2025.

**Implication for raise-cli**: Before extracting a utility function or creating an abstract base class, verify the pattern appears 3+ times AND represents the same semantic concept.

---

### Claim 2: Semantic Duplication Matters More Than Syntactic Duplication

**Statement**: Only abstract duplicated code when it represents the SAME business concept. Code that looks identical but serves different purposes should remain separate.

**Confidence**: HIGH

**Evidence**:
1. [Understanding Legacy Code](https://understandlegacycode.com/blog/refactoring-rule-of-three/) - "Identify shared meaning, not shared syntax"
2. [Sandi Metz - The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) - "Once an abstraction is proved wrong, re-introduce duplication and let it show you what's right"
3. [Avoiding Premature Software Abstractions](https://betterprogramming.pub/avoiding-premature-software-abstractions-8ba2e990930a) - "Only add abstractions when solving a real (not theoretical) problem"

**Disagreement**: None found.

**Implication for raise-cli**: Two validators that happen to share similar code structure but validate different domain concepts (e.g., kata validation vs component validation) should NOT be unified just because the code looks similar.

---

### Claim 3: Python's SOLID Implementation Is Lighter Than Java's

**Statement**: Python's dynamic nature (duck typing, first-class functions, protocols) allows SOLID principles to be achieved with less ceremony than statically-typed languages.

**Confidence**: HIGH

**Evidence**:
1. [Real Python - SOLID Design Principles](https://realpython.com/solid-principles-python/) - "Python's dynamic nature means ISP naturally handled through duck typing"
2. [ResearchGate - SOLID Python](https://www.researchgate.net/publication/323935872_SOLID_Python_SOLID_principles_applied_to_a_dynamic_programming_language) - "Dynamic languages reduce SOLID implementation complexity but principles still apply"
3. [A Pythonic Guide to SOLID](https://dev.to/ezzy1337/a-pythonic-guide-to-solid-design-principles-4c8i) - "Python doesn't need interfaces for polymorphism"
4. [PEP 544 - Protocols](https://peps.python.org/pep-0544/) - Structural subtyping without explicit interface inheritance

**Disagreement**: Some sources (primarily from Java backgrounds) still advocate for explicit ABC usage. However, Python community consensus favors lighter approaches.

**Implication for raise-cli**: Avoid creating abstract base classes just because "Java would do it that way." Use Protocols for type checking, duck typing for runtime flexibility.

---

### Claim 4: Composition Should Be the Default; Inheritance for Genuine "Is-A"

**Statement**: Prefer composition over inheritance. Reserve inheritance for clear "is-a" relationships where behavior genuinely needs to be shared and specialized.

**Confidence**: HIGH

**Evidence**:
1. [Python Patterns - Composition Over Inheritance](https://python-patterns.guide/gang-of-four/composition-over-inheritance/) - "Design principles like Composition Over Inheritance are more important than individual patterns"
2. [Real Python - Inheritance and Composition](https://realpython.com/inheritance-composition-python/) - "Use inheritance for 'is-a' when behavior needs sharing; composition for 'has-a' and modularity"
3. [Philip Mutua - Composition in Python](https://medium.com/@philip.mutua/why-i-prefer-composition-over-inheritance-in-python-a-practical-guide-f9fddd4aa72f) - "Composition promotes loose coupling; components can be swapped without affecting the system"

**Disagreement**: None found for Python. Some OOP purists advocate inheritance, but Python community consensus strongly favors composition.

**Implication for raise-cli**: The existing pattern of injecting dependencies (extractors, formatters) via composition is correct. Avoid creating deep inheritance hierarchies.

---

### Claim 5: Protocols Are More Pythonic Than ABCs for Most Use Cases

**Statement**: Use Protocols (structural subtyping) for type hints and static checking. Use ABCs only when runtime enforcement of interface compliance is critical.

**Confidence**: HIGH

**Evidence**:
1. [PEP 544 - Protocols](https://peps.python.org/pep-0544/) - "Protocols enable 'static duck typing'"
2. [Justin Ellis - ABCs vs Protocols](https://jellis18.github.io/post/2022-01-11-abc-vs-protocol/) - "Use ABC for runtime enforcement; use Protocol for static checking; Protocol is more Pythonic"
3. [Real Python - Duck Typing](https://realpython.com/duck-typing-python/) - "Duck typing is Python's default; formal interfaces are optional optimizations"

**Disagreement**: ABCs still valuable when you need to prevent instantiation of incomplete classes or enforce method implementation at class definition time.

**Implication for raise-cli**: Use `Protocol` from `typing` for defining interfaces (like `Extractor`, `Formatter`). Reserve ABC for cases where incomplete implementations would cause runtime errors.

---

### Claim 6: Simple Dependency Injection Beats Framework DI in Python

**Statement**: Constructor injection with a composition root is sufficient for most Python applications. DI frameworks add complexity without proportional benefit.

**Confidence**: MEDIUM

**Evidence**:
1. [Medium - DI Without Framework](https://medium.com/the-pythonworld/how-i-use-dependency-injection-in-python-without-a-framework-69bbd24cbedc) - "Constructor injection + composition root pattern; no framework needed"
2. [DataCamp - Python DI Guide](https://www.datacamp.com/tutorial/python-dependency-injection) - "DI complexity in Python is lower than other languages; frameworks optional"

**Disagreement**: Large applications (Django, enterprise systems) may benefit from DI containers for managing complex dependency graphs. However, CLI tools rarely reach this complexity.

**Implication for raise-cli**: Continue using constructor injection. Create dependencies in `main.py` or CLI entry points. Avoid DI frameworks like `dependency-injector` unless complexity genuinely warrants it.

---

### Claim 7: SRP Applies at Module, Class, and Function Levels

**Statement**: Single Responsibility Principle should be applied consistently: modules have one domain, classes have one reason to change, functions have one task.

**Confidence**: HIGH

**Evidence**:
1. [PythonTutorial.net - SRP](https://www.pythontutorial.net/python-oop/python-single-responsibility-principle/) - "If you can't describe function purpose without 'and', split it"
2. [Real Python - SOLID](https://realpython.com/solid-principles-python/) - "Responsibility isn't directly tied to number of methods but to core task"
3. [Refactoring Guru - God Object](https://softwarepatternslexicon.com/patterns-python/11/2/4/) - "Split God Objects incrementally using Extract Class"

**Disagreement**: None found.

**Implication for raise-cli**:
- Module level: Each module in `governance/` has clear responsibility (extraction, graph, query)
- Class level: Classes like `ConceptExtractor` should only extract, not format or persist
- Function level: If describing a function requires "and", extract a helper

---

### Claim 8: Premature Abstraction Has Compounding Costs

**Statement**: Wrong abstractions get worse over time as developers try to bend them to fit new use cases rather than removing them. The cost compounds.

**Confidence**: HIGH

**Evidence**:
1. [Sandi Metz - The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) - "Programmer feels honor-bound to retain existing abstraction... alters code to take parameter and add logic"
2. [Codeling - Premature Abstraction](https://codeling.dev/blog/premature-abstraction-in-software-engineering/) - "Red flag: abstraction checks numerous input cases"
3. [Post-Architecture - Premature Abstraction](https://arendjr.nl/blog/2024/07/post-architecture-premature-abstraction-is-the-root-of-all-evil/) - "Leads to wasted effort, increased complexity, reduced flexibility, slower development"

**Disagreement**: None found.

**Implication for raise-cli**: When an abstraction starts accumulating special cases or conditional branches, consider REMOVING it and re-introducing duplication. Then re-evaluate if abstraction is still warranted.

---

### Claim 9: Parameter Objects Should Eventually Own Behavior

**Statement**: When introducing a parameter object (dataclass grouping related parameters), it should eventually gain methods related to its data. Pure data containers are a stepping stone, not the end state.

**Confidence**: MEDIUM

**Evidence**:
1. [Refactoring Guru - Introduce Parameter Object](https://refactoring.guru/introduce-parameter-object) - "Parameter Objects should eventually own logic related to their data"
2. [Refactoring.com - Parameter Object](https://refactoring.com/catalog/introduceParameterObject.html) - "You may discover a new object that was hiding in plain sight"

**Disagreement**: Some advocate for strict separation of data and behavior (functional style). In Python, this is a valid alternative pattern.

**Implication for raise-cli**: Pydantic models like `KataContext` or `ComponentInfo` can have methods. If validation or transformation logic is repeated elsewhere, consider moving it to the model.

---

### Claim 10: Python's Zen Supports Pragmatism Over Purity

**Statement**: "Practicality beats purity" and "Simple is better than complex" should guide when to apply design principles. Dogmatic adherence to any principle (including DRY/SOLID) can be counterproductive.

**Confidence**: HIGH

**Evidence**:
1. [PEP 20 - Zen of Python](https://peps.python.org/pep-0020/) - "Simple is better than complex. Practicality beats purity."
2. [Fluent Python - Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) - "Pythonic patterns differ from Java patterns; functions as first-class objects change design"
3. [DEV - Pragmatic Clean Code](https://dev.to/climentea/a-pragmatic-approach-on-writing-clean-code-1lm3) - "A great developer should have good judgment for reaching compromises between code quality and customer value"

**Disagreement**: None found. Even Clean Code advocates acknowledge context matters.

**Implication for raise-cli**: If a "clean code" refactoring makes the code harder to understand or adds complexity without clear benefit, don't do it. Readability counts.

---

## Patterns and Paradigm Shifts

### Pattern 1: AHA over DRY
The industry is shifting from "always DRY" to "Avoid Hasty Abstractions" (AHA). This recognizes that:
- Duplication has a known, bounded cost
- Wrong abstractions have unbounded, compounding cost
- The cure (abstraction) can be worse than the disease (duplication)

### Pattern 2: Protocols over ABCs
Python 3.8+ introduced Protocols (PEP 544), shifting the community toward structural subtyping:
- No need to inherit from abstract classes
- Type checkers verify structure, not ancestry
- More Pythonic, less Java-like

### Pattern 3: Composition Containers
Modern Python patterns favor "composition containers" - small classes that compose behaviors rather than inherit them:
- Strategy pattern via constructor injection
- Decorator pattern via function wrappers
- Adapter pattern via composition, not inheritance

### Pattern 4: Functions as First-Class Design Elements
Python's first-class functions reduce need for class-based patterns:
- Strategy pattern: Just pass a function
- Command pattern: Functions with closures
- Factory pattern: Simple factory functions

---

## Gaps and Unknowns

### Gap 1: Quantitative Data on Abstraction Timing
While "rule of three" is widely accepted, no empirical study validates whether 3 is optimal vs 2 or 4. This is accepted wisdom, not measured science.

### Gap 2: CLI-Specific Patterns
Most SOLID/DRY literature focuses on web applications or enterprise software. Limited research specifically addresses CLI tool architecture patterns.

### Gap 3: Type Hints Impact on Design
How Python's gradual typing (via type hints) should influence design decisions is still evolving. The Protocol/ABC choice is clear, but broader impact on composition vs inheritance is less documented.

### Gap 4: AI-Assisted Development Context
With AI code generation becoming common, the traditional refactoring patterns may need revision. AI can generate boilerplate, reducing duplication cost.

---

## Key Insights for CLI Codebases

1. **Flat is better than nested**: CLI tools should have shallow hierarchies. Deep inheritance is a smell.

2. **Entry points as composition roots**: `main.py` or CLI command handlers are natural places to wire dependencies.

3. **Pydantic models as domain objects**: Leverage Pydantic's validation + dataclass-like syntax. Add methods when behavior emerges.

4. **Commands as functions**: CLI commands map naturally to functions. OOP is not required for everything.

5. **Extract modules, not classes first**: When something grows too large, extracting to a new module often beats creating a new class.
