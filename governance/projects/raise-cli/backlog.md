# Backlog: raise-cli

> **Status**: Draft
> **Date**: 2026-01-30
> **Version**: 1.0.0
> **Related**: PRD v1.1.0, Vision v1.0.0, Design v1.1.0

---

## 1. Epics Overview

| ID | Epic | Objective | Design Ref | Priority | MVP |
|----|------|-----------|------------|----------|-----|
| E1 | **Core Foundation** | CLI skeleton, config, error handling | Design §2-4 | P0 | ✓ |
| E2 | **Governance Toolkit** | Concept extraction, graph building, MVC queries | ADR-011, ADR-012 | P0 | ✓ |
| ~~E3~~ | ~~**Gate Engine**~~ | ~~Merged into E2~~ | ~~See ADR-012~~ | ~~P0~~ | |
| E4 | **Context Generation** | Generate CLAUDE.md from governance graph | PRD RF-05, ADR-011 | P1 | ✓ |
| E5 | **SAR Engine** | Brownfield codebase analysis | PRD RF-06 | P1 | |
| E6 | **Observability** | Track metrics, generate reports | PRD RF-07 | P2 | |
| E7 | **Distribution** | Agent Skill, packaging, docs | PRD RF-08 | P1 | ✓ |

**MVP Scope**: E1, E2, E4, E7 (core governance + distribution)

**Note:** E3 (Gate Engine) merged into E2 per ADR-012. Validation via skills + toolkit.

---

## 2. Features by Epic

### E1: Core Foundation

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F1.1 | **Project Scaffolding** | Set up package structure, pyproject.toml, entry points | 3 | ✓ |
| F1.2 | **CLI Skeleton** | Typer app with global options (-v, -q, --format) | 5 | ✓ |
| F1.3 | **Configuration System** | Pydantic Settings with cascade (CLI > env > file) | 5 | ✓ |
| F1.4 | **Exception Hierarchy** | Centralized errors with exit codes and Rich output | 3 | ✓ |
| F1.5 | **Output Module** | Formatters (human, json, table) + Rich console | 3 | ✓ |
| F1.6 | **Core Utilities** | Subprocess wrappers (git, ast-grep, ripgrep) | 3 | ✓ |

**Epic Total**: 22 SP

### E2: Governance Toolkit ⚡ UPDATED

**Architecture:** Skills + CLI Toolkit (per ADR-011, ADR-012)
- **Skills execute** processes (katas, gates) by reading markdown guides
- **CLI provides** deterministic data extraction and validation
- **Concept graph** enables 97% token savings via MVC queries

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F2.1 | **Concept Extraction** | Parse requirements (PRD), outcomes (Vision), principles (Constitution) | 3 | ✓ |
| F2.2 | **Graph Builder** | Build concept graph with relationships, serialize to JSON/YAML | 2 | ✓ |
| F2.3 | **MVC Query Engine** | Graph traversal, concept aggregation, fallback to file-level | 2 | ✓ |
| F2.4 | **CLI Commands** | `raise graph build`, `raise context query`, `raise validate structure` | 2 | ✓ |

**Epic Total**: 9 SP (85% reduction from original 60 SP)

**Rationale:** Experiments showed:
- Concept-level graph: 97% token savings (vs 50% for file-level)
- Skills + toolkit: 85% scope reduction (vs engines)
- Proven feasible: Spike extracted 23 concepts, 11 relationships
- See: `dev/experiments/`, ADR-011, ADR-012

### ~~E3: Gate Engine~~ ⚠️ DEPRECATED

**Status:** Merged into E2 per ADR-012

**Rationale:**
- Gates work as skills (e.g., `/validate-prd`)
- Skills call CLI toolkit for deterministic checks
- No separate engine needed
- Same functionality, simpler architecture

**Migration:**
- Gate definitions → Skills in `.claude/skills/`
- Gate validation → `raise validate` CLI commands
- Gate execution → Skills guide Claude through validation

### E4: Context Generation

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F4.1 | **Governance Loader** | Load constitution, guardrails, vision from governance/ | 3 | ✓ |
| F4.2 | **CLAUDE.md Generator** | Produce CLAUDE.md from governance artifacts | 5 | ✓ |
| F4.3 | **Cursorrules Generator** | Produce .cursorrules from guardrails | 3 | |
| F4.4 | **Context Handler** | Orchestrate generation with format selection | 3 | ✓ |

**Epic Total**: 14 SP (MVP: 11 SP)

### E5: SAR Engine (Brownfield Analysis)

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F5.1 | **Directory Walker** | Scan codebase structure, respect .gitignore | 3 | |
| F5.2 | **Technology Detector** | Identify stack from file patterns | 5 | |
| F5.3 | **ast-grep Integration** | Extract code patterns (classes, functions) | 8 | |
| F5.4 | **ripgrep Integration** | Search for technology indicators | 5 | |
| F5.5 | **SAR Report Generator** | Produce structured SAR output | 5 | |
| F5.6 | **SAR Handler** | Orchestrate analysis with graceful degradation | 3 | |

**Epic Total**: 29 SP (not in MVP)

### E6: Observability

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F6.1 | **Metrics Collector** | Record execution metrics to JSON | 3 | |
| F6.2 | **Metrics Storage** | XDG-compliant data directory | 2 | |
| F6.3 | **Metrics Reporter** | Generate summary reports | 5 | |
| F6.4 | **Metrics Export** | Export to JSON/CSV formats | 3 | |

**Epic Total**: 13 SP (not in MVP)

### E7: Distribution

| ID | Feature | Description | Story Points | MVP |
|----|---------|-------------|--------------|-----|
| F7.1 | **Agent Skill** | Create raise/SKILL.md following Anthropic spec | 2 | ✓ |
| F7.2 | **Package Metadata** | Complete pyproject.toml for PyPI | 2 | ✓ |
| F7.3 | **Shell Completion** | Bash/Zsh/Fish completions | 3 | |
| F7.4 | **README & Docs** | User documentation | 5 | ✓ |

**Epic Total**: 12 SP (MVP: 9 SP)

---

## 3. MVP Summary

| Epic | Features | Story Points | Status |
|------|----------|--------------|--------|
| E1 Core Foundation | F1.1-F1.6 | 22 | ✅ Complete |
| E2 Governance Toolkit | F2.1-F2.4 | 9 | 🔄 Next |
| ~~E3 Gate Engine~~ | ~~Merged into E2~~ | ~~-51~~ | ⚠️ Deprecated |
| E4 Context Generation | F4.1, F4.2, F4.4 | 11 | Pending |
| E7 Distribution | F7.1, F7.2, F7.4 | 9 | Pending |
| **MVP Total** | **17 features** | **51 SP** | |

**Scope reduction:** 92 SP → 51 SP (45% reduction, 6 weeks saved)

**Post-MVP**: E5 (SAR - 29 SP), E6 (Observability - 13 SP), F4.3, F7.3 = 45 SP

**Total Project**: 96 SP (was 150 SP)

**Updated:** 2026-01-31 per ADR-011, ADR-012

---

## 4. Dependencies

```
F1.1 ──▶ F1.2 ──▶ F1.3 ──▶ F1.4 ──▶ F1.5
                    │
                    ▼
              ┌─────┴─────┐
              ▼           ▼
           F2.1        F3.1
              │           │
              ▼           ▼
           F2.2        F3.2
              │           │
              ▼           ▼
           F2.3        F3.3
              │           │
              ▼           ▼
           F2.4        F3.4
              │           │
              ▼           ▼
           F2.5        F3.5
              │           │
              └─────┬─────┘
                    ▼
                  F4.1
                    │
                    ▼
                  F4.2
                    │
                    ▼
                  F7.1 ──▶ F7.2 ──▶ F7.4
```

| Blocker | Blocked | Type | Reason |
|---------|---------|------|--------|
| F1.2 | F2.*, F3.* | Technical | CLI skeleton required |
| F1.3 | F2.*, F3.*, F4.* | Technical | Config system required |
| F1.4 | All features | Technical | Error handling required |
| F2.1 | F2.2-F2.5 | Technical | Parser needed first |
| F3.1 | F3.2-F3.5 | Technical | Parser needed first |
| F2.5, F3.5 | F4.1 | Technical | Engines must work before context |

---

## 5. User Stories (MVP Features)

### F1.2: CLI Skeleton

**US-1.2.1**: Basic CLI invocation
```
As a RaiSE Engineer
I want to run `raise --version` and `raise --help`
So that I can verify the CLI is installed correctly

Acceptance Criteria:
- Given raise-cli is installed
- When I run `raise --version`
- Then I see the version number (e.g., "raise-cli 2.0.0")

- Given raise-cli is installed
- When I run `raise --help`
- Then I see available commands and global options
```
**SP**: 2

**US-1.2.2**: Global options
```
As a RaiSE Engineer
I want to use --format, -v, -q options on any command
So that I can control output format and verbosity

Acceptance Criteria:
- Given any raise command
- When I add `--format json`
- Then output is valid JSON

- Given any raise command
- When I add `-q` (quiet)
- Then only errors are shown
```
**SP**: 3

### F2.2: Kata Discovery

**US-2.2.1**: List katas
```
As a RaiSE Engineer
I want to run `raise kata list`
So that I can see available governance katas

Acceptance Criteria:
- Given .raise/katas/ contains kata definitions
- When I run `raise kata list`
- Then I see a list of katas with id, name, work_cycle

- Given --format json
- When I run `raise kata list --format json`
- Then output is valid JSON array of kata objects
```
**SP**: 3

### F2.4: Kata Executor

**US-2.4.1**: Execute kata
```
As a RaiSE Engineer
I want to run `raise kata run project/discovery`
So that I can execute a governance kata with guidance

Acceptance Criteria:
- Given kata "project/discovery" exists
- When I run `raise kata run project/discovery`
- Then I see each step with instructions and verification

- Given kata has prerequisites not met
- When I run the kata
- Then I see an error with hint about prerequisites
```
**SP**: 5

**US-2.4.2**: Track kata state
```
As a RaiSE Engineer
I want kata execution state to persist
So that I can resume interrupted katas

Acceptance Criteria:
- Given I start a kata and stop midway
- When I run the same kata again
- Then I'm prompted to resume or restart
```
**SP**: 3

### F3.4: Gate Executor

**US-3.4.1**: Check gate
```
As a RaiSE Engineer
I want to run `raise gate check gate-discovery --artifact prd.md`
So that I can validate my artifact against governance criteria

Acceptance Criteria:
- Given gate "gate-discovery" exists and artifact path is valid
- When I run the gate check
- Then I see pass/fail for each criterion with details

- Given all required criteria pass
- When gate check completes
- Then exit code is 0

- Given any required criterion fails
- When gate check completes
- Then exit code is 10 (GateFailedError)
```
**SP**: 5

### F4.2: CLAUDE.md Generator

**US-4.2.1**: Generate context
```
As a RaiSE Engineer
I want to run `raise context generate`
So that I can produce CLAUDE.md for AI assistants

Acceptance Criteria:
- Given governance/ contains vision.md, guardrails.md
- When I run `raise context generate`
- Then CLAUDE.md is created/updated in project root

- Given CLAUDE.md is generated
- When I read the file
- Then it contains constitution, guardrails, project context
```
**SP**: 5

---

## 6. Estimation Summary

| Category | Story Points | % of Total |
|----------|--------------|------------|
| MVP | 92 | 61% |
| Post-MVP | 58 | 39% |
| **Total** | **150** | **100%** |

### Suggested Sprint Allocation (assuming 20 SP/sprint)

| Sprint | Features | Focus |
|--------|----------|-------|
| 1 | F1.1-F1.6 | Core Foundation |
| 2 | F2.1-F2.3 | Kata Parser + Discovery + State |
| 3 | F2.4-F2.5, F3.1-F3.2 | Kata Executor, Gate Parser |
| 4 | F3.3-F3.5 | Gate Validation |
| 5 | F4.1-F4.2, F4.4 | Context Generation |
| 6 | F7.1-F7.2, F7.4 | Distribution + Launch |

**MVP Timeline**: ~6 sprints

---

## 7. Definition of Done

Each feature is complete when:

- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on feature)
- [ ] Integration tests for CLI commands
- [ ] Error handling with proper exception types
- [ ] Documentation (docstrings, --help text)
- [ ] Code passes `ruff check` and `pyright --strict`
- [ ] PR reviewed and approved

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Kata parsing complexity | Medium | Start with simple katas, iterate |
| Gate validation edge cases | Medium | BDD tests for all criteria types |
| ast-grep/ripgrep not available | Low | Graceful degradation already designed |
| Scope creep (MCP, SaaS) | High | Strict MVP boundary, defer to v2.x |

---

## 9. Traceability

| PRD Requirement | Feature(s) |
|-----------------|------------|
| RF-01 Kata Engine | F2.1-F2.6 |
| RF-02 Gate Engine | F3.1-F3.6 |
| RF-03 Commands Library | F1.6 |
| RF-04 Template Scaffolding | (deferred, use manual for v2.0) |
| RF-05 Context Generation | F4.1-F4.4 |
| RF-06 SAR Analysis | F5.1-F5.6 |
| RF-07 Observability | F6.1-F6.4 |
| RF-08 Agent Skill | F7.1 |

---

## 10. Approvals

| Role | Name | Date | Status |
|------|------|------|--------|
| Product Owner | Emilio Osorio | 2026-01-30 | Pending |

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Initial backlog |

---

*Generated by: `project/backlog` kata*
*Template: backlog v1*
