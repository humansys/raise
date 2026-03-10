# Evidence Catalog: DRY and SOLID Principles in Python

> Research ID: DRY-SOLID-PYTHON-20260205
> Search Date: 2026-02-05
> Tool: WebSearch (Claude)
> Researcher: Rai (Claude Opus 4.5)

---

## Summary Statistics

- **Total Sources**: 25
- **Evidence Distribution**:
  - Very High: 7 (28%)
  - High: 10 (40%)
  - Medium: 6 (24%)
  - Low: 2 (8%)
- **Temporal Coverage**: 2012-2025 (focus on 2020+)

---

## Sources by Topic

### DRY Principle and Rule of Three

**Source 1**: [The Wrong Abstraction - Sandi Metz](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- **Type**: Primary (original practitioner insight)
- **Evidence Level**: Very High
- **Date**: 2016 (seminal, still referenced)
- **Key Finding**: "Duplication is far cheaper than the wrong abstraction" - wrong abstractions compound in cost over time
- **Relevance**: Core principle for when NOT to apply DRY; foundational for understanding abstraction timing

**Source 2**: [Refactoring and The Rule of Three - Incus Data](https://incusdata.com/blog/refactoring-the-rule-of-three)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2025
- **Key Finding**: Wait until code is repeated 3 times before abstracting; the third instance provides enough context to understand the pattern
- **Relevance**: Practical heuristic for DRY timing

**Source 3**: [The Rule of Three - Andrew Brookins](https://andrewbrookins.com/technology/the-rule-of-three/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2015
- **Key Finding**: The first and second implementations reveal different aspects; only by the third can you see the true pattern
- **Relevance**: Explains WHY rule of three works

**Source 4**: [Abstraction: The Rule of Three - Los Techies](https://lostechies.com/derickbailey/2012/10/31/abstraction-the-rule-of-three/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2012
- **Key Finding**: First time: just implement. Second time: let it be. Third time: NOW consider abstraction
- **Relevance**: Original articulation of the implementation protocol

**Source 5**: [Don't make Clean Code harder to maintain - Understanding Legacy Code](https://understandlegacycode.com/blog/refactoring-rule-of-three/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Focus on meaning, not syntax; only abstract when code represents the SAME concept
- **Relevance**: Critical distinction between semantic vs syntactic duplication

---

### Premature Abstraction

**Source 6**: [Avoiding Premature Software Abstractions - Better Programming](https://betterprogramming.pub/avoiding-premature-software-abstractions-8ba2e990930a)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2021
- **Key Finding**: Abstractions add complexity; only add when solving a real (not theoretical) problem
- **Relevance**: Balances DRY against complexity cost

**Source 7**: [Premature Abstraction: When Clean Code Goes Wrong - Codeling](https://codeling.dev/blog/premature-abstraction-in-software-engineering/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Red flag: if abstraction checks numerous input cases, it was premature or has outgrown its purpose
- **Relevance**: Diagnostic for detecting wrong abstractions

**Source 8**: [Post-Architecture: Premature Abstraction is the Root of All Evil - Arend Jr](https://arendjr.nl/blog/2024/07/post-architecture-premature-abstraction-is-the-root-of-all-evil/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Premature abstraction leads to wasted effort, increased complexity, reduced flexibility, slower development
- **Relevance**: Articulates concrete costs of over-abstraction

**Source 9**: [WET vs AHA: Avoiding Premature Abstraction - Code With Seb](https://www.codewithseb.com/blog/wet-vs-aha-avoiding-premature-abstraction-in-frontend-development)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: WET (Write Everything Twice) is acceptable; AHA (Avoid Hasty Abstractions) is the balance
- **Relevance**: Alternative acronyms that complement DRY

---

### SOLID Principles in Python

**Source 10**: [SOLID Design Principles - Real Python](https://realpython.com/solid-principles-python/)
- **Type**: Primary (authoritative Python resource)
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Python's dynamic nature means ISP naturally handled through duck typing; DIP easier without frameworks
- **Relevance**: Authoritative Python-specific SOLID guide

**Source 11**: [A Pythonic Guide to SOLID Design Principles - DEV Community](https://dev.to/ezzy1337/a-pythonic-guide-to-solid-design-principles-4c8i)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Python doesn't need interfaces for polymorphism; SOLID applies but with lighter implementation
- **Relevance**: Practical adaptation of SOLID for Python idioms

**Source 12**: [SOLID Python (Research Paper) - ResearchGate](https://www.researchgate.net/publication/323935872_SOLID_Python_SOLID_principles_applied_to_a_dynamic_programming_language)
- **Type**: Primary (academic)
- **Evidence Level**: Very High
- **Date**: 2018
- **Key Finding**: Dynamic languages reduce SOLID implementation complexity but principles still apply
- **Relevance**: Academic validation of SOLID in dynamic contexts

**Source 13**: [Python Single Responsibility Principle - PythonTutorial.net](https://www.pythontutorial.net/python-oop/python-single-responsibility-principle/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: If you can't describe function purpose without "and", split it; applies at module, class, and function levels
- **Relevance**: Practical SRP heuristic

---

### Composition vs Inheritance

**Source 14**: [The Composition Over Inheritance Principle - Python Patterns](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- **Type**: Primary (Brandon Rhodes, authoritative)
- **Evidence Level**: Very High
- **Date**: 2020+
- **Key Finding**: Design principles like Composition Over Inheritance are more important than individual patterns; dead code analyzers work better with composition
- **Relevance**: Definitive Python guide to composition

**Source 15**: [Inheritance and Composition: A Python OOP Guide - Real Python](https://realpython.com/inheritance-composition-python/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Use inheritance for "is-a" when behavior needs sharing; use composition for "has-a" and modularity
- **Relevance**: Decision framework for choosing between approaches

**Source 16**: [Why I Prefer Composition Over Inheritance in Python - Philip Mutua](https://medium.com/@philip.mutua/why-i-prefer-composition-over-inheritance-in-python-a-practical-guide-f9fddd4aa72f)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Composition promotes loose coupling; components can be swapped without affecting the system
- **Relevance**: Practical benefits for maintainability

---

### Python Protocols, ABCs, and Duck Typing

**Source 17**: [PEP 544 - Protocols: Structural Subtyping - Python.org](https://peps.python.org/pep-0544/)
- **Type**: Primary (official)
- **Evidence Level**: Very High
- **Date**: 2017 (Python 3.8+)
- **Key Finding**: Protocols enable "static duck typing" - structure checked by type checkers without runtime cost
- **Relevance**: Modern Python approach to interfaces

**Source 18**: [Abstract Base Classes and Protocols - Justin Ellis](https://jellis18.github.io/post/2022-01-11-abc-vs-protocol/)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2022
- **Key Finding**: Use ABC for runtime enforcement; use Protocol for static checking; Protocol is more Pythonic
- **Relevance**: Decision guide for interface choices

**Source 19**: [Duck Typing in Python - Real Python](https://realpython.com/duck-typing-python/)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: 2024
- **Key Finding**: Duck typing is Python's default; formal interfaces are optional optimizations for type safety
- **Relevance**: Foundation for understanding Python's approach to polymorphism

---

### Dependency Injection

**Source 20**: [How I Use Dependency Injection in Python Without a Framework - Medium](https://medium.com/the-pythonworld/how-i-use-dependency-injection-in-python-without-a-framework-69bbd24cbedc)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2023
- **Key Finding**: Constructor injection + composition root pattern; no framework needed for simple DI
- **Relevance**: Practical DI without over-engineering

**Source 21**: [Python Dependency Injection Guide - DataCamp](https://www.datacamp.com/tutorial/python-dependency-injection)
- **Type**: Secondary
- **Evidence Level**: High
- **Date**: 2024
- **Key Finding**: DI complexity in Python is lower than other languages; frameworks optional
- **Relevance**: Validates simple DI approach

---

### Code Smells and Refactoring

**Source 22**: [Code Smells - Refactoring Guru](https://refactoring.guru/refactoring/smells)
- **Type**: Primary (authoritative catalog)
- **Evidence Level**: Very High
- **Date**: Ongoing
- **Key Finding**: Comprehensive catalog: Long Method, Large Class, Feature Envy, Data Clumps, etc.
- **Relevance**: Reference for smell detection

**Source 23**: [Introduce Parameter Object - Refactoring Guru](https://refactoring.guru/introduce-parameter-object)
- **Type**: Primary
- **Evidence Level**: Very High
- **Date**: Ongoing
- **Key Finding**: Parameter clusters indicate hidden objects; Parameter Objects should eventually own related behavior
- **Relevance**: Key refactoring for Python dataclasses

**Source 24**: [God Object Anti-Pattern in Python - Software Patterns Lexicon](https://softwarepatternslexicon.com/patterns-python/11/2/4/)
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Finding**: Split God Objects incrementally using Extract Class; test each change
- **Relevance**: Python-specific God Object guidance

---

### Balance: KISS/YAGNI vs DRY/SOLID

**Source 25**: [Clean Code Essentials: YAGNI, KISS, DRY - DEV Community](https://dev.to/juniourrau/clean-code-essentials-yagni-kiss-and-dry-in-software-engineering-4i3j)
- **Type**: Secondary
- **Evidence Level**: Low
- **Date**: 2024
- **Key Finding**: Start simple (KISS), avoid duplication as codebase grows (DRY), defer unnecessary features (YAGNI)
- **Relevance**: Integration of competing principles

**Source 26**: [KISS, DRY, SOLID, YAGNI Guide - HlfDev](https://medium.com/@hlfdev/kiss-dry-solid-yagni-a-simple-guide-to-some-principles-of-software-engineering-and-clean-code-05e60233c79f)
- **Type**: Secondary
- **Evidence Level**: Low
- **Date**: 2023
- **Key Finding**: These are tensions to manage, not rules to follow; requires architectural insight
- **Relevance**: Frames principles as trade-offs

---

### Python Philosophy

**Source 27**: [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)
- **Type**: Primary (official)
- **Evidence Level**: Very High
- **Date**: 2004 (canonical)
- **Key Finding**: "Simple is better than complex. Complex is better than complicated. Practicality beats purity."
- **Relevance**: Python's design philosophy supports pragmatic approach

**Source 28**: [Fluent Python - Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)
- **Type**: Primary (authoritative book)
- **Evidence Level**: Very High
- **Date**: 2022 (2nd edition)
- **Key Finding**: Pythonic patterns differ from Java patterns; functions as first-class objects change design
- **Relevance**: Definitive guide to Pythonic design

---

## Evidence Quality Assessment

| Topic | Very High | High | Medium | Low |
|-------|-----------|------|--------|-----|
| DRY/Rule of Three | 1 | 3 | 1 | 0 |
| Premature Abstraction | 0 | 1 | 3 | 0 |
| SOLID in Python | 3 | 2 | 0 | 0 |
| Composition vs Inheritance | 2 | 0 | 1 | 0 |
| Protocols/ABCs/Duck Typing | 2 | 1 | 0 | 0 |
| Dependency Injection | 0 | 2 | 0 | 0 |
| Code Smells/Refactoring | 2 | 0 | 1 | 0 |
| KISS/YAGNI Balance | 0 | 0 | 0 | 2 |
| Python Philosophy | 2 | 0 | 0 | 0 |

**Note**: The KISS/YAGNI balance topic has lower evidence quality because most sources are introductory articles. However, this topic is well-triangulated through the combination of Sandi Metz's work, Python Philosophy sources, and the premature abstraction literature.
