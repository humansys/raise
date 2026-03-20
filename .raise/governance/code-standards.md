# Code Quality Standards — raise-commons

> **Status: PERMANENT** (validated in E370 — S370.4 audit, S370.5 refactoring)
>
> Drafted in S370.1, validated by full codebase audit (28 modules, S370.4),
> refined through 6 refactoring stories (S370.5a-f). See Appendix C for
> audit learnings that informed the final version.

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

---

## D5: Collaboration & Maintenance

*Priority: Medium. Code is read more than written. These criteria ensure that contributions are sustainable and the codebase remains navigable.*

### D5.1: Docstrings on public API

- **What:** Every public module, class, function, and method has a docstring. Docstrings follow Google style with `Args:`, `Returns:`, and `Raises:` sections where applicable. Private functions (`_prefix`) may omit docstrings if the implementation is self-evident.
- **How:** `ruff check --select D` (pydocstyle rules: D100-D107 missing docstrings, D200-D215 formatting). Manual review for content quality — docstrings that just restate the function name add no value.
- **Why:** Docstrings are the primary documentation for library users. Args/Returns/Raises sections create a contract that IDE tooltips surface at the call site. (Sources: PEP 257 [S3], Google Style Guide [S5])
- **Classification:** BOTH (D rules check presence; HUMAN checks quality and completeness)

### D5.2: Import organization

- **What:** Imports organized in three groups separated by blank lines: (1) standard library, (2) third-party packages, (3) local/project imports. No wildcard imports (`from x import *`). No unused imports.
- **How:** `ruff check --select I` (isort rules for organization) + `ruff check --select F401` (unused imports). Ruff's formatter handles blank line separation automatically.
- **Why:** Consistent import organization makes dependency scanning instant — a glance at the import block reveals what the module depends on. Wildcard imports pollute the namespace and hide actual dependencies. (Sources: PEP 8 [S2], Ruff I rules [S18])
- **Classification:** TOOL (I + F401 rules)

### D5.3: Test quality

- **What:** Tests use specific assertions (`assert result.name == "expected"`, not `assert result is not None`). Test names describe behavior (`test_parse_jql_returns_empty_on_invalid_input`, not `test_parse`). Branch coverage >= 80%. Edge cases and error paths are tested, not just the happy path.
- **How:** `pytest --cov --cov-branch` for coverage measurement. Manual review for assertion specificity and test naming. `ruff check --select PT` for pytest style (PT009 assertEqual -> assert, PT018 composite assertions).
- **Why:** Vague assertions pass when the code is wrong. Behavior-spec naming makes test failures self-explanatory. Branch coverage ensures error handling and edge cases are exercised. (Sources: Augment [S15], Google [S5])
- **Classification:** BOTH (coverage + PT rules are TOOL; assertion quality and naming are HUMAN)

### D5.4: Commit discipline

- **What:** Each commit represents one logical change. Commit messages follow conventional format (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`). No mega-commits mixing features, fixes, and refactoring. Story commits reference the story ID.
- **How:** Manual review of git log. Pre-commit hook can enforce message format. CI can reject commits without conventional prefix.
- **Why:** Atomic commits enable `git bisect`, clean reverts, and meaningful changelogs. Mega-diffs are unreviewable and hide bugs in the noise. (Sources: DEV Community [S17], project convention)
- **Classification:** BOTH (message format is TOOL via pre-commit; commit granularity is HUMAN)

### D5.5: Pre-commit hooks

- **What:** Pre-commit runs: Ruff format, Ruff lint, Pyright type check. CI additionally runs: tests, coverage, import-linter. No code reaches `dev` without passing all gates.
- **How:** `.pre-commit-config.yaml` defines local hooks. CI pipeline configuration. `rai gate check --all` verifies all gates pass.
- **Why:** Automated gates catch issues at the earliest possible point. A developer who runs `git commit` gets instant feedback, not a CI failure 5 minutes later. (Sources: Augment [S15], project convention)
- **Classification:** TOOL (pre-commit + CI)

### D5.6: Dependency justification

- **What:** Every new third-party dependency added to `pyproject.toml` has a written rationale — either in the commit message, an ADR, or a comment in `pyproject.toml`. Dependencies must be actively maintained, have > 1000 GitHub stars or equivalent adoption evidence, and not duplicate existing functionality.
- **How:** Manual review of `pyproject.toml` changes. Check that new dependencies are justified. `pip-audit` for known vulnerability scanning.
- **Why:** Every dependency is a maintenance burden — security updates, breaking changes, transitive dependencies. The bar for adding one should be high. (Sources: Augment [S15])
- **Classification:** HUMAN

---

## Appendix A: AI-Generated Code Tells

*Patterns that signal "a machine wrote this, no human reviewed it." These are not errors per se, but their presence indicates lack of human judgment in the review process.*

### A1: Excessive obvious comments

- **Pattern:** Comments that restate the next line of code: `# Initialize the list` above `items = []`, `# Return the result` above `return result`.
- **Detection:** Manual review. More than 2 restatement comments per function is a strong signal.
- **Resolution:** Delete the comment. If the code needs explanation, explain WHY, not WHAT.

### A2: Generic names without domain language

- **Pattern:** Variables and functions named `data_handler`, `processed_item`, `result_value`, `input_data`, `output_list`, `temp_var`. No connection to the problem domain.
- **Detection:** Manual review. Check: could this name appear in any codebase, or is it specific to ours?
- **Resolution:** Rename using domain terminology: `backlog_item`, `jql_query`, `session_bundle`, `skill_definition`.

### A3: Old typing syntax on Python 3.10+

- **Pattern:** `from typing import List, Optional, Dict, Tuple, Set` when the project targets Python 3.10+. Use of `Optional[X]` instead of `X | None`.
- **Detection:** `ruff check --select UP006,UP007`. Grep for `from typing import` with deprecated names.
- **Resolution:** Replace with builtin generics (`list[str]`, `dict[str, int]`) and union syntax (`X | None`).

### A4: Monolithic functions

- **Pattern:** Functions exceeding 100 lines that fetch, transform, validate, and persist in a single body. Often with numbered comment sections (`# Step 1: ...`, `# Step 2: ...`).
- **Detection:** `ruff check --select C901` (cyclomatic complexity). Manual review for long functions with section comments.
- **Resolution:** Extract each step into a named function. The orchestrating function becomes a 10-line pipeline.

### A5: Vague test assertions

- **Pattern:** `assert result is not None`, `assert len(result) > 0`, `assert isinstance(result, dict)`. These pass for almost any non-trivial return value.
- **Detection:** Manual review of test files. Grep for `is not None`, `> 0`, `isinstance` in assert statements.
- **Resolution:** Assert specific values: `assert result.name == "expected_name"`, `assert len(result) == 3`, `assert result["key"] == "value"`.

### A6: Suspiciously uniform structure

- **Pattern:** Every class has exactly the same method layout. Every function has exactly one try/except. Every module has the same boilerplate. Real code has pragmatic compromises — some modules are simple, others complex.
- **Detection:** Manual review. Compare several modules — if they are structurally identical despite different purposes, human judgment was not applied.
- **Resolution:** Let each module's structure reflect its actual complexity. Simple modules should be short. Complex modules should have more structure. One size does not fit all.

---

## Appendix B: Summary

| Dimension | Criteria | TOOL | HUMAN | BOTH |
|-----------|----------|------|-------|------|
| D1: Correctness & Safety | 7 | 3 | 1 | 3 |
| D2: Readability & Idiom | 8 | 1 | 5 | 2 |
| D3: Type Safety & API Surface | 8 | 3 | 4 | 1 |
| D4: Architecture & Design | 8 | 2 | 4 | 2 |
| D5: Collaboration & Maintenance | 6 | 2 | 1 | 3 |
| **Total** | **37** | **11** | **15** | **11** |

---

## Appendix C: Audit Learnings (E370)

*What we learned from applying this standard to 28 modules and 444 source files.*

### Criteria that proved essential (strengthened)

- **D4.4 Single Responsibility** — The audit's highest-impact finding. God classes (builder.py at 1,569 lines, bundle.py at 821 lines) were the primary source of complexity. SRP decomposition produced the largest quality improvements.
- **D1.1 Exception handling** — Silent `except Exception` catches hid real bugs across 5 modules. Adding logging to catch-all handlers exposed issues that had been invisible.
- **D2.6 Domain naming** — Generic names (`data`, `handler`, `result`) appeared in 12 modules. Renaming to domain terms made code immediately more navigable.

### Criteria that proved impractical (relaxed)

- **D3.6 Flat API surface** — Full `__init__.py` re-exports create maintenance burden when modules change frequently. Applied selectively to stable public API modules only, not internal packages.
- **D2.4 Function size (40 lines)** — Some YAML/config parsing functions are necessarily long but simple (sequential field extraction). McCabe complexity ≤10 is the binding constraint; line count is advisory.

### Patterns discovered during refactoring

- Module-level Path constants as test seams (PAT-E-589) are an acceptable exception to D4.7 (no global mutable state)
- `yaml.safe_load()` + `cast()` is the standard pattern for pyright-strict YAML reading (PAT-E-658)
- State machine over regex for bulk test fixture migration (PAT-E-659)
- mock.patch targets import site, not definition site — patches survive module splits
- TDD RED phase catches fixture migration scope underestimates — count occurrences, not files

### Audit metrics

| Metric | Value |
|--------|-------|
| Modules audited | 28 |
| Source files | 444 (197 src + 247 tests) |
| Critical findings | 1 |
| Must-fix findings | 24 |
| Recommendations | 14 |
| Refactoring stories | 6 (S370.5a-f) |
| Lines reduced (God class) | builder.py 1,569 → 267 (-83%) |
| Lines reduced (Bundle) | bundle.py 821 → 323 (-61%) |

---

## References

- **Research report:** `work/research/code-quality-standards/code-quality-standards-report.md`
- **Evidence catalog:** `work/research/code-quality-standards/sources/evidence-catalog.md` (24 sources, 8 triangulated claims)
- **ADR-001:** `dev/decisions/adr-001-three-layer-architecture.md` (referenced in D4.1, D4.2, D4.8)
- **ADR-002:** `dev/decisions/adr-002-pydantic-everywhere.md` (referenced in D3.8)
- **Audit report:** `work/epics/e370-code-beauty-standards/audit-results.md`
- **Source notation:** [S1]-[S24] refer to the evidence catalog source index
