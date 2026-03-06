# Code Quality Standards — raise-commons

> **Status: DRAFT**
>
> This standard will be validated against the raise-commons codebase in S370.4.
> Criteria that prove impractical will be adjusted.
> Criteria that prove essential will be strengthened.

---

## Purpose

This document defines the concrete, verifiable criteria that raise-commons code must satisfy. It translates the research findings (24 sources, 5 dimensions, 8 triangulated claims) into an actionable governance artifact.

## How to Use

- **During review:** Walk each dimension relevant to the change. Check criteria in order.
- **During implementation:** Use the "How" column to self-check before requesting review.
- **For tooling:** Criteria classified as TOOL can be automated. HUMAN criteria require judgment.

## Criterion Format

Every criterion follows the **What / How / Why** triple:

- **What:** The specific, observable thing to check.
- **How:** The verification method — a tool command, a review question, or both.
- **Why:** Evidence-backed rationale with source attribution.

Classification:

- **TOOL** — Fully automatable via Ruff rule, Pyright check, or import-linter contract.
- **HUMAN** — Requires human or AI judgment during review.
- **BOTH** — Partially automatable (tool catches the obvious cases), partially judgment.

---

## D1: Correctness & Safety

*Priority: Highest. Code that is incorrect or unsafe fails regardless of how elegant it looks.*

### D1.1: Specific exception handling

- **What:** Every `except` clause catches a specific exception type. No bare `except:`. Overly broad `except Exception:` only with explicit justification (e.g., error-isolation hooks with logging).
- **How:** `ruff check --select E722` catches bare `except`. Manual review for `except Exception:` — verify the caught exception is logged (at minimum debug level) and re-raised or explicitly justified.
- **Why:** "Errors should never pass silently" (PEP 20). Bare excepts catch `KeyboardInterrupt` and `SystemExit`, hiding real errors. Overly broad catches mask bugs silently. (Sources: PEP 20 [S1], Slatkin Items 80-88 [S6], Google Style Guide [S5], Augment [S15])
- **Classification:** BOTH (E722 is TOOL; `Exception` broadness is HUMAN)

### D1.2: Exception chaining

- **What:** When catching one exception and raising another, always use `raise X from Y` to preserve the original traceback.
- **How:** `ruff check --select B904` (within `except`, `raise` without `from`). Manual review for cases where chaining is missing but should be present.
- **Why:** Without chaining, the original cause is lost. Debugging becomes guesswork. `raise X from Y` produces a "The above exception was the direct cause..." message that connects cause to effect. (Sources: Slatkin Item 88 [S6])
- **Classification:** BOTH (B904 is TOOL; completeness is HUMAN)

### D1.3: Resource cleanup via context managers

- **What:** All I/O resources (files, network connections, database cursors, locks) use `with` statements or explicit context managers. No manual `open()`/`close()` pairs.
- **How:** `ruff check --select SIM115` (open() without context manager). Manual review for custom resources that should implement `__enter__`/`__exit__`.
- **Why:** Context managers guarantee cleanup even on exceptions. Manual close() is skipped on early return or exception, leaking file descriptors and connections. (Sources: Slatkin [S6], Google Style Guide [S5], QuantifiedCode [S16])
- **Classification:** BOTH (SIM115 is TOOL; custom resource review is HUMAN)

### D1.4: No mutable default arguments

- **What:** Function parameters never use mutable defaults (`list`, `dict`, `set`). Use `None` sentinel with explicit creation in the body.
- **How:** `ruff check --select B006` (mutable default argument). Pyright also flags some cases.
- **Why:** Mutable defaults are shared across calls — a function that does `def f(items=[])` accumulates state between invocations. This is Python's most infamous gotcha. (Sources: Google Style Guide [S5], Slatkin [S6], Augment [S15])
- **Classification:** TOOL (B006)

### D1.5: Consistent return types

- **What:** Every code path in a function returns a value, or none do. No mixed `return value` / bare `return` / implicit `None`. All return types explicit in annotation.
- **How:** `ruff check --select RET` (return consistency rules). Pyright strict enforces return type annotation completeness.
- **Why:** Mixed returns force callers to check for None unexpectedly. Explicit returns with explicit types make the function contract clear. (Sources: PEP 8 [S2], Google Style Guide [S5])
- **Classification:** TOOL (RET rules + Pyright strict)

### D1.6: Security hygiene

- **What:** No hardcoded secrets (passwords, API keys, tokens). No `eval()`/`exec()` on untrusted input. No `pickle.loads()` on untrusted data. SQL via parameterized queries only.
- **How:** `ruff check --select S` (Bandit security rules: S105 hardcoded passwords, S307 eval, S301 pickle, S608 SQL injection). Environment variables or secret managers for credentials.
- **Why:** Hardcoded secrets leak via version control. `eval`/`pickle` on untrusted input enables arbitrary code execution. These are not theoretical — they are the top causes of Python security incidents. (Sources: Augment [S15], Ruff/Bandit S rules [S18])
- **Classification:** TOOL (S rules)

### D1.7: Thread safety awareness

- **What:** Shared mutable state is either eliminated (preferred) or explicitly documented with synchronization strategy. Module-level mutable state (non-constant dicts, lists) requires justification comment.
- **How:** Manual review. Grep for module-level mutable assignments (`^[A-Z_]+ =.*\[\]` or `{}` patterns that are not `Final`). Check that concurrent access patterns are documented.
- **Why:** Shared mutable state is the root cause of race conditions. Even in single-threaded CLI code, libraries may be used in async or threaded contexts later. Documenting the assumption prevents future bugs. (Sources: Google Style Guide [S5])
- **Classification:** HUMAN

---

## D2: Readability & Idiom

*Priority: High. Pythonic code communicates intent. Non-idiomatic code forces readers to reverse-engineer what the author meant.*

### D2.1: Pythonic iteration

- **What:** Use `enumerate()` for index+value, `zip()` for parallel iteration, tuple unpacking for structured data. Never manipulate indices manually (`for i in range(len(items))`).
- **How:** `ruff check --select C4,SIM` catches some anti-patterns (unnecessary list comprehensions, simplifiable iterations). Manual review for index-manipulation patterns that tools miss.
- **Why:** Index manipulation is error-prone (off-by-one), harder to read, and ignores Python's iterator protocol. "There should be one obvious way to do it" (PEP 20). (Sources: Hettinger [S9], Ramalho [S8], Slatkin [S6])
- **Classification:** BOTH (C4/SIM partial TOOL; idiom completeness is HUMAN)

### D2.2: Data model usage

- **What:** Classes implement appropriate dunder methods for their role: `__repr__` for debugging, `__eq__`/`__hash__` for value semantics, `__len__`/`__iter__` for container behavior, `__enter__`/`__exit__` for resource management.
- **How:** Manual review. For Pydantic models (per ADR-002), these are provided automatically. For non-Pydantic classes, check that protocol compliance matches usage context.
- **Why:** Python's data model enables objects to participate in language protocols (iteration, comparison, context management). Not implementing relevant dunders forces callers into workarounds. (Sources: Ramalho [S8])
- **Classification:** HUMAN

### D2.3: Standard library collections

- **What:** Use `defaultdict`, `Counter`, `deque`, `namedtuple` where appropriate. Use comprehensions for transformations. Avoid manual accumulation loops when a one-liner comprehension is clearer.
- **How:** Manual review. Look for patterns like `d = {}; for x in items: if x not in d: d[x] = 0; d[x] += 1` that should be `Counter(items)`.
- **Why:** Standard library collections are tested, optimized, and instantly recognizable to experienced Python developers. Reimplementing them is slower and harder to read. (Sources: Hettinger [S9], Ramalho [S8])
- **Classification:** HUMAN

### D2.4: Function size

- **What:** Functions are at most 40 lines of logic (excluding docstrings, blank lines, and type annotations). Functions exceeding this threshold must be decomposed.
- **How:** `ruff check --select C901` with `[tool.ruff.lint.mccabe] max-complexity = 10`. Manual review for functions under the complexity threshold but over 40 lines (long but simple).
- **Why:** Long functions have multiple responsibilities, are hard to test in isolation, and force readers to hold too much context. The 40-line threshold aligns with Google's standard and fits on one screen. (Sources: Google Style Guide [S5], Augment [S15], Ruff C90 [S18])
- **Classification:** BOTH (C901 complexity is TOOL; line count is HUMAN)

### D2.5: Nesting depth

- **What:** Maximum 3 levels of indentation within a function body. Use early returns, guard clauses, and extracted helper functions to flatten logic.
- **How:** Manual review (Ruff does not enforce nesting depth directly). `wemake-python-styleguide` WPS220 can enforce this if adopted. Look for `if/for/if/for` patterns.
- **Why:** "Flat is better than nested" (PEP 20). Deep nesting forces readers to track multiple conditions simultaneously, increasing cognitive load and bug likelihood. (Sources: PEP 20 [S1], wemake [S20])
- **Classification:** HUMAN

### D2.6: Domain naming

- **What:** Variables, functions, classes, and modules use domain terminology. No generic names like `data`, `handler`, `processor`, `manager`, `item`, `result` unless in genuinely generic utility code.
- **How:** Manual review. Check that names answer "what business concept does this represent?" not "what technical role does this play?"
- **Why:** Generic names require reading the implementation to understand purpose. Domain names carry meaning: `backlog_item` vs `data_object`, `parse_jql_query` vs `process_input`. (Sources: DEV Community [S17], QuantifiedCode [S16])
- **Classification:** HUMAN

### D2.7: Comments explain WHY

- **What:** Comments explain intent, constraints, trade-offs, or non-obvious decisions. No comments that restate the code (`# increment counter` above `counter += 1`). Inline comments are for "why this specific choice."
- **How:** Manual review. Flag any comment that restates the next line of code. Check that non-obvious logic has a rationale comment.
- **Why:** Code says "what." Comments should say "why." Obvious comments add noise, get stale, and signal that no human reviewed the code. (Sources: Google Style Guide [S5], Augment [S15], PEP 8 [S2])
- **Classification:** HUMAN

### D2.8: Modern Python syntax

- **What:** Use `list[str]` not `List[str]`, `dict[str, int]` not `Dict[str, int]`, `X | None` not `Optional[X]`, `type Alias = X` not `Alias = TypeAlias`. Requires Python 3.10+ (raise-commons target).
- **How:** `ruff check --select UP` (pyupgrade rules: UP006 deprecated typing imports, UP007 Optional to union). Pyright also flags deprecated forms.
- **Why:** Modern syntax is shorter, requires no imports, and is the language direction. Old `from typing import List, Optional, Dict` is a tell that the code was generated from outdated patterns. (Sources: Meta Survey [S14], Augment [S15], Ruff UP rules [S18])
- **Classification:** TOOL (UP rules + Pyright)

---

## D3: Type Safety & API Surface

*Priority: High. Types are contracts. A clean API surface is the difference between a library people use and one they fight.*

### D3.1: Full public API annotation

- **What:** Every public function, method, and class attribute has explicit type annotations for all parameters and return values. No unannotated public API.
- **How:** Pyright strict mode (`"typeCheckingMode": "strict"`) enforces this globally. `ruff check --select ANN` can supplement for annotation presence.
- **Why:** 86% of Python developers use type hints always or often; 93% among those with 5-10 years of experience (Meta Survey). Types enable IDE support, catch bugs at write time, and serve as executable documentation. (Sources: PEP 484 [S4], Meta Survey [S14], Pyright [S21])
- **Classification:** TOOL (Pyright strict)

### D3.2: Abstract parameter types

- **What:** Function parameters accept abstract types (`Sequence`, `Mapping`, `Iterable`) rather than concrete types (`list`, `dict`). This allows callers to pass any compatible type.
- **How:** Manual review. Check that input parameters use `collections.abc` protocols or `typing` abstractions. Exceptions: when the function genuinely mutates the container (then `list` is correct).
- **Why:** "Accept interfaces, return concretes" is the Postel principle for types. Abstract inputs make functions more reusable and testable. (Sources: PEP 484 [S4], Slatkin [S6])
- **Classification:** HUMAN

### D3.3: Concrete return types

- **What:** Function return types are concrete (`list`, `dict`, `str`, specific Pydantic model) not abstract (`Sequence`, `Mapping`). Callers should know exactly what they get.
- **How:** Pyright strict mode enforces return type presence. Manual review for overly abstract return types that hide the actual value.
- **Why:** Concrete returns give callers full access to the returned type's API. Returning `Sequence` when you always return `list` hides `.append()`, `.sort()`, etc. (Sources: PEP 484 [S4], Ben Hoyt [S13])
- **Classification:** BOTH (Pyright enforces presence; HUMAN checks concreteness)

### D3.4: Explicit Optional

- **What:** Use `X | None` explicitly for nullable types. Never rely on `= None` default to imply Optional. Every nullable parameter and return must be annotated with `| None`.
- **How:** Pyright strict mode flags implicit Optional. `ruff check --select UP007` converts `Optional[X]` to `X | None`.
- **Why:** Implicit Optional hides the fact that None is a valid value. Explicit `| None` forces both the author and caller to handle the None case. (Sources: PEP 484 [S4], Pyright strict [S21])
- **Classification:** TOOL (Pyright strict + UP007)

### D3.5: No Any leakage

- **What:** `Any` is not used in public API signatures. Generic code uses `TypeVar` or `ParamSpec`. Internal `Any` for third-party untyped libs is acceptable with a `# type: ignore[*]` comment explaining why.
- **How:** Pyright strict mode (`reportUnknownMemberType`, `reportUnknownParameterType`, `reportUnknownVariableType`). Grep for `Any` in public function signatures.
- **Why:** `Any` disables type checking at that boundary. It propagates — one `Any` input produces `Any` outputs, creating a "type hole" that Pyright cannot analyze. (Sources: Pyright strict [S21], Slatkin [S6])
- **Classification:** TOOL (Pyright strict)

### D3.6: Flat API surface

- **What:** Each package exposes its public API via `__init__.py` re-exports. Users import from the package, not from internal modules. Internal modules are prefixed with `_` or excluded from `__all__`.
- **How:** Manual review. Check that `__init__.py` files re-export the public names. Check that external code does not import from `package._internal` or `package.submodule.detail`.
- **Why:** A flat API surface means users learn one import path. Internal reorganization does not break callers. This is how Pydantic, requests, and httpx work — clean public surface, rich internals. (Sources: Ben Hoyt [S13], Pydantic [S10])
- **Classification:** HUMAN

### D3.7: Custom exception hierarchy

- **What:** The library defines a base exception (`RaiseError` or similar). All custom exceptions inherit from it. Exceptions carry contextual data as attributes, not just string messages.
- **How:** Manual review. Check for a base exception class. Check that callers can `except RaiseError` to catch all library errors. Check that exception attributes provide programmatic access to error context.
- **Why:** A base exception lets callers handle "any library error" without catching too broadly. Contextual attributes enable programmatic error handling beyond string parsing. (Sources: Ben Hoyt [S13], Slatkin Item 121 [S6])
- **Classification:** HUMAN

### D3.8: Pydantic for data models

- **What:** All data structures that cross module boundaries use Pydantic `BaseModel`. No raw dicts for structured data. No dataclasses for validated data. Plain dataclasses acceptable only for internal, unvalidated value objects.
- **How:** Manual review. Check that function inputs/outputs carrying structured data use Pydantic models. Per ADR-002: "Use Pydantic v2 for all data models throughout the codebase."
- **Why:** Pydantic provides runtime validation, JSON serialization, and schema generation in one package. Raw dicts have no type safety, no validation, and are prone to typos. (Sources: ADR-002, Pydantic [S10], FastAPI [S11])
- **Classification:** HUMAN

---

## D4: Architecture & Design

*Priority: Medium-High. Architecture determines how well code ages. Bad architecture makes every future change harder.*

*This dimension references [ADR-001: Three-Layer Architecture](../../dev/decisions/adr-001-three-layer-architecture.md) as the authoritative architecture model for raise-commons.*

### D4.1: Dependency direction

- **What:** Dependencies flow downward only: Presentation (CLI) -> Application (Handlers) -> Domain (Engines) -> Core (Schemas, Config). No layer imports from a layer above it. Engines never import from CLI or handlers.
- **How:** `import-linter` with layered contracts enforcing: `cli | handlers | engines | core`. Run as `lint-imports`. Also verifiable via Pyright import analysis.
- **Why:** Upward dependencies create coupling — changing the CLI breaks the engine, changing the engine breaks nothing. ADR-001 establishes this as the foundational architecture rule for raise-commons. (Sources: ADR-001, Percival & Gregory [S7], Pydantic architecture [S10], import-linter [S19])
- **Classification:** TOOL (import-linter contracts)

### D4.2: Domain purity

- **What:** Domain logic (engines, core models) contains no I/O: no file reads, no network calls, no database queries, no logging side effects. I/O lives in handlers (orchestration) and adapters (infrastructure).
- **How:** Manual review + import analysis. Domain modules should not import `pathlib.Path.read_text`, `open`, `requests`, `httpx`, or any I/O library. `import-linter` forbidden contracts can enforce this.
- **Why:** Pure domain logic is testable without mocks, fixtures, or network. It can be reused across interfaces (CLI, MCP server, web UI) — which is exactly why ADR-001 adopted three layers. (Sources: ADR-001, Percival & Gregory [S7])
- **Classification:** BOTH (import-linter partial TOOL; I/O-via-function-call requires HUMAN review)

### D4.3: Testability by design

- **What:** Domain logic is testable with plain function calls and assertions — no database, no network, no filesystem required. If a function needs I/O to test, it has too many responsibilities.
- **How:** Manual review of test files. Check that domain tests use no `mock.patch`, no `tmp_path`, no `monkeypatch` for I/O. Handler/adapter tests may use these.
- **Why:** If testing domain logic requires mocking, the domain is impure. Mocks test the wiring, not the logic. Pure domain + thin I/O adapters is the Percival & Gregory pattern. (Sources: Percival & Gregory [S7])
- **Classification:** HUMAN

### D4.4: Single responsibility

- **What:** Each module and class has one reason to change. A module handles one concept (e.g., backlog parsing, session state, skill validation). A class represents one entity or one service.
- **How:** Manual review. Heuristic: if the module docstring needs "and" to describe its purpose, it does too much. Check that classes have <7 public methods and modules have <15 public functions.
- **Why:** Modules with multiple responsibilities change for multiple reasons, increasing merge conflicts, test fragility, and cognitive load. (Sources: Multiple — Percival & Gregory [S7], Google [S5], Augment [S15])
- **Classification:** HUMAN

### D4.5: Composition over inheritance

- **What:** Favor delegation and composition over class inheritance. Inheritance depth should not exceed 2 levels (base + one subclass). Use protocols (`typing.Protocol`) for interface contracts instead of abstract base classes where possible.
- **How:** Manual review. Check class hierarchies. Grep for multi-level inheritance chains. Look for "template method" patterns that could be replaced with strategy delegation.
- **Why:** Deep inheritance hierarchies are brittle — a change in the base class ripples through all descendants. Composition allows independent evolution. Python's duck typing and Protocol support make interface inheritance unnecessary. (Sources: Ramalho [S8], Percival & Gregory [S7])
- **Classification:** HUMAN

### D4.6: Declarative over imperative

- **What:** Where applicable, describe "what" rather than "how." Use Pydantic models for validation (not manual if/else chains), Typer decorators for CLI (not argparse boilerplate), and configuration-driven behavior over procedural setup.
- **How:** Manual review. Look for long procedural setup code that could be replaced with declarative configuration or model definitions.
- **Why:** Declarative code is shorter, less error-prone, and self-documenting. FastAPI, Typer, and Pydantic demonstrate that declarative Python is both possible and productive. (Sources: FastAPI [S11], Typer [S24], Pydantic [S10])
- **Classification:** HUMAN

### D4.7: No global mutable state

- **What:** No module-level mutable data structures (non-`Final` dicts, lists, sets). Configuration via Pydantic Settings instances, not module-level dicts. Module-level constants (`Final`) are acceptable. Module-level Path constants as test seams (PAT-E-589) are acceptable with justification.
- **How:** `ruff check --select PLW` can catch some global assignment patterns. Manual review for module-level mutable state. Grep for `^[a-z_]+ = (\\[|\\{|set\\()` at module level.
- **Why:** Global mutable state creates invisible coupling between functions, makes testing order-dependent, and causes bugs in concurrent use. (Sources: Ben Hoyt [S13], QuantifiedCode [S16])
- **Classification:** BOTH (partial TOOL via PLW; HUMAN for judgment on acceptable exceptions)

### D4.8: Layer contracts enforced

- **What:** Architecture layers from ADR-001 are enforced by automated tooling, not just convention. An `import-linter` configuration defines the allowed dependency directions and is checked in CI.
- **How:** `.importlinter` configuration in `pyproject.toml` with layered contracts. Run `lint-imports` in pre-commit and CI. Contracts define: `cli -> handlers -> engines -> core` with no reverse imports.
- **Why:** Convention without enforcement decays. import-linter is simple (~6 lines of config), runs in seconds, and catches architectural violations at commit time. (Sources: import-linter [S19], Seddon blog [S19], ADR-001)
- **Classification:** TOOL (import-linter)
