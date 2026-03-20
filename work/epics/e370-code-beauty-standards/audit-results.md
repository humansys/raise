# Code Audit Results — raise-commons

**Date:** 2026-03-06
**Standard:** code-standards-draft.md (37 criteria, 5 dimensions)
**Criteria evaluated:** 26 (15 HUMAN + 11 BOTH)
**Scope:** 28 modules in `src/raise_cli/` + test sampling from `tests/`

---

## Executive Summary

The raise-commons codebase is in **good shape overall** — well-structured, strongly typed, and consistently using Pydantic at boundaries. The architectural patterns (Protocol + frozen dataclass + entry points, error isolation, module-level test seams) are sound and repeatable.

**Key numbers:**
- **28 modules** audited across 4 ADR-001 layers
- **1 critical** finding (GraphBuilder God Class in context/builder.py)
- **24 must-fix** findings (function size, exception broadness, SRP violations)
- **~30 should-fix** findings (API surface, domain purity, naming)
- **~30 info/nitpick** findings (documentation, conventions)
- **0 security** issues beyond what S370.2 Ruff S-rules already catch

**Recurring themes (systemic):**
1. **Function size** — 20+ functions exceed 40 lines, 8 exceed 100 lines. Most have `noqa: C901` acknowledgments.
2. **Domain purity** — Several domain modules perform direct file I/O. Pragmatic for a CLI tool but inconsistent with ADR-001.
3. **Flat API surface** — 5+ modules lack `__init__.py` re-exports, forcing deep imports.
4. **Exception broadness** — `except Exception` used in 15+ places; most are justified (error isolation) but some miss logging.

**Strongest areas:**
- Pydantic model usage (D3.8) — exemplary across all layers
- Type safety (D3) — Pyright strict mode + comprehensive annotations
- Test quality — specific assertions, behavior-spec naming, mock-free domain tests
- Exception hierarchy — `RaiError` base, contextual data, exit codes

---

## Layer Summary

| Layer | Modules | Pass | Partial | Fail | Critical | Must-Fix |
|-------|---------|------|---------|------|----------|----------|
| Core | 4 | 2 | 2 | 0 | 0 | 1 |
| Domain | 16 | 2 | 14 | 0 | 0 | 12 |
| Application | 6 | 2 | 3 | 1 | 1 | 5 |
| Presentation | 2 | 1 | 1 | 0 | 0 | 8 |
| **Total** | **28** | **7** | **20** | **1** | **1** | **26** |

---

## Core Layer

### Module: core/ (Core)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 2 |
| D3 Types & API | partial | 2 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Clean separation across three focused modules. `files.py` uses `frozenset` for immutable exclusions. `text.py` is pure-functional. `__init__.py` provides flat re-exports with `__all__`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 1 | D3.2 | should-fix | core/tools.py:122 | `run_tool(args: list[str])` — concrete list for read-only input | `Sequence[str]` |
| 2 | D2.7 | nitpick | core/text.py:163-172 | Comments explain WHAT not WHY in `sanitize_id` | Remove or consolidate |
| 3 | D2.2 | nitpick | core/tools.py:58-60 | `default_factory=lambda: list[str]()` — unusual | `default_factory=list` |

### Module: config/ (Core)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 2 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Pydantic `frozen=True` for `AgentConfig`. 3-tier YAML loading. Path-traversal protection. Well-designed exception hierarchy with exit codes, hints, and `to_dict()`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 4 | D1.1 | must-fix | config/settings.py:71 | `except Exception` in `TomlConfigSource.__call__` — silent, no logging | Add `logger.debug(...)` |
| 5 | D1.1 | should-fix | config/agent_registry.py:121 | Broad `except Exception` in plugin resolution — logged but could narrow | Narrow or justify |

### Module: schemas/ (Core)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | partial | 1 |

**Exemplary:** Textbook Pydantic. `JournalEntry`, `SessionState`, `CurrentWork` with field validators and StrEnum.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 6 | D3.6 | nitpick | schemas/__init__.py | No re-exports — forces deep imports | Add re-exports + `__all__` |

### Module: rai_base/ (Core)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Resource-distribution package. `__init__.py` includes `importlib.resources` usage example. Purely declarative.

---

## Domain Layer

### Module: backlog/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | partial | 1 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Exception chaining. Atomic write with `os.replace`. `SyncResult` Pydantic model.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 7 | D3.6 | should-fix | backlog/__init__.py | No re-exports | Add `SyncResult`, `sync_backlog` to `__init__.py` |
| 8 | D4.2 | should-fix | backlog/sync.py:104-115 | `_atomic_write` does file I/O in domain module | Document as application service or extract |

### Module: engines/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Note:** Effectively empty module (3-line `__init__.py`). Consider removing if unused.

### Module: tier/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | partial | 1 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `TierCapabilityError` with contextual data. Declarative `_CAPABILITY_TIER` mapping. StrEnum usage.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 9 | D3.6 | should-fix | tier/__init__.py | Empty — no re-exports | Add re-exports from `context.py` |

### Module: viz/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 1 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `__init__.py` properly re-exports with `__all__`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 10 | D4.2 | should-fix | viz/generator.py:361,404-405 | Direct file I/O in domain module | Refactor to accept data / return string |

### Module: telemetry/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `schemas.py` is model Pydantic — discriminated unions, Field descriptions, docstrings with examples. `writer.py` uses file locking for thread safety. Comprehensive `__init__.py` re-exports.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 11 | D4.2 | should-fix | telemetry/writer.py:73-124 | `emit()` does file I/O — inherent to purpose | Document as infrastructure, not pure domain |

### Module: discovery/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 1 |
| D2 Readability | partial | 2 |
| D3 Types & API | partial | 1 |
| D4 Architecture | partial | 2 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Comprehensive re-exports. Excellent Pydantic models in analyzer.py. Declarative category maps.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 12 | D2.4 | must-fix | discovery/scanner.py:467-570 | `walk()` inner function ~103 lines with `noqa: C901` | Extract node-type handlers |
| 13 | D2.4 | must-fix | discovery/scanner.py:598-663 | `_extract_php_signature` 66 lines, complexity 14 | Extract per-node-type handlers |
| 14 | D1.1 | should-fix | discovery/scanner.py:1613 | Broad `except Exception` — could mask bugs | Narrow or add debug logging |
| 15 | D4.4 | must-fix | discovery/scanner.py (1686 lines) | 3+ responsibilities: language extractors, directory walking, gitignore parsing | Split into sub-modules |

### Module: graph/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 2 |
| D5 Collaboration | pass | 0 |

**Exemplary:** DualWriteBackend is textbook composition (D4.5). Pending sync marker with Pydantic. Exception chaining in import guard.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 16 | D4.2 | should-fix | graph/backends/__init__.py:30 | `get_active_backend()` reads `os.environ` and `Path.cwd()` | Accept as parameters |
| 17 | D1.3 | should-fix | graph/api.py:41-45 | `httpx.Client` without `__enter__`/`__exit__` | Add context manager protocol |

### Module: memory/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 2 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Atomic file rewrite pattern (tmp+rename). Clean Pydantic models with `WriteResult`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 18 | D2.4 | must-fix | memory/migration.py:164 | `migrate_to_personal` 58 lines, complexity 11 | Extract per-data-type migration helper |
| 19 | D2.4 | must-fix | memory/writer.py:424-510 | `reinforce_pattern` ~87 lines | Extract `_read_records`, `_apply_vote`, `_atomic_rewrite` |

### Module: mcp/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Exemplary:** `bridge.py` is the standout — lazy session with reconnect, `subprocess.DEVNULL` WHY comment (RAISE-436), custom `McpBridgeError`, optional telemetry via `contextlib.nullcontext()`, thorough async cleanup.

### Module: artifacts/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Pydantic model validators for governance rules in `story_design.py`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 20 | D4.7 | should-fix | artifacts/reader.py:12-24 | Module-level mutable `_artifact_registry` with `global` | Use `functools.lru_cache` or class-level |

### Module: skills/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Best SRP decomposition of all modules — 7 files, each single-responsibility. `SkillLocator` accepts `skill_dir` in constructor (testable). `NameCheckResult.is_valid` computed property.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 21 | D4.2 | should-fix | skills/name_checker.py:175-178 | `check_name()` calls `Path.cwd()` internally | Accept `skill_dir` as parameter |

### Module: gates/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Exemplary:** DRY `_runner.py` shared helper. Protocol + frozen dataclass + entry points is clean. Thin gate implementations are maximally declarative.

### Module: doctor/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Pipeline ordering with critical failure cascade. `register_fix` decorator. `CheckResult` with `fix_id` + `fix_hint`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 22 | D4.7 | must-fix | doctor/fix.py:21 | `FIX_REGISTRY: dict` module-level mutable global | Class-based registry or document pattern |

### Module: hooks/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 1 |
| D2 Readability | partial | 1 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Typed event hierarchy with Literal names. Error isolation consistently applied. `_check_abort` separation.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 23 | D1.3 | must-fix | hooks/emitter.py:130 | `ThreadPoolExecutor` created per hook call, potential thread leak on timeout | Create once in `__init__` or use context manager |
| 24 | D2.4 | must-fix | hooks/builtin/backlog.py:142-216 | `handle()` 75 lines, complexity 14 | Extract `_handle_start()` and `_handle_complete()` |

### Module: adapters/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 2 |
| D3 Types & API | pass | 0 |
| D4 Architecture | pass | 0 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Well-layered adapter architecture: Protocols → Models → Sync wrappers → Implementations. Declarative YAML-driven MCP integration.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 25 | D2.4 | must-fix | adapters/mcp_jira.py:301-353 | `_parse_issue_detail` 52 lines, duplicated format branching | Extract format handlers |
| 26 | D2.4 | must-fix | adapters/mcp_jira.py:383-419 | `_parse_search_results` duplicates flat/nested branching | Share with #25 |

### Module: governance/ (Domain)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 2 |
| D2 Readability | partial | 4 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 2 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Pydantic models with validators. StrEnum for ConceptType. Consistent parser structure. Thorough docstrings.

**Note:** This module enforces code quality — it should lead by example. The 5 functions with `noqa: C901` are a notable gap.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 27 | D1.1 | must-fix | governance/extractor.py:243+ | 9 bare `except Exception` in legacy path without justification | Add `noqa: BLE001` or narrow |
| 28 | D1.1 | should-fix | governance/guardrails.py:41 | `except Exception:` without binding — silent swallow | Bind and log at debug |
| 29 | D2.4 | must-fix | governance/extractor.py:222 | `extract_with_result` ~103 lines, complexity 14 | Extract per-artifact helpers |
| 30 | D2.4 | must-fix | governance/epic.py:178 | `extract_stories` ~125 lines | Extract `_resolve_story_columns()` |
| 31 | D2.4 | must-fix | governance/backlog.py:210 | `extract_epics` ~126 lines | Extract dedup check |
| 32 | D4.4 | must-fix | governance/extractor.py:222-325 | `extract_with_result` has 5 responsibilities | Split into discovery + extraction + assembly |
| 33 | D4.5 | should-fix | governance/parsers/ | 8 Parser classes share no Protocol/ABC | Define `GovernanceParser` Protocol |
| 34 | D2.5 | should-fix | governance/backlog.py:285-295 | Nesting depth 4 | Extract to named predicate |

---

## Application Layer

### Module: session/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | pass | 0 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `resolver.py` — clean validation with CWE-23 security note. `journal.py` — append-only semantics.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 35 | D4.4 | must-fix | session/bundle.py (821 lines) | Mixes data fetching + formatting + assembly — 3 responsibilities | Split into `bundle_formatters.py`, `bundle_data.py`, `bundle.py` |

### Module: context/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 1 |
| D3 Types & API | pass | 0 |
| D4 Architecture | fail | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `diff.py` — clean Pydantic models, frozen constants, deterministic output. `analyzers/` — textbook Protocol + implementation.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 36 | D4.4 | **critical** | context/builder.py (1,539 lines) | **God Class.** GraphBuilder loads 7 data sources, infers relationships, extracts structural nodes. 25+ methods. | Decompose into loader classes + thin orchestrator |
| 37 | D2.4 | must-fix | context/builder.py:877-1020 | `_extract_bounded_contexts` ~143 lines | Extract `_create_bc_node_and_edges` helper |

### Module: onboarding/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | pass | 0 |
| D2 Readability | partial | 1 |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 1 |
| D5 Collaboration | pass | 0 |

**Exemplary:** `skill_manifest.py` — dpkg three-hash algorithm. `conventions.py` — confidence calculation with edge cases. `profile.py` — immutable updates via `model_copy`.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 38 | D2.4/A4 | must-fix | onboarding/skills.py:174-437 | `scaffold_skills` ~260 lines, `noqa: C901` | Extract `_handle_conflict`, `_handle_auto_update` helpers |
| 39 | D4.4 | must-fix | onboarding/instructions.py:348-563 | `_add_cli_reference_section` 216 lines of hardcoded text | Move to static resource file |

### Module: handlers/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Note:** Empty placeholder module.

### Module: publish/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Exemplary:** Cleanest module in the audit. `version.py` — frozen dataclass with `__str__`, pure functions. `changelog.py` — minimal and correct.

### Module: agents/ (Application)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 1 |
| D2-D5 | pass | 0 |

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 40 | D1.1 | must-fix | agents/copilot_plugin.py:113 | `except Exception` in `_read_frontmatter` — silent (PAT-E-598) | Narrow to `(yaml.YAMLError, OSError)`, log at debug |

---

## Presentation Layer

### Module: cli/ (Presentation)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1 Correctness | partial | 2 |
| D2 Readability | partial | 8+ |
| D3 Types & API | pass | 0 |
| D4 Architecture | partial | 2 |
| D5 Collaboration | pass | 0 |

**Exemplary:** Consistent delegation pattern — CLI parses args and delegates. `error_handler.py` — clean human/JSON separation. `_resolve.py` — generic resolver. Deprecation aliases with migration warnings. `Annotated` type aliases for common options.

#### Findings

| # | Criterion | Severity | File:Line | Description | Fix |
|---|-----------|----------|-----------|-------------|-----|
| 41 | D2.4/A4 | must-fix | cli/commands/init.py:434 | `init_command` 321 lines — largest function | Extract profile/manifest/scaffold phases |
| 42 | D2.4/A4 | must-fix | cli/commands/session.py:293 | `close` 236 lines | Extract legacy/structured paths |
| 43 | D2.4/A4 | must-fix | cli/commands/signal.py:42 | `emit_work` 177 lines | Extract validation/event/output |
| 44 | D2.4/A4 | must-fix | cli/commands/session.py:88 | `start` 152 lines | Extract profile/session/context |
| 45 | D2.4/A4 | must-fix | cli/commands/init.py:174 | `_get_project_message` 147 lines | Split SHU/RI builders |
| 46 | D2.4/A4 | must-fix | cli/commands/discover.py:405 | `drift_command` 147 lines | Extract baseline loading |
| 47 | D2.4/A4 | must-fix | cli/commands/release.py:198 | `publish_command` 141 lines | Extract git operations |
| 48 | D2.4/A4 | must-fix | cli/commands/graph.py:67 | `query` 139 lines | Extract arg parsing |
| 49 | D4.4 | should-fix | cli/commands/graph.py (1087 lines) | Formatting functions should be in `output/formatters/` | Move 5 `_format_*` functions |
| 50 | D4.7 | should-fix | cli/main.py:35 | `_current_output_format` module-level mutable global | Route through `ctx.obj` exclusively |

### Module: output/ (Presentation)

| Dimension | Verdict | Findings |
|-----------|---------|----------|
| D1-D5 | pass | 0 |

**Exemplary:** `OutputConsole` — format-aware output with test seam. Formatter functions are pure. TYPE_CHECKING imports keep dependency direction correct.

---

## Test Quality Sampling

**Overall assessment: HIGH quality.** 20+ test files sampled across all layers.

| Area | Verdict | Notes |
|------|---------|-------|
| Naming | pass | Behavior-spec names throughout, minor exceptions in gate tests |
| Assertions | pass | Specific value assertions, only 1 vague `or` assertion found |
| Edge cases | pass | Backward compat, error paths, security (CWE-23) |
| Structure | pass | Clean AAA, minimal fixtures |
| Mock usage | pass | Mock-free domain tests, mocks only at boundaries |

**Minor findings:**
- `tests/test_gates/test_builtin_gates.py`: Generic `test_pass`/`test_fail` naming; repetitive mock-patch blocks across 5 gate classes
- `tests/discovery/test_scanner.py`: Construction-focused names instead of behavior-spec
- `tests/cli/commands/test_skill.py:129`: One vague `or` assertion

---

## Systemic Patterns

### SYS-1: Function size (D2.4) — 20+ violations across all layers

**Affected:** cli/ (8 functions >100 lines), governance/ (5 functions), discovery/ (3 functions), onboarding/ (2), session/ (1), memory/ (2), hooks/ (1), adapters/ (2)

**Pattern:** Long sequential functions that combine validation + domain call + formatting. Most have `noqa: C901` acknowledging the issue.

**Root cause:** Functions grew organically as features were added. The `noqa: C901` with "defer to S370.5" comments are honest but accumulated.

**Fix strategy:** Extract into named helper functions. For CLI commands: separate validation, domain delegation, and output formatting. This is the #1 refactoring priority for S370.5.

### SYS-2: Domain purity (D4.2) — 7 modules with I/O in domain layer

**Affected:** backlog/, viz/, telemetry/, graph/, skills/, discovery/, governance/

**Pattern:** Domain modules perform direct file I/O via `Path.read_text()`, `Path.write_text()`, `Path.cwd()`, or `os.environ`.

**Root cause:** Pragmatic for a CLI tool — some modules (telemetry writer, viz generator) exist specifically to do I/O. Others (skills/name_checker, graph/backends) bake `Path.cwd()` defaults into domain functions.

**Fix strategy:** For functions that bake CWD defaults: accept as parameter with default. For I/O-purpose modules (telemetry, viz): document architectural decision. Don't over-refactor — this is a CLI, not a library.

### SYS-3: Flat API surface (D3.6) — 5 modules lack re-exports

**Affected:** schemas/, backlog/, tier/, engines/, (partially) governance parsers

**Pattern:** `__init__.py` is empty or just a docstring. Consumers must use deep imports.

**Fix strategy:** Quick wins — add re-exports + `__all__` to each `__init__.py`. < 1 hour total.

### SYS-4: Exception broadness (D1.1) — 15+ `except Exception` across codebase

**Affected:** config/settings.py (silent), governance/extractor.py (9 legacy), agents/copilot_plugin.py (silent), cli/ (various)

**Pattern:** Most are intentional error isolation (hooks, entry points, YAML parsing). Problem cases are those that catch silently without logging.

**Fix strategy:** Audit each `except Exception` — if it logs, add justification comment. If silent, add `logger.debug()`. Narrow where possible.

---

## Exemplary Code

These modules and patterns should serve as templates for the rest of the codebase:

| Module | What's exemplary | Pattern |
|--------|-----------------|---------|
| `mcp/bridge.py` | Lazy session, reconnect, WHY comments, custom exception, async cleanup | Application service with resilience |
| `publish/` | Cleanest module — frozen dataclasses, pure functions, focused files | Value objects + pure domain |
| `skills/` | Best SRP decomposition — 7 files, each single-responsibility | Module structure |
| `telemetry/schemas.py` | Discriminated unions, Field descriptions, docstrings with examples | Pydantic model design |
| `tier/context.py` | Custom exception with contextual data, declarative mapping | Domain exception + config-as-data |
| `output/` | Pure formatters, test seam singleton, TYPE_CHECKING imports | Presentation layer |
| `gates/` | Protocol + frozen dataclass + entry points, DRY runner | Plugin architecture |
| `hooks/` | Typed events, error isolation, never-crash pattern | Event system |

---

## Recommendations

### Quick Wins (< 1 hour each)

| # | Description | Modules | Effort |
|---|-------------|---------|--------|
| R1 | Add `__init__.py` re-exports to 5 modules | schemas, backlog, tier, engines | 30 min |
| R2 | Add `logger.debug()` to silent `except Exception` catches | config/settings.py, agents/copilot_plugin.py | 15 min |
| R3 | Move graph formatting functions to `output/formatters/graph.py` | cli/graph.py, output/ | 30 min |
| R4 | Remove `_current_output_format` global, use `ctx.obj` only | cli/main.py | 15 min |

### Medium Effort (1-4 hours each)

| # | Description | Modules | Effort |
|---|-------------|---------|--------|
| R5 | Extract CLI command functions into helper functions (top 8 by size) | cli/init.py, session.py, signal.py, graph.py, discover.py, release.py | 3-4 hr |
| R6 | Extract governance parser helpers for functions >100 lines | governance/extractor.py, epic.py, backlog.py | 2-3 hr |
| R7 | Split discovery/scanner.py into language-specific sub-modules | discovery/ | 2-3 hr |
| R8 | Add `GovernanceParser` Protocol, justify legacy `except Exception` | governance/ | 1-2 hr |
| R9 | Fix hooks/emitter.py ThreadPoolExecutor lifecycle | hooks/ | 1 hr |
| R10 | Extract adapters/mcp_jira.py format handlers, DRY flat/nested branching | adapters/ | 1-2 hr |

### Significant Refactoring (story-level)

| # | Description | Modules | Effort |
|---|-------------|---------|--------|
| R11 | **Decompose context/builder.py God Class** into loader classes + orchestrator | context/ | Full story (L) |
| R12 | Split session/bundle.py into formatters + data + assembly | session/ | M story |
| R13 | Split onboarding/skills.py scaffold_skills into conflict handlers | onboarding/ | M story |
| R14 | Move onboarding/instructions.py CLI reference to resource file | onboarding/ | S story |
