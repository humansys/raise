---
title: "Quality Review Skill — Evidence Catalog"
created: "2026-02-22"
session: "SES-246"
status: "complete"
research_questions: 4
---

# Evidence Catalog: Quality Review Skill

## RQ1: What do code reviewers find that linters miss?

### Key Claims

**Claim 1.1: Semantic bugs = 51% of all missed bugs. Linters catch 0%.**
- Evidence: Very High (peer-reviewed, SmartSHARK dataset, 187 bugs in 173 PRs)
- Source: arxiv 2205.09428 (ICSE)
- Categories: wrong algorithm, incorrect business logic, off-by-one, wrong variable, inverted conditions, missing edge cases

**Claim 1.2: LLM reviewers detect logic/correctness errors, cross-file implications, architectural drift**
- Evidence: High (CodeRabbit, Amazon CodeGuru, independent benchmarks)
- Bug catch rates vary 6-82% across tools (Greptile benchmark, July 2025)

**Claim 1.3: AI-generated code has 1.7x more issues than human code**
- Evidence: High (CodeRabbit analysis, 470 PRs)
- 1.75x logic errors, 1.64x quality errors, 1.57x security findings

**Claim 1.4: The specific anti-patterns we found are well-documented but tool-invisible**
- Type lies: pyright can't detect semantically wrong annotations
- Tautological tests: 5+ independent practitioner sources (Rainsberger, Coulman, Williams, Codepipes, yegor256)
- Mock-implementation coupling: "Inspector" anti-pattern — test tests the mocks, not the system
- Magic number assertions: special case of "never calculate expected values in tests"

### Taxonomy for review (from RQ1)

| Tier | What to check | Example |
|------|---------------|---------|
| 1. Semantic correctness | Type lies, wrong logic, missing edge cases, inverted conditions | `dict[str, type]` when `ep.load()` returns `Any` |
| 2. Test quality | Tautological, mock-coupled, inspector, magic numbers | `assert EP_X == "literal"` |
| 3. Design & evolvability | API ergonomics, naming, responsibility, DRY, coupling | Leaky abstractions |
| 4. Cross-cutting | Error handling, security context, concurrency, architectural drift | Swallowed exceptions |

---

## RQ2: Python OSS code review checklists (partial)

### Key Claims

**Claim 2.1: "Keep APIs lean — expose only what callers need"**
- Evidence: High (Real Python best practices)
- `__all__` declares intent but doesn't enforce access control

**Claim 2.2: Kedro uses identical entry point pattern (importlib_metadata + auto-discovery)**
- Evidence: High (Kedro docs)
- Plugin hooks registered via EntryPoints API, auto-discovery by default

**Claim 2.3: vintasoftware Python API checklist (PyCon 2017) is canonical reference**
- Evidence: Medium (334 stars, MIT, community reference)
- Source: github.com/vintasoftware/python-api-checklist

---

## RQ3: Test value vs test muda

### Key Claims

**Claim 3.1: Line coverage is a weak proxy for fault detection**
- Evidence: High (Papadakis ICSE 2018, Jain "Oracle Gap", AST 2024)
- Coverage measures execution, not testedness. 100% coverage with zero assertions is possible.

**Claim 3.2: Mutation testing is better (though imperfect)**
- Evidence: High (Google ICSE 2021, ~15M mutants analyzed)
- Google surfaces surviving mutants during code review, not as CI gate
- Python tools: mutmut (most active), cosmic-ray (distributed)

**Claim 3.3: Coverage targets cause perverse incentives**
- Evidence: High (Google Testing Blog evolved from "80% gate" in 2010 to "qualitative signal" in 2020)
- Fowler (2021): rejects fixed test pyramid ratios

**Claim 3.4: "Test behavior, not implementation" is the consensus**
- Evidence: Very High (Beck + Fowler + Cooper + Google — 4 independent sources, 20+ years)
- Kent Beck: "trigger for a new test is a new behavior, not a new function"
- Ian Cooper: "you cannot refactor if you have implementation details in your tests"

### 7 Heuristics for the review prompt

| # | Name | Question | Detects |
|---|------|----------|---------|
| 1 | Mutation Survival | "If I changed the behavior, would this test fail?" | Constant assertions, tautological tests |
| 2 | Refactoring Resilience | "If I refactored internals, would this test break?" | Mock-coupled, implementation-dependent tests |
| 3 | Behavior Specification | "Does this test name describe a behavior or a structural element?" | Coverage-padding tests |
| 4 | Magic Literal | "Is this assertion against a literal copied from implementation?" | `assert X == "literal"`, `len() == N` |
| 5 | Mock Depth | "Does the test mock more than one layer? Does mock setup encode impl knowledge?" | Over-mocked tests |
| 6 | Deletion | "If I deleted this test, what bug could escape that no other test catches?" | Redundant, duplicate tests |
| 7 | Specification Independence | "Can I write this assertion from the requirements alone, without reading impl?" | Tautological tests |

---

## RQ4: importlib.metadata security risks

### Key Claims

**Claim 4.1: Any installed package can register entry points in ANY group**
- Evidence: Very High (Python Packaging spec, no access control on groups)
- Attack: `pip install malicious-package` → appears in `entry_points(group="rai.adapters.pm")`

**Claim 4.2: Checkmarx documented "Command-Jacking" via entry points (Oct 2024)**
- Evidence: High (Checkmarx research, Yehuda Gelb & Elad Rapaport)
- Source: checkmarx.com/blog/this-new-supply-chain-attack-technique-can-trojanize-all-your-cli-commands/
- Mechanism identical for custom groups like ours

**Claim 4.3: `ep.load()` executes arbitrary code (no sandboxing possible in Python)**
- Evidence: Very High (CPython source verified)
- `import_module()` runs all module-level code
- Python in-process sandboxing is impossible (rexec/Bastion removed in 2.3+)

**Claim 4.4: `ep.load()` can raise 5+ exception types, not just ImportError**
- Evidence: High (CPython source)
- ModuleNotFoundError, ImportError, AttributeError, SyntaxError, any Exception from module-level code
- Our `except Exception` is correct (stevedore uses same pattern)

**Claim 4.5: No major Python project implements entry-point allowlists**
- Evidence: Medium (negative evidence — pytest, stevedore, pip, tox all load unconditionally)
- Industry norm: "if installed, trusted"

### Recommendations (priority order)
1. Document trust model (now) — entry points inherit pip install trust boundary
2. Log `ep.dist.name` for traceability (easy win)
3. Add Protocol conformance check after `isclass()` (future story)
4. Consider optional allowlist (future — would be first-in-ecosystem)

---

## Sources (deduplicated)

### Peer-reviewed
- arxiv 2205.09428 — Which bugs are missed in code reviews (ICSE)
- Papadakis et al. ICSE 2018 — Mutation scores and real fault detection
- Petrovic et al. ICSE 2021 — Does mutation testing improve practices (Google)
- Garousi et al. JSS 2018 — Test smells multivocal literature review (166 sources)
- Jain et al. — The Oracle Gap

### Industry
- Google Testing Blog (2013, 2020, 2021) — Test behavior, coverage practices, mutation testing
- Checkmarx (Oct 2024) — Command-Jacking via entry points
- CodeRabbit — AI vs human code generation report (470 PRs)
- Greptile — AI code review benchmarks (July 2025)
- stevedore — OpenStack entry point management

### Practitioner
- Kent Beck, Martin Fowler, Ian Cooper, J.B. Rainsberger — TDD and test quality
- Real Python — Public API surface best practices
- testsmells.org — Test smell catalog
- vintasoftware — Python API checklist (PyCon 2017)
