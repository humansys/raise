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
