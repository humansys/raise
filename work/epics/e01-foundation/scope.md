# Epic E1: Core Foundation - Scope

> Branch: `epic/e1-core-foundation`
> Created: 2026-01-31
> Target: Feb 9, 2026 (Friends & Family pre-launch)

---

## Objective

Build the foundational CLI infrastructure: package structure, command framework, configuration system, error handling, and output formatting.

---

## Features (22 SP)

| ID | Feature | SP | Status | Actual Time |
|----|---------|----|----|-------------|
| F1.1 | Project Scaffolding | 3 | ✓ Complete | ~30min |
| F1.2 | CLI Skeleton | 5 | ✓ Complete | ~45min |
| F1.3 | Configuration System | 5 | ✓ Complete | 20min |
| F1.4 | Exception Hierarchy | 3 | ✓ Complete | ~30min |
| F1.5 | Output Module | 3 | ✓ Complete | ~15min |
| F1.6 | Core Utilities | 3 | ✓ Complete | ~10min |

**Total:** 22 SP
**Completed:** 22 SP (100%)
**Velocity:** ~12 SP/hour (based on F1.1-F1.6 data)

---

## In Scope

**MUST:**
- Working `raise` CLI command with help/version
- Configuration cascade (CLI → env → file → defaults)
- Exception hierarchy with proper exit codes
- Output formatters (human, json, table)
- Rich console for human output
- Core utilities: subprocess wrappers (git, ast-grep, ripgrep)
- Type safety: all code type-annotated
- Tests: >90% coverage on new code
- Quality: passes ruff, pyright, bandit

**SHOULD:**
- Global options (-v, -q, --format) working
- XDG directory compliance
- Good error messages with hints

---

## Out of Scope (defer to E2+)

- Kata engine implementation → E2
- Gate engine implementation → E3
- SAR analysis → E5
- Context generation → E4
- Metrics/observability → E6
- Agent Skill packaging → E7
- Interactive mode → F2.6 (post-MVP)
- Shell completions → F7.3 (post-MVP)

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] **Docstrings on all public APIs** (Google-style)
- [ ] **Component catalog updated** (`dev/components.md`)
- [ ] **ADR created if architectural decision** (`dev/decisions/`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [x] All 6 features complete (F1.1-F1.6)
- [x] `raise --version` and `raise --help` work
- [x] All tests pass (214 tests, 95% coverage)
- [x] **Architecture guide updated** (`dev/architecture-overview.md`)
- [ ] README updated with installation instructions (deferred: pre-release, no PyPI yet)
- [ ] Epic merged to v2

---

## Dependencies

F1.1 → F1.2 → F1.3 → F1.4 → F1.5 (linear dependency chain)
F1.6 can be parallel with F1.5

---

## Notes

- Keep it simple: No over-engineering
- YAGNI: Only build what E2/E3 will actually use
- Focus: Get foundation solid so engines can be built on top

---

*Epic tracking - updated per story completion*
