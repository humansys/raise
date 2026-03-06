# Research Report: Python Code Quality Standards for Senior Review

Date: 2026-03-06
Researcher: Rai
Decision: Define code governance for raise-commons before open source publication
Depth: Standard (24 sources, 8 triangulated claims)

---

## Executive Summary

A senior Python developer evaluates code across 5 dimensions, in priority order:

1. **Correctness & Safety** — Does it work? Can it fail silently?
2. **Readability & Idiom** — Is it Pythonic? Can a teammate understand it in 30 seconds?
3. **Type Safety & API Surface** — Are contracts explicit? Is the public API clean?
4. **Architecture & Design** — Does dependency direction flow correctly? Is domain logic pure?
5. **Collaboration & Maintenance** — Can someone contribute without reading everything?

The "definition of done" for code that passes a senior review: **functionally correct, idiomatically Python, architecturally sound, and tooling-enforced**.

---

## The Five Dimensions

### Dimension 1: Correctness & Safety

What a senior reviewer checks:

| Criterion | Standard | Sources |
|-----------|----------|---------|
| Error handling | Specific exceptions, never bare `except:` | PEP 20, Slatkin 80-88, Google |
| Exception chaining | `raise X from Y` for clear tracebacks | Slatkin Item 88 |
| Resource cleanup | Context managers (`with`) for all I/O | Slatkin, Google, QuantifiedCode |
| Mutable defaults | Never `def f(items=[])` — use `None` sentinel | Google, Slatkin, Augment |
| Return consistency | All paths return, or none do — never mixed | PEP 8, Google |
| Security | No hardcoded secrets, no unsafe deserialization, parameterized queries | Augment, Bandit/Ruff S rules |
| Thread safety | Shared mutable state documented or eliminated | Google |

### Dimension 2: Readability & Idiom

| Criterion | Standard | Sources |
|-----------|----------|---------|
| Iteration | `enumerate`, `zip`, unpacking — never index manipulation | Hettinger, Ramalho |
| Data model | Dunder methods for protocol compliance (`__repr__`, `__eq__`, `__hash__`, `__len__`) | Ramalho |
| Collections | `defaultdict`, `Counter`, comprehensions — not manual loops | Hettinger |
| Function size | <40 lines (Google), single responsibility | Google, Augment |
| Nesting depth | <=3 levels — flat is better than nested | PEP 20, wemake |
| Naming | Domain terminology, not generic (`user` not `data_handler`) | DEV Community, QuantifiedCode |
| Comments | Explain WHY, not WHAT — code is self-documenting | Google, Augment, multiple |
| Modern syntax | `list[str]` not `List[str]`, `X \| None` not `Optional[X]` | Meta Survey, Augment |

### Dimension 3: Type Safety & API Surface

| Criterion | Standard | Sources |
|-----------|----------|---------|
| Public API annotated | All public functions/methods with types | PEP 484, Meta Survey (86% adoption) |
| Parameter types | Abstract (`Sequence`, `Mapping`) for inputs | PEP 484 |
| Return types | Concrete for outputs | PEP 484 |
| Optional explicit | `X \| None`, never inferred from `= None` | PEP 484, Pyright strict |
| No Any leakage | Generic `TypeVar` over `Any` | Pyright strict |
| Flat API surface | `__init__.py` re-exports — users don't learn internals | Ben Hoyt, Pydantic |
| Custom exceptions | Base exception per library, contextual data on exception objects | Ben Hoyt, Slatkin Item 121 |
| Short clear names | Module provides context — `requests.get()` not `requests.send_get_request()` | Ben Hoyt |

### Dimension 4: Architecture & Design

| Criterion | Standard | Sources |
|-----------|----------|---------|
| Dependency direction | High-level depends on abstractions, not details | Percival & Gregory, Pydantic |
| Domain purity | Domain logic has no I/O imports | Percival & Gregory |
| Testability | Domain logic testable without DB/mocks/network | Percival & Gregory |
| Single responsibility | Each module/class does one thing | Multiple |
| Composition > inheritance | Delegation, not deep hierarchies | Ramalho, Percival & Gregory |
| Declarative over imperative | Describe what, not how — where applicable | FastAPI, Typer, Polars |
| No global mutable state | Configuration via instances, not module-level dicts | Ben Hoyt, QuantifiedCode |
| Layer contracts | Enforceable with import-linter | import-linter, Seddon |

### Dimension 5: Collaboration & Maintenance

| Criterion | Standard | Sources |
|-----------|----------|---------|
| Docstrings | All public APIs — Args/Returns/Raises sections | PEP 257, Google |
| Import organization | stdlib / third-party / local, blank line separated | PEP 8, isort/Ruff I |
| Test quality | >=80% branch coverage, specific assertions, edge cases | Augment |
| Commit discipline | Incremental commits, clear messages, no mega-diffs | DEV Community |
| Pre-commit hooks | Formatter + linter + type checker automated | Augment, multiple |
| Dependency justification | Written rationale for new deps | Augment |

---

## Tooling Recommendations

### Current State (raise-commons)
- Ruff: E, W, F, I, N, UP, B, C4, SIM
- Pyright: strict mode (already gold standard)
- Coverage: 91%

### Recommended Additions

#### Tier 1: Expand Ruff (zero new deps)

Add rule sets: `S` (security), `C90` (complexity), `PL` (pylint), `PERF` (performance), `FURB` (refactoring), `RET` (return consistency), `ARG` (unused args), `ERA` (commented code), `PT` (pytest style), `TC` (type checking imports), `A` (builtins shadowing).

Set `[tool.ruff.lint.mccabe] max-complexity = 10`.

**Replaces standalone Bandit. Confidence: Very High.**

#### Tier 2: Architecture Enforcement (one new dep)

Add `import-linter` with layered contracts:
- cli -> services -> adapters -> core
- Prevents architectural decay automatically

**Confidence: High. Simple config (~6 lines), proven tool.**

#### Tier 3: Deeper Quality (optional, higher friction)

- `wemake-python-styleguide` — OOP violations, cognitive complexity (requires flake8)
- `Radon` — Maintainability Index tracking
- `Vulture` — Dead code beyond what Ruff catches

**Confidence: Medium-High. Value clear but adds tool complexity.**

---

## "AI-Generated" Code Tells to Eliminate

These are patterns that signal "a machine wrote this, no human reviewed it":

1. **Excessive obvious comments** — `# Initialize the list` above `items = []`
2. **Generic names** — `processed_item`, `data_handler`, `result_value` (no domain language)
3. **Old typing syntax** — `from typing import List, Optional, Dict` on 3.10+
4. **Monolithic functions** — 200+ line functions doing fetch/transform/validate/persist
5. **Vague assertions in tests** — `assert result is not None` instead of specific value checks
6. **Suspiciously uniform structure** — real code has pragmatic compromises

**Note:** Some of these are legitimate in generated code that gets human review. The issue is when there's no evidence of human judgment applied.

---

## Definition of Done: "Beautiful Python"

Code passes a senior Python review when:

1. **Zen-compliant** — Beautiful, explicit, simple, flat, readable
2. **Idiomatically Python** — Uses the data model, not fighting the language
3. **Type-safe** — Pyright strict passes, public API fully annotated
4. **Architecturally sound** — Dependency direction enforced, domain logic pure
5. **Tooling-verified** — Ruff (expanded), Pyright strict, import-linter, >=80% coverage
6. **Human-reviewed** — Evidence of judgment, not just generation

A codebase achieves "beauty" when a senior developer reads it and thinks:
> "Whoever wrote this understands Python deeply, respects the reader, and made deliberate design choices."

---

## Confidence Assessment

| Recommendation | Confidence | Triangulation |
|---|---|---|
| 5-dimension review framework | High | Synthesized from 8+ sources per dimension |
| Expand Ruff rules | Very High | Used by Pydantic, FastAPI; built into existing tool |
| import-linter for architecture | High | Proven, simple, actively maintained |
| Modern type syntax standard | Very High | Meta survey (1,241 respondents), PEPs, all top projects |
| Complexity enforcement (<=10) | High | Google, Augment, Ruff C90; exact threshold debatable |
| "AI tells" checklist | Medium-High | 4 sources, mostly secondary; directionally correct |

**Overall confidence in framework: High.** Major claims triangulated across 3+ independent sources. No significant contrary evidence found.

---

## Next Steps

1. Codify this into `.raise/governance/code-standards.md` as an enforceable governance artifact
2. Audit raise-commons against these criteria (module by module)
3. Capture findings as an epic with prioritized stories
4. Update Ruff config and add import-linter
5. Patterns learned become permanent governance

---

## References

See `sources/evidence-catalog.md` for full source index with 24 entries and 8 triangulated claims.
