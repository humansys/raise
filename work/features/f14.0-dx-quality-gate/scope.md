# Feature Scope: F14.0 DX Quality Gate

> Pre-distribution cleanup to ensure raise-cli quality before F&F release.

**Epic:** E14 Rai Distribution
**Branch:** `feature/e14/f14.0-dx-quality-gate`
**Priority:** HIGH (blocks clean F&F distribution)

---

## In Scope

### Critical Fixes (Must)
- [ ] Fix `raise init` output to clarify CLI vs Claude Code skills gap
- [ ] Add post-init guidance (what to do next)
- [ ] Resolve MemoryGraph deprecation (complete migration or remove warnings)

### Code Quality (Should)
- [ ] Extract duplicated ID sanitization to shared utility
- [ ] Extract duplicated graph methods to base class/mixin
- [ ] Extract duplicated XDG path helpers to parameterized function
- [ ] Delete duplicate `/epic-close/skill.md` (old version)

### Guardrails Update (Should)
- [ ] Add stack best practices section from research:
  - Pydantic v2 patterns
  - Typer CLI patterns
  - Security checklist
  - DRY/SOLID guidelines for Python
- [ ] Add Jidoka checkpoint referencing new guardrails

### Quick Wins (Should)
- [ ] Standardize session skill headers ("When to Use" → "Purpose")
- [ ] Fix command naming: `raise memory dump` → `raise memory list`

---

## Out of Scope

### Deferred to Post-F&F
- Skill bloat refactoring (epic-plan 736 lines → <400)
- Split `raise context query` into two commands
- Schema consolidation (governance/query vs context/query)
- Telemetry boilerplate extraction from skills
- Convention schema flattening (8 models → 3)

### Deferred to V3
- Full codebase security audit
- Performance optimization
- Property-based testing adoption

---

## Done Criteria

- [ ] `raise init` output clearly distinguishes CLI commands from Claude Code skills
- [ ] No deprecated code warnings in normal usage paths
- [ ] Zero duplicated utility functions (sanitizers, paths, graph methods)
- [ ] `guardrails.md` updated with stack best practices section
- [ ] All tests pass (>90% coverage maintained)
- [ ] Quality checks pass (ruff, pyright, bandit)
- [ ] Retrospective complete

---

## Research Foundation

| Topic | Location | Key Takeaways |
|-------|----------|---------------|
| Pydantic v2 | `work/research/pydantic-v2-best-practices/` | BaseModel at boundaries, TypeAdapter singleton |
| Typer CLI | `work/research/typer-cli-best-practices/` | Flags over positional, multi-format output |
| Python Structure | `work/research/python-project-structure-2025/` | src layout validated, minimal __init__.py |
| Pytest | `work/research/pytest-best-practices/` | AAA pattern, factory fixtures |
| Security | `work/research/python-security/` | Input validation, subprocess shell=False |
| DRY/SOLID | `work/research/dry-solid-python/` | Rule of three, composition over inheritance |

---

## Related Issues

- ISSUE-003: Directory Structure Ontology
- ISSUE-004: Epic/Feature Tree Structure
- ISSUE-005: DX Audit Findings (primary driver)

---

*Created: 2026-02-05*
