# Recommendation: DRY and SOLID Guidelines for raise-cli

> Research ID: DRY-SOLID-PYTHON-20260205
> Based on synthesis of 28 sources

---

## Decision

**Adopt a pragmatic, Python-idiomatic approach to DRY and SOLID that prioritizes simplicity and readability over dogmatic adherence.**

**Confidence**: HIGH

---

## Rationale

The evidence strongly supports that:
1. Python's dynamic nature allows lighter SOLID implementation than statically-typed languages
2. Premature abstraction costs more than duplication
3. The Python community consensus favors composition, protocols, and pragmatism
4. CLI tools benefit from flat, simple architectures

---

## Practical Guidelines for raise-cli

### DRY Guidelines

| Situation | Guideline | Example |
|-----------|-----------|---------|
| Code duplicated once | **Leave it** - Not enough data to know the pattern | Two similar validators in different modules |
| Code duplicated twice | **Leave it** - Still premature to abstract | Three similar extractors |
| Code duplicated 3+ times | **Consider abstracting** - If same semantic concept | Common file parsing across 3+ commands |
| Same syntax, different meaning | **Keep separate** - Not true duplication | Kata validator vs Component validator |
| Abstraction accumulates special cases | **Remove it** - Re-introduce duplication | Utility function with 5+ conditional branches |

**Heuristic**: Ask "Would changes to one instance ALWAYS require changes to the others?" If no, it's not true duplication.

### SOLID Guidelines (Python-Adapted)

#### S - Single Responsibility
```python
# GOOD: Clear single responsibility
class ConceptExtractor:
    """Extracts concepts from governance files."""
    def extract(self, content: str) -> list[Concept]: ...

# BAD: Multiple responsibilities
class ConceptManager:
    """Extracts, validates, stores, and formats concepts."""  # Too many jobs
```

**Test**: Can you describe the class/function purpose without "and"?

#### O - Open/Closed
```python
# GOOD: Open for extension via composition
class ConceptGraph:
    def __init__(self, extractors: list[Extractor]):
        self.extractors = extractors  # Add new extractors without modifying

# GOOD: Python decorator pattern
@validate_input
def process_kata(kata: Kata) -> Result: ...  # Add validation without modifying
```

**Test**: Can you add new behavior without modifying existing code?

#### L - Liskov Substitution
```python
# GOOD: Subclasses are substitutable
class FileExtractor(Extractor):
    def extract(self, path: Path) -> list[Concept]: ...  # Same contract

# BAD: Subclass changes contract
class CachingExtractor(Extractor):
    def extract(self, path: Path, use_cache: bool) -> list[Concept]: ...  # Different signature
```

**Test**: Can you replace parent with child everywhere without breaking code?

#### I - Interface Segregation
```python
# GOOD: Use Protocols for focused interfaces
class Extractor(Protocol):
    def extract(self, content: str) -> list[Concept]: ...

# Python naturally handles this via duck typing - don't over-engineer
```

**Guideline**: In Python, duck typing often makes explicit ISP unnecessary. Use Protocols when you need type checking.

#### D - Dependency Inversion
```python
# GOOD: Depend on abstractions (protocols/duck typing)
class GraphBuilder:
    def __init__(self, extractor: Extractor):  # Protocol, not concrete class
        self.extractor = extractor

# GOOD: Constructor injection (no framework needed)
def create_graph_builder():
    return GraphBuilder(extractor=ConceptExtractor())  # Composition root
```

**Guideline**: Simple constructor injection is sufficient. Avoid DI frameworks unless complexity genuinely warrants it.

### Composition vs Inheritance Decision Tree

```
Do you need to reuse code?
├── Yes: Is it a genuine "is-a" relationship?
│   ├── Yes: Does subclass specialize behavior?
│   │   ├── Yes: Use INHERITANCE
│   │   └── No: Use COMPOSITION
│   └── No: Use COMPOSITION
└── No: Don't abstract yet
```

**Default**: Composition. Only use inheritance when you're genuinely specializing behavior.

### Refactoring Patterns for raise-cli

| Pattern | When to Use | Python Implementation |
|---------|-------------|----------------------|
| Extract Method | Function > 20 lines or has "and" in description | Move to helper function, consider module-level |
| Extract Class | Class has multiple reasons to change | Split into focused classes with composition |
| Introduce Parameter Object | 4+ related parameters | Use `@dataclass` or Pydantic `BaseModel` |
| Replace Conditional with Polymorphism | Switch on type appears 3+ times | Use Protocol + strategy pattern |
| Move Method | Method uses more features of another class | Move to that class |

### Code Smells to Watch

| Smell | Detection | Resolution |
|-------|-----------|------------|
| God Object | Class > 500 lines, 10+ methods | Extract Class incrementally |
| Long Method | Function > 30 lines | Extract Method |
| Feature Envy | Method mostly accesses another class's data | Move Method |
| Data Clumps | Same 3+ parameters appear together | Introduce Parameter Object |
| Shotgun Surgery | One change requires many small changes | Consolidate into single module |
| Premature Abstraction | Abstract class with 1 implementation | Inline it, wait for second use |

---

## Trade-offs Acknowledged

### We Accept
- Some code duplication (bounded, known cost)
- Simpler architecture over "complete" SOLID compliance
- Protocols over ABCs (less runtime checking)
- Functions over classes when appropriate

### We Sacrifice
- Academic "purity" of design patterns
- Explicit interface enforcement at runtime
- Framework-based dependency management
- Deep inheritance hierarchies (not actually a sacrifice)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Under-abstraction leads to inconsistency | Code review focus on semantic duplication |
| Over-abstraction creeps in | Require justification for new abstractions in PRs |
| Protocol misuse (wrong structure passes type check) | Integration tests verify behavior, not just types |
| Composition complexity | Keep dependency chains shallow (max 3 levels) |

---

## Implementation Checklist

Before merging PRs that add abstractions:

- [ ] Is this the 3rd+ instance of this pattern?
- [ ] Does the abstraction represent a single semantic concept?
- [ ] Can the abstraction be described without "and"?
- [ ] Is there a simpler alternative (function, module)?
- [ ] Does it use composition over inheritance?
- [ ] Are dependencies injected (not created internally)?
- [ ] If using Protocol/ABC: is runtime enforcement actually needed?

---

## Governance Linkage

This research informs:
- **Code review standards**: Reviewers should challenge premature abstractions
- **Guardrails update**: Consider adding "Rule of Three" guideline
- **Developer onboarding**: Include pragmatic SOLID guidance

---

## Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| Strict DRY (abstract on 2nd occurrence) | Evidence shows this leads to wrong abstractions |
| Java-style SOLID (ABCs everywhere) | Python's dynamic nature makes this unnecessary |
| No guidelines (pure code review) | Explicit heuristics help junior developers and AI assistants |
| DI framework | Overhead not justified for CLI tool complexity |

---

## Summary: The raise-cli Design Philosophy

```
1. Start simple. Add complexity only when evidence demands it.
2. Duplication is not a sin. Wrong abstraction is worse.
3. Wait for three. Then abstract with confidence.
4. Compose, don't inherit. Keep hierarchies flat.
5. Functions are fine. Not everything needs a class.
6. Inject dependencies. But skip the framework.
7. Practicality beats purity. When in doubt, keep it simple.
```
