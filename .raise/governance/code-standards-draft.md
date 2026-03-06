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
